from fastapi import APIRouter, Query, HTTPException
from typing import List, Annotated
from app.core.db import get_connection
from app.models.devices import DeviceRead, DeviceUpdate
from app.services.devices import update_device_fields
import json

router = APIRouter()

def _internal_list_devices(device_type: str | None = None, online_only: bool = False):
    conn = get_connection()
    try:
        base_sql = """
            SELECT id, ip, mac, name, display_name, device_type,
                   first_seen, last_seen, vendor, icon, open_ports, status, attributes
            FROM devices
        """
        clauses: list[str] = []
        params: list[object] = []
    
        if device_type:
            clauses.append("device_type = ?")
            params.append(device_type)

        if online_only:
            clauses.append("status = 'online'")
        
        if clauses:
            base_sql += " WHERE " + " AND ".join(clauses)
        base_sql += " ORDER BY ip"
    
        rows = conn.execute(base_sql, params).fetchall()
        return [
            DeviceRead(
                id=r[0],
                ip=r[1],
                mac=r[2],
                name=r[3],
                display_name=r[4],
                device_type=r[5],
                first_seen=r[6],
                last_seen=r[7],
                vendor=r[8],
                icon=r[9],
                open_ports=json.loads(r[10]) if r[10] else [],
                status=r[11],
                attributes=json.loads(r[12]) if r[12] else {},
            )
            for r in rows
        ]
    finally:
        conn.close()

@router.get("/", response_model=list[DeviceRead])
def list_devices(
    device_type: Annotated[str | None, Query()] = None,
    online_only: Annotated[bool, Query()] = False,
):
    return _internal_list_devices(device_type=device_type, online_only=online_only)

@router.get("/{device_id}", response_model=DeviceRead)
def get_device(device_id: str):
    conn = get_connection()
    try:
        row = conn.execute(
            """
            SELECT id, ip, mac, name, display_name, device_type,
                   first_seen, last_seen, vendor, icon, open_ports, status, attributes
            FROM devices
            WHERE id = ?
            """,
            [device_id],
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Device not found")
            
        # Fetch detailed ports
        ports_rows = conn.execute(
            "SELECT port, service, protocol FROM device_ports WHERE device_id = ? ORDER BY port",
            [device_id]
        ).fetchall()
        
        detailed_ports = []
        if ports_rows:
            detailed_ports = [
                {"port": r[0], "service": r[1], "protocol": r[2]}
                for r in ports_rows
            ]
        else:
            # Fallback to cached simple list if no detailed scan data
            detailed_ports = json.loads(row[10]) if row[10] else []

        return DeviceRead(
            id=row[0],
            ip=row[1],
            mac=row[2],
            name=row[3],
            display_name=row[4],
            device_type=row[5],
            first_seen=row[6],
            last_seen=row[7],
            vendor=row[8],
            icon=row[9],
            open_ports=detailed_ports,
            status=row[11],
            attributes=json.loads(row[12]) if row[12] else {},
        )
    finally:
        conn.close()

@router.patch("/{device_id}", response_model=DeviceRead)
def update_device(device_id: str, update_data: DeviceUpdate):
    """
    Updates a device's display name, type, or icon.
    """
    # Filter out None values to only update what was sent
    fields = {k: v for k, v in update_data.model_dump().items() if v is not None}
    
    if not fields:
        raise HTTPException(status_code=400, detail="No fields provided for update")
        
    updated_device = update_device_fields(device_id, fields)
    
    if not updated_device:
        raise HTTPException(status_code=404, detail="Device not found")
        
    return updated_device

@router.get("/export/json")
def export_devices():
    """Returns all devices for backup purposes."""
    return _internal_list_devices()

@router.post("/import/json")
def import_devices(devices_data: List[DeviceRead]):
    """Imports/Restores devices from a list. Uses INSERT OR REPLACE."""
    conn = get_connection()
    try:
        count = 0
        for d in devices_data:
            conn.execute(
                """
                INSERT OR REPLACE INTO devices 
                (id, ip, mac, name, display_name, device_type, first_seen, last_seen, vendor, icon, status, open_ports, attributes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    d.id, d.ip, d.mac, d.name, d.display_name, d.device_type,
                    d.first_seen, d.last_seen, d.vendor, d.icon, d.status, d.open_ports, d.attributes
                ]
            )
            count += 1
        return {"status": "success", "imported": count}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to import: {str(e)}")
    finally:
        conn.close()

@router.delete("/{device_id}")
def delete_device(device_id: str):
    conn = get_connection()
    try:
        # Verify existence
        row = conn.execute("SELECT id FROM devices WHERE id = ?", [device_id]).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Device not found")
        
        # Manual Cascade
        conn.execute("DELETE FROM device_ports WHERE device_id = ?", [device_id])
        conn.execute("DELETE FROM device_status_history WHERE device_id = ?", [device_id])
        conn.execute("DELETE FROM devices WHERE id = ?", [device_id])
        
        return {"status": "success", "message": f"Device {device_id} deleted"}
    finally:
        conn.close()
