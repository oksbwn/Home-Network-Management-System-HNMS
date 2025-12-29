import paho.mqtt.client as mqtt
import json
import logging
import time
from typing import Any, Optional
from app.core.config import get_settings
from app.core.db import get_connection

logger = logging.getLogger(__name__)

# Paho MQTT 2.0 compatibility helper
def get_mqtt_client(client_id: str):
    try:
        # Paho 2.0+
        from paho.mqtt.enums import CallbackAPIVersion
        return mqtt.Client(CallbackAPIVersion.VERSION1, client_id=client_id)
    except (ImportError, TypeError):
        # Paho 1.x
        return mqtt.Client(client_id=client_id)

class MQTTManager:
    _instance: Optional['MQTTManager'] = None
    
    def __init__(self):
        self.last_status = "unknown"
        self.last_error = None
        self.last_test_time = 0
        self.is_reachable = False
        self._load_status()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _load_status(self):
        """Loads the last known status from the database."""
        conn = get_connection()
        try:
            row = conn.execute("SELECT value FROM config WHERE key = 'mqtt_status'").fetchone()
            if row:
                self.last_status = row[0]
                self.is_reachable = (self.last_status == "online")
            
            error_row = conn.execute("SELECT value FROM config WHERE key = 'mqtt_error'").fetchone()
            if error_row:
                self.last_error = error_row[0]
        except Exception as e:
            logger.error(f"Failed to load MQTT status: {e}")
        finally:
            conn.close()

    def _save_status(self, status: str, error: str = None):
        """Saves status to the database and updates internal state."""
        self.last_status = status
        self.last_error = error
        self.is_reachable = (status == "online")
        
        conn = get_connection()
        try:
            conn.execute("INSERT OR REPLACE INTO config (key, value, updated_at) VALUES ('mqtt_status', ?, now())", [status])
            conn.execute("INSERT OR REPLACE INTO config (key, value, updated_at) VALUES ('mqtt_error', ?, now())", [error or ""])
            conn.commit()
        except Exception as e:
            logger.error(f"Failed to save MQTT status: {e}")
        finally:
            conn.close()

    def get_config(self):
        settings = get_settings()
        conn = get_connection()
        try:
            keys = ['mqtt_broker', 'mqtt_port', 'mqtt_base_topic', 'mqtt_username', 'mqtt_password']
            rows = conn.execute("SELECT key, value FROM config WHERE key IN ({})".format(','.join(['?']*len(keys))), keys).fetchall()
            config = {r[0]: r[1] for r in rows}
            
            return {
                'broker': config.get('mqtt_broker') or getattr(settings, 'mqtt_broker', 'localhost'),
                'port': int(config.get('mqtt_port') or getattr(settings, 'mqtt_port', 1883)),
                'base_topic': config.get('mqtt_base_topic') or getattr(settings, 'mqtt_base_topic', 'network_scanner'),
                'username': config.get('mqtt_username') or getattr(settings, 'mqtt_username', None),
                'password': config.get('mqtt_password') or getattr(settings, 'mqtt_password', None)
            }
        finally:
            conn.close()

    def test_connection(self, custom_config: Optional[dict] = None) -> tuple[bool, str]:
        """Tests connection to the broker and updates status."""
        import threading
        config = custom_config or self.get_config()
        client_id = f"hnms_test_{int(time.time())}"
        client = get_mqtt_client(client_id)
        
        logger.info(f"Testing MQTT connection to {config['broker']}:{config['port']}")
        
        if config.get('username'):
            client.username_pw_set(config['username'], config.get('password'))
            
        connect_event = threading.Event()
        result = {"success": False, "error": "Connection timeout"}

        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                result["success"] = True
                result["error"] = None
            else:
                result["success"] = False
                result["error"] = f"Connection failed with code {rc}"
            connect_event.set()

        client.on_connect = on_connect
            
        try:
            client.connect(config['broker'], config['port'], keepalive=5)
            client.loop_start()
            
            # Wait for connection or timeout (2 seconds)
            if connect_event.wait(timeout=2.0):
                if result["success"]:
                    client.disconnect()
                    client.loop_stop()
                    if not custom_config:
                        self._save_status("online")
                    return True, "Connected successfully"
                else:
                    client.loop_stop()
                    if not custom_config:
                        self._save_status("offline", result["error"])
                    return False, result["error"]
            else:
                client.loop_stop()
                if not custom_config:
                    self._save_status("offline", "Connection timeout")
                return False, "Connection timeout"
        except Exception as e:
            if not custom_config:
                self._save_status("offline", str(e))
            return False, str(e)

    def publish(self, topic: str, payload: Any, retain: bool = False):
        if not self.is_reachable:
            logger.debug(f"Skipping MQTT publish to {topic} because broker is offline/unreachable")
            return
            
        config = self.get_config()
        try:
            client_id = f"hnms_pub_{int(time.time())}"
            client = get_mqtt_client(client_id)
            if config['username']:
                client.username_pw_set(config['username'], config['password'])
            
            client.connect(config['broker'], config['port'], 60)
            msg = payload if isinstance(payload, str) else json.dumps(payload)
            client.publish(topic, msg, retain=retain)
            client.disconnect()
        except Exception as e:
            logger.error(f"Failed to publish to {topic}: {e}")
            self._save_status("offline", str(e))

def publish_mqtt(topic: str, payload: Any, retain: bool = False):
    MQTTManager.get_instance().publish(topic, payload, retain=retain)

def publish_ha_discovery(device_info: dict):
    config = MQTTManager.get_instance().get_config()
    mac = device_info.get("mac")
    if not mac: return
    
    unique_id = f"hnms_{mac.replace(':', '').lower()}"
    discovery_topic = f"homeassistant/device_tracker/{unique_id}/config"
    
    discovery_payload = {
        "name": device_info.get("hostname") or f"Device {mac}",
        "unique_id": unique_id,
        "state_topic": f"{config['base_topic']}/devices/{unique_id}/status",
        "payload_home": "online",
        "payload_not_home": "offline",
        "device": {
            "identifiers": [unique_id],
            "name": device_info.get("hostname") or f"Device {mac}",
            "manufacturer": device_info.get("vendor"),
            "model": "Network Device",
            "connections": [["mac", mac]]
        }
    }
    
    publish_mqtt(discovery_topic, discovery_payload, retain=True)

def publish_device_status(device_info: dict, status: str):
    config = MQTTManager.get_instance().get_config()
    mac = device_info.get("mac")
    if not mac:
        return

    key = mac.replace(":", "").lower()
    base_topic = config['base_topic']
    
    state_topic = f"{base_topic}/devices/hnms_{key}/status"
    # Also publish to generic topic for HA compatibility if needed, 
    # but let's stick to the discovery config structure:
    # state_topic: f"{config['base_topic']}/devices/{unique_id}/status"
    
    state_val = "online" if status == "online" else "offline"
    publish_mqtt(state_topic, state_val, retain=True)
    
    # Optional: Publish attributes
    attr_topic = f"{base_topic}/devices/hnms_{key}/attributes"
    publish_mqtt(attr_topic, device_info, retain=True)
    
    if status == "online":
        publish_ha_discovery(device_info)

def publish_device_online(device_info: dict):
    publish_device_status(device_info, "online")

def publish_device_offline(device_info: dict):
    publish_device_status(device_info, "offline")
