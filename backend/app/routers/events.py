from fastapi import APIRouter, Query
from typing import List, Annotated
from app.core.db import get_connection
from app.models.events import DeviceEvent, EventStats
from datetime import datetime, timedelta, timezone
import asyncio

router = APIRouter()

@router.get("/", response_model=List[DeviceEvent])
async def list_events(
    limit: int = 100,
    offset: int = 0,
    status: Annotated[str | None, Query()] = None,
    search: Annotated[str | None, Query()] = None
):
    def query():
        conn = get_connection()
        try:
            sql = """
                SELECT h.id, h.device_id, h.status, h.changed_at,
                       d.ip, d.display_name, d.icon, d.device_type
                FROM device_status_history h
                JOIN devices d ON h.device_id = d.id
            """
            clauses = []
            params = []

            if status:
                clauses.append("h.status = ?")
                params.append(status)
            
            if search:
                clauses.append("(d.ip LIKE ? OR d.display_name LIKE ?)")
                params.extend([f"%{search}%", f"%{search}%"])

            if clauses:
                sql += " WHERE " + " AND ".join(clauses)
            
            sql += " ORDER BY h.changed_at DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])

            rows = conn.execute(sql, params).fetchall()
            return [
                DeviceEvent(
                    id=r[0], device_id=r[1], status=r[2], changed_at=r[3],
                    ip=r[4], display_name=r[5], icon=r[6], device_type=r[7]
                )
                for r in rows
            ]
        finally:
            conn.close()
    return await asyncio.to_thread(query)

@router.get("/stats", response_model=List[EventStats])
async def get_event_stats(hours: int = 168):
    def query():
        conn = get_connection()
        try:
            sql = """
                SELECT changed_at as ts, 
                       CASE WHEN status = 'online' THEN 1 ELSE 0 END as on_cnt,
                       CASE WHEN status = 'offline' THEN 1 ELSE 0 END as off_cnt
                FROM device_status_history
                WHERE changed_at > (now() - cast(? || ' hours' AS interval))
                ORDER BY ts ASC
            """
            rows = conn.execute(sql, [hours]).fetchall()
            return [
                EventStats(timestamp=r[0], online_count=r[1], offline_count=r[2])
                for r in rows
            ]
        finally:
            conn.close()
    return await asyncio.to_thread(query)

@router.get("/device/{device_id}", response_model=List[DeviceEvent])
async def get_device_history(device_id: str, limit: int = 50, offset: int = 0):
    def query():
        conn = get_connection()
        try:
            rows = conn.execute(
                """
                SELECT h.id, h.device_id, h.status, h.changed_at,
                       d.ip, d.display_name, d.icon, d.device_type
                FROM device_status_history h
                JOIN devices d ON h.device_id = d.id
                WHERE h.device_id = ?
                ORDER BY h.changed_at DESC
                LIMIT ? OFFSET ?
                """,
                [device_id, limit, offset]
            ).fetchall()
            return [
                DeviceEvent(
                    id=r[0], device_id=r[1], status=r[2], changed_at=r[3],
                    ip=r[4], display_name=r[5], icon=r[6], device_type=r[7]
                )
                for r in rows
            ]
        finally:
            conn.close()
    return await asyncio.to_thread(query)

@router.get("/count")
async def get_events_count(status: str | None = None, search: str | None = None):
    def query():
        conn = get_connection()
        try:
            sql = "SELECT count(*) FROM device_status_history h JOIN devices d ON h.device_id = d.id"
            clauses = []
            params = []
            if status:
                clauses.append("h.status = ?")
                params.append(status)
            if search:
                clauses.append("(d.ip LIKE ? OR d.display_name LIKE ?)")
                params.extend([f"%{search}%", f"%{search}%"])
            if clauses:
                sql += " WHERE " + " AND ".join(clauses)
            
            count = conn.execute(sql, params).fetchone()[0]
            return {"total": count}
        finally:
            conn.close()
    return await asyncio.to_thread(query)

@router.get("/device/{device_id}/count")
async def get_device_events_count(device_id: str):
    def query():
        conn = get_connection()
        try:
            count = conn.execute("SELECT count(*) FROM device_status_history WHERE device_id = ?", [device_id]).fetchone()[0]
            return {"total": count}
        finally:
            conn.close()
    return await asyncio.to_thread(query)

@router.get("/device/{device_id}/fidelity")
async def get_device_fidelity_history(device_id: str, hours: int = 24):
    def query():
        conn = get_connection()
        try:
            # 1. Get device details
            device_row = conn.execute("SELECT mac, ip FROM devices WHERE id = ?", [device_id]).fetchone()
            if not device_row: return []
            mac, ip = device_row

            # 2. Get all successful discovery scans in the window
            scans = conn.execute(
                """
                SELECT id, finished_at 
                FROM scans 
                WHERE status = 'done' 
                  AND scan_type IN ('arp', 'discovery')
                  AND finished_at > now() - interval '1 hour' * ?
                ORDER BY finished_at ASC
                """,
                [hours]
            ).fetchall()

            # 3. For each scan, check if the device was seen
            fidelity_data = []
            for scan_id, finished_at in scans:
                seen = conn.execute(
                    "SELECT count(*) FROM scan_results WHERE scan_id = ? AND (mac = ? OR ip = ?)",
                    [scan_id, mac, ip]
                ).fetchone()[0]
                if finished_at:
                    fidelity_data.append({
                        "timestamp": finished_at,
                        "status": "online" if seen > 0 else "offline"
                    })
            return fidelity_data
        finally:
            conn.close()
    return await asyncio.to_thread(query)
