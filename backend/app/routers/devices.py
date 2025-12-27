from fastapi import APIRouter, Query, HTTPException
from app.core.db import get_connection
from app.models.devices import DeviceRead

router = APIRouter()

@router.get("/", response_model=list[DeviceRead])
def list_devices(
    device_type: str | None = Query(default=None),
    online_only: bool = Query(default=False),
):
    conn = get_connection()
    try:
        base_sql = """
            SELECT id, ip, mac, name, display_name, device_type,
                   first_seen, last_seen, vendor, icon, attributes
            FROM devices
        """
        clauses: list[str] = []
        params: list[object] = []
    
        if device_type:
            clauses.append("device_type = ?")
            params.append(device_type)
        
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
                attributes=r[10],
            )
            for r in rows
        ]
    finally:
        conn.close()

@router.get("/{device_id}", response_model=DeviceRead)
def get_device(device_id: str):
    conn = get_connection()
    try:
        row = conn.execute(
            """
            SELECT id, ip, mac, name, display_name, device_type,
                   first_seen, last_seen, vendor, icon, attributes
            FROM devices
            WHERE id = ?
            """,
            [device_id],
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Device not found")
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
            attributes=row[10],
        )
    finally:
        conn.close()

from app.models.devices import DeviceUpdate

@router.put("/{device_id}", response_model=DeviceRead)
def update_device(device_id: str, payload: DeviceUpdate):
    conn = get_connection()
    try:
        # Verify existence
        row = conn.execute("SELECT id FROM devices WHERE id = ?", [device_id]).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Device not found")
            
        # Construct update query dynamically
        updates = []
        params = []
        
        if payload.name is not None:
            updates.append("name = ?")
            params.append(payload.name)
            
        if payload.display_name is not None:
            updates.append("display_name = ?")
            params.append(payload.display_name)
            
        if payload.device_type is not None:
            updates.append("device_type = ?")
            params.append(payload.device_type)

        if payload.vendor is not None:
            updates.append("vendor = ?")
            params.append(payload.vendor)

        if payload.icon is not None:
            updates.append("icon = ?")
            params.append(payload.icon)
            
        if not updates:
            # no-op
            return get_device(device_id)
            
        sql = f"UPDATE devices SET {', '.join(updates)} WHERE id = ?"
        params.append(device_id)
        
        conn.execute(sql, params)
        
        return get_device(device_id)
    finally:
        conn.close()
