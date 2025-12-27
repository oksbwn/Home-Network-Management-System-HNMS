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
        # We use asyncio.to_thread because asyncio subprocess can be flaky on some Windows setups
        # and we want to see the error if it fails.
        cmd = ["ping", "-n", "1", "-w", "1000", ip]
        res = await asyncio.to_thread(
            subprocess.run, cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True
        )
        if res.returncode == 0:
            # On Windows, ping can return 0 even if "Destination host unreachable" is in output
            # though usually it's only 0 if it gets a reply.
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
        # Regex to find IP (xxx.xxx.xxx.xxx) and MAC (xx-xx-xx-xx-xx-xx)
        # Windows ARP uses hyphens, standard is colons. We'll normalize to colons.
        matches = re.findall(r"(\d+\.\d+\.\d+\.\d+)\s+([0-9a-fA-F:-]{17})", output)
        for ip, mac in matches:
            normalized_mac = mac.replace('-', ':').lower()
            arp_map[ip] = normalized_mac
    except Exception as e:
        print(f"DEBUG ERROR: Failed to read ARP table: {e}")
    return arp_map

async def run_scan_job(scan_id: str, target: str, scan_type: str) -> None:
    conn = get_connection()
    now = datetime.now(timezone.utc)
    
    print(f"DEBUG: Starting scan. Target: {target}, Type: {scan_type}")
    discovered_devices = []

    # 1. Try Scapy first if available
    if SCAPY_AVAILABLE and scan_type in ["arp", "ping"]:
        try:
            print(f"DEBUG: Attempting Scapy ARP scan on {target}")
            # Ensure pcap provider exists (will raise error otherwise on Windows)
            # if we don't have this check, srp usually just returns empty lists with a warning
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

    # 2. Fallback to Native Discovery (Ping + ARP) if Scapy found nothing or failed
    if not discovered_devices and scan_type in ["arp", "ping"]:
        print("DEBUG: Using Native Fallback (Ping + ARP Cache)")
        
        # Expand targets (supports space separated IPs or CIDR)
        targets_to_ping = []
        for part in target.split():
            try:
                if '/' in part:
                    net = ipaddress.ip_network(part, strict=False)
                    # Don't ping network and broadcast if /24 or smaller
                    if net.num_addresses > 2:
                        targets_to_ping.extend([str(ip) for ip in net.hosts()])
                    else:
                        targets_to_ping.extend([str(ip) for ip in net])
                else:
                    targets_to_ping.append(part)
            except:
                targets_to_ping.append(part)

        # Ping everyone in parallel (limited concurrency to avoid overwhelming OS)
        semaphore = asyncio.Semaphore(50)
        async def sem_ping(ip):
            async with semaphore:
                return await native_ping(ip), ip
        
        print(f"DEBUG: Pinging {len(targets_to_ping)} potential hosts...")
        ping_results = await asyncio.gather(*(sem_ping(ip) for ip in targets_to_ping))
        up_ips = [ip for is_up, ip in ping_results if is_up]
        
        print(f"DEBUG: {len(up_ips)} hosts responded to ping. Fetching ARP table.")
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
            [
                result_id,
                scan_id,
                ip,
                mac,
                hostname,
                json.dumps(ports_list) if ports_list else None,
                None,
                now,
                now,
            ],
        )

        # upsert device
        from app.services.devices import upsert_device_from_scan
        await upsert_device_from_scan(ip, mac, hostname, ports_list)
