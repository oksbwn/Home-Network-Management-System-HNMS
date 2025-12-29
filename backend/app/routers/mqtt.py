from fastapi import APIRouter, HTTPException
from paho.mqtt import client as mqtt
from typing import Optional
from pydantic import BaseModel
from app.services.mqtt import MQTTManager

router = APIRouter()

class MQTTTestRequest(BaseModel):
    broker: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None

@router.get("/status")
async def get_mqtt_status():
    manager = MQTTManager.get_instance()
    return {
        "status": manager.last_status,
        "error": manager.last_error,
        "reachable": manager.is_reachable
    }

@router.post("/test")
async def test_mqtt_connection(payload: MQTTTestRequest):
    manager = MQTTManager.get_instance()
    
    # Create a temp config dict for testing
    test_config = {
        "broker": payload.broker,
        "port": payload.port,
        "username": payload.username,
        "password": payload.password
    }
    
    success, message = manager.test_connection(test_config)
    
    return {
        "success": success,
        "message": message
    }
