import json
import asyncio
import subprocess
import re
import ipaddress
from uuid import uuid4
from datetime import datetime, timezone
from app.core.db import get_connection

# Conditional import of scapy
try:
    from scapy.all import ARP, Ether, srp, conf
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False

async def native_ping(ip: str) -> bool:
    """Uses system ping to check if a host is up."""
    try:
        cmd = ["ping", "-n", "1", "-w", "1000", ip]
        res = await asyncio.to_thread(
            subprocess.run, cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True
        )
        if res.returncode == 0:
            if "Reply from" in res.stdout:
                return True
        return False
    except Exception as e:
        print(f"DEBUG PING ERROR for {ip}: {e}")
        return False

def get_arp_table() -> dict[str, str]:
    """Parses 'arp -a' output into an IP -> MAC mapping."""
    arp_map = {}
    try:
        output = subprocess.check_output(["arp", "-a"], text=True)
        matches = re.findall(r"(\d+\.\d+\.\d+\.\d+)\s+([0-9a-fA-F:-]{17})", output)
        for ip, mac in matches:
            normalized_mac = mac.replace('-', ':').lower()
            arp_map[ip] = normalized_mac
    except Exception as e:
        print(f"DEBUG ERROR: Failed to read ARP table: {e}")
    return arp_map

async def run_scan_job(scan_id: str, target: str, scan_type: str) -> None:
    conn = get_connection()
    try:
        now = datetime.now(timezone.utc)
        print(f"DEBUG: Starting scan {scan_id}. Target: {target}, Type: {scan_type}")
        discovered_devices = []

        # 1. Try Scapy first
        if SCAPY_AVAILABLE and scan_type in ["arp", "ping"]:
            try:
                print(f"DEBUG: Attempting Scapy ARP scan on {target}")
                ans, unans = await asyncio.to_thread(
                    srp, 
                    Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=target), 
                    timeout=2, 
                    verbose=False
                )
                for snd, rcv in ans:
                    discovered_devices.append({
                        "ip": rcv.psrc,
                        "mac": rcv.hwsrc,
                        "hostname": None 
                    })
            except Exception as e:
                print(f"DEBUG: Scapy failed or driver missing: {e}. Falling back to native.")

        # 2. Native Fallback
        if not discovered_devices and scan_type in ["arp", "ping"]:
            print("DEBUG: Using Native Fallback (Ping + ARP Cache)")
            targets_to_ping = []
            for part in target.split():
                try:
                    if '/' in part:
                        net = ipaddress.ip_network(part, strict=False)
                        if net.num_addresses > 2:
                            targets_to_ping.extend([str(ip) for ip in net.hosts()])
                        else:
                            targets_to_ping.extend([str(ip) for ip in net])
                    else:
                        targets_to_ping.append(part)
                except:
                    targets_to_ping.append(part)

            semaphore = asyncio.Semaphore(50)
            async def sem_ping(ip):
                async with semaphore:
                    return await native_ping(ip), ip
            
            ping_results = await asyncio.gather(*(sem_ping(ip) for ip in targets_to_ping))
            up_ips = [ip for is_up, ip in ping_results if is_up]
            arp_table = get_arp_table()
            
            for ip in up_ips:
                discovered_devices.append({
                    "ip": ip,
                    "mac": arp_table.get(ip),
                    "hostname": None
                })

        # 3. Process Results
        unique_devices = {d["ip"]: d for d in discovered_devices}.values()
        print(f"DEBUG: Final unique devices found: {len(unique_devices)}")

        for device in unique_devices:
            ip = device["ip"]
            mac = device["mac"]
            hostname = device["hostname"]
            ports_list = []

            result_id = str(uuid4())
            conn.execute(
                """
                INSERT INTO scan_results
                (id, scan_id, ip, mac, hostname, open_ports, os, first_seen, last_seen)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [result_id, scan_id, ip, mac, hostname, json.dumps(ports_list), None, now, now]
            )

            # upsert device
            from app.services.devices import upsert_device_from_scan
            await upsert_device_from_scan(ip, mac, hostname, ports_list)
            
    except Exception as e:
        print(f"DEBUG ERROR in run_scan_job {scan_id}: {e}")
        # We don't raise here usually to let the worker handle the next job, 
        # but the worker also has a try-except. Actually, raising is better for worker's error logging.
        raise e
    finally:
        conn.close()
