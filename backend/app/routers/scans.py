from fastapi import APIRouter, HTTPException
from app.core.db import get_connection
from app.models.scans import ScanCreate, ScanRead, ScanResultRead
from datetime import datetime, timezone
import json, uuid

router = APIRouter()

@router.get("/gist/")
@router.get("/gist")
def get_scan_gist():
    conn = get_connection()
    try:
        # Get the latest finished scan
        row = conn.execute(
            """
            SELECT id, started_at, finished_at, target
            FROM scans
            WHERE status = 'done'
            ORDER BY finished_at DESC
            LIMIT 1
            """
        ).fetchone()
        
        if not row:
            return {"has_scan": False}
        
        scan_id, started_at, finished_at, target = row
        
        # Count results for this scan
        count_row = conn.execute(
            "SELECT COUNT(*) FROM scan_results WHERE scan_id = ?", [scan_id]
        ).fetchone()
        device_count = count_row[0] if count_row else 0
        
        duration = None
        if started_at and finished_at:
            # DuckDB might return strings or datetime objects depending on driver/setup
            # Let's assume they are handled or we can calculate difference
            # For simplicity, we can just return the raw values or try basic diff
            try:
                if isinstance(started_at, str):
                    started_at = datetime.fromisoformat(started_at.replace('Z', '+00:00'))
                if isinstance(finished_at, str):
                    finished_at = datetime.fromisoformat(finished_at.replace('Z', '+00:00'))
                
                # Ensure both are aware for duration calculation
                if started_at and started_at.tzinfo is None:
                    started_at = started_at.replace(tzinfo=timezone.utc)
                if finished_at and finished_at.tzinfo is None:
                    finished_at = finished_at.replace(tzinfo=timezone.utc)
                    
                duration = (finished_at - started_at).total_seconds()
            except:
                duration = 0

        return {
            "has_scan": True,
            "scan_id": scan_id,
            "finished_at": finished_at,
            "target": target,
            "device_count": device_count,
            "duration_seconds": duration
        }
    finally:
        conn.close()


@router.post("/discovery")
async def trigger_discovery():
    conn = get_connection()
    try:
        # Fetch configured subnets
        row = conn.execute("SELECT value FROM config WHERE key = 'scan_subnets'").fetchone()
        
        target = None
        if row and row[0]:
            try:
                import json
                subnets = json.loads(row[0])
                if isinstance(subnets, list) and subnets:
                    target = " ".join(subnets)
            except:
                target = row[0]
                
        if not target:
            # Fallback to scan_target or default settings
            target_row = conn.execute("SELECT value FROM config WHERE key = 'scan_target'").fetchone()
            target = target_row[0] if target_row else None
            
        if not target:
            from app.core.config import get_settings
            target = get_settings().default_subnet

        from app.services.worker import enqueue_scan
        scan_id = await enqueue_scan(target, "arp")
        
        if not scan_id:
            return {"status": "already_active", "message": "A scan is already in progress for this target.", "target": target}
            
        return {"status": "enqueued", "scan_id": scan_id, "target": target}
    finally:
        conn.close()


@router.post("/", response_model=ScanRead)
def create_scan(payload: ScanCreate):
    conn = get_connection()
    try:
        scan_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        options_json = json.dumps(payload.options) if payload.options else None
        conn.execute(
            """
            INSERT INTO scans (id, target, scan_type, options, status, created_at)
            VALUES (?, ?, ?, ?, 'queued', ?)
            """,
            [scan_id, payload.target, payload.scan_type, options_json, now],
        )
        return ScanRead(
            id=scan_id,
            target=payload.target,
            scan_type=payload.scan_type,
            options=payload.options,
            status="queued",
            created_at=now,
            started_at=None,
            finished_at=None,
            error_message=None,
        )
    finally:
        conn.close()

@router.get("/")
def list_scans():
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT id, target, scan_type, options, status,
                   created_at, started_at, finished_at, error_message
            FROM scans ORDER BY created_at DESC
            """
        ).fetchall()
        print(f"DEBUG SCANS: Fetched {len(rows)} rows from database.")
    except Exception as e:
        print(f"DEBUG ERROR: Failed to fetch scans from DB: {e}")
        return []
    finally:
        conn.close()

    result = []
    # ... previous logic ... (rest of the function remains similar but within result list construction)
    # I will replace the whole block for clarity
    for r in rows:
        try:
            options = json.loads(r[3]) if (len(r) > 3 and r[3]) else None
            
            def ensure_aware(dt):
                if dt and isinstance(dt, datetime) and dt.tzinfo is None:
                    return dt.replace(tzinfo=timezone.utc)
                if isinstance(dt, str):
                    try:
                        parsed = datetime.fromisoformat(dt.replace('Z', '+00:00'))
                        if parsed.tzinfo is None:
                            return parsed.replace(tzinfo=timezone.utc)
                        return parsed
                    except:
                        return None
                return dt

            item = {
                "id": r[0],
                "target": r[1],
                "scan_type": r[2],
                "options": options,
                "status": r[4],
                "created_at": ensure_aware(r[5]) or datetime.now(timezone.utc),
                "started_at": ensure_aware(r[6]),
                "finished_at": ensure_aware(r[7]),
                "error_message": r[8],
            }
            try:
                ScanRead(**item)
                result.append(item)
            except Exception as val_err:
                print(f"DEBUG VALIDATION ERROR for scan {r[0]}: {val_err}")
                result.append(item)
        except Exception as e:
            print(f"DEBUG ERROR: Failed to process scan row {r[0]}: {e}")
            continue
            
    return result

@router.delete("/queue")
def clear_scan_queue():
    """Deletes all scans with status 'queued'"""
    conn = get_connection()
    try:
        conn.execute("DELETE FROM scans WHERE status = 'queued'")
        return {"status": "success", "message": "Queued scans cleared"}
    finally:
        conn.close()

@router.delete("/")
def clear_all_history():
    """Deletes all scan history and results"""
    conn = get_connection()
    try:
        conn.execute("DELETE FROM scan_results")
        conn.execute("DELETE FROM scans")
        return {"status": "success", "message": "All scan history cleared"}
    finally:
        conn.close()

@router.get("/{scan_id}", response_model=ScanRead)
def get_scan(scan_id: str):
    conn = get_connection()
    try:
        row = conn.execute(
            """
            SELECT id, target, scan_type, options, status,
                   created_at, started_at, finished_at, error_message
            FROM scans WHERE id = ?
            """,
            [scan_id],
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Scan not found")
        options = json.loads(row[3]) if row[3] else None
        return ScanRead(
            id=row[0],
            target=row[1],
            scan_type=row[2],
            options=options,
            status=row[4],
            created_at=row[5],
            started_at=row[6],
            finished_at=row[7],
            error_message=row[8],
        )
    finally:
        conn.close()

@router.get("/{scan_id}/results", response_model=list[ScanResultRead])
def get_scan_results(scan_id: str):
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT id, scan_id, ip, mac, hostname, open_ports, os, first_seen, last_seen
            FROM scan_results
            WHERE scan_id = ?
            ORDER BY ip
            """,
            [scan_id],
        ).fetchall()
        result: list[ScanResultRead] = []
        for r in rows:
            open_ports = json.loads(r[5]) if r[5] else None
            result.append(
                ScanResultRead(
                    id=r[0],
                    scan_id=r[1],
                    ip=r[2],
                    mac=r[3],
                    hostname=r[4],
                    open_ports=open_ports,
                    os=r[6],
                    first_seen=r[7],
                    last_seen=r[8],
                )
            )
        return result
    finally:
        conn.close()
