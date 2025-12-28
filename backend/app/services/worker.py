import asyncio
from typing import Optional
from datetime import datetime, timedelta, timezone
from app.core.db import get_connection
from app.services.scans import run_scan_job

POLL_INTERVAL_SECONDS = 5

async def scheduler_loop():
    while True:
        try:
            await handle_schedules()
        except Exception as e:
            print(f"DEBUG ERROR in scheduler_loop: {e}")
        await asyncio.sleep(POLL_INTERVAL_SECONDS)

async def scan_runner_loop():
    while True:
        try:
            await handle_queued_scans()
        except Exception as e:
            print(f"DEBUG ERROR in scan_runner_loop: {e}")
        await asyncio.sleep(1)

async def handle_schedules():
    conn = get_connection()
    try:
        now = datetime.now(timezone.utc)
        
        # 1. Fetch Config for Global Discovery
        config_rows = conn.execute("SELECT key, value FROM config WHERE key IN ('scan_subnets', 'scan_interval', 'last_discovery_run_at')").fetchall()
        config = {r[0]: r[1] for r in config_rows}
        
        scan_subnets_raw = config.get('scan_subnets')
        scan_interval = int(config.get('scan_interval', '300'))
        last_run_str = config.get('last_discovery_run_at')
        
        last_run = None
        if last_run_str:
            try:
                last_run = datetime.fromisoformat(last_run_str.replace('Z', '+00:00'))
                if last_run.tzinfo is None:
                    last_run = last_run.replace(tzinfo=timezone.utc)
            except ValueError:
                pass
                
        # Check if global discovery is due
        if scan_subnets_raw and (last_run is None or now >= last_run + timedelta(seconds=scan_interval)):
            import json
            try:
                subnets = json.loads(scan_subnets_raw)
                if isinstance(subnets, list) and subnets:
                    combined_target = " ".join(sorted([s.strip() for s in subnets if s.strip()]))
                    if combined_target:
                        await enqueue_scan(combined_target, "arp")
                        conn.execute(
                            """
                            INSERT INTO config (key, value) VALUES ('last_discovery_run_at', ?)
                            ON CONFLICT (key) DO UPDATE SET value = excluded.value, updated_at = now()
                            """,
                            [now.isoformat()],
                        )
            except json.JSONDecodeError:
                target = scan_subnets_raw.strip()
                if target:
                    await enqueue_scan(target, "arp")
                    conn.execute(
                        """
                        INSERT INTO config (key, value) VALUES ('last_discovery_run_at', ?)
                        ON CONFLICT (key) DO UPDATE SET value = excluded.value, updated_at = now()
                        """,
                        [now.isoformat()],
                    )

        # 2. Handle specific schedules
        rows = conn.execute(
            """
            SELECT id, scan_type, target, interval_seconds
            FROM scan_schedules
            WHERE enabled = TRUE AND (next_run_at IS NULL OR next_run_at <= ?)
            """,
            [now],
        ).fetchall()

        for sched_id, scan_type, target, interval in rows:
            enqueued = await enqueue_scan(target, scan_type)
            if enqueued:
                next_run_at = now + timedelta(seconds=interval)
                conn.execute(
                    "UPDATE scan_schedules SET last_run_at = ?, next_run_at = ? WHERE id = ?",
                    [now, next_run_at, sched_id],
                )
    finally:
        conn.close()

async def enqueue_scan(target: str, scan_type: str) -> Optional[str]:
    from uuid import uuid4
    conn = get_connection()
    try:
        target = target.strip()
        
        # STRICT: check for ANY active scan of discovery type
        # AND: Check for VERY recent scans to prevent double-clicks/scheduler race
        cutoff = datetime.now(timezone.utc) - timedelta(seconds=60)
        active = conn.execute(
            "SELECT id, target, created_at FROM scans WHERE status IN ('queued', 'running') OR created_at > ?",
            [cutoff]
        ).fetchall()
        
        if scan_type in ('arp', 'discovery'):
            for _, act_target, created_at in active:
                if act_target.strip() == target:
                    print(f"DEBUG WORKER: Scan for {target} already active or triggered within last 60s. Skipping.")
                    return None
            if len([s for s in active if s[2] > cutoff]) >= 2:
                print(f"DEBUG WORKER: Too many recent scans triggered. Skipping.")
                return None

        scan_id = str(uuid4())
        now = datetime.now(timezone.utc)
        conn.execute(
            """
            INSERT INTO scans (id, target, scan_type, status, created_at)
            VALUES (?, ?, ?, 'queued', ?)
            """,
            [scan_id, target, scan_type, now],
        )
        return scan_id
    finally:
        conn.close()

async def handle_queued_scans():
    conn = get_connection()
    try:
        # Pick the oldest queued scan
        row = conn.execute(
            """
            SELECT id, target, scan_type
            FROM scans
            WHERE status = 'queued'
            ORDER BY created_at
            LIMIT 1
            """
        ).fetchone()
        
        if not row:
            return

        scan_id, target, scan_type = row
        now = datetime.now(timezone.utc)
        
        # Clean up stale running scans (older than 10 minutes)
        stale_cutoff = datetime.now(timezone.utc) - timedelta(minutes=10)
        conn.execute(
            """
            UPDATE scans SET status='error', finished_at=?, error_message='Stale scan auto-cleared'
            WHERE status='running' AND started_at < ?
            """,
            [datetime.now(timezone.utc), stale_cutoff]
        )
        # Check if something else is already running
        running_count = conn.execute("SELECT COUNT(*) FROM scans WHERE status = 'running'").fetchone()[0]
        if running_count >= 1:
            return

        print(f"DEBUG WORKER: Picking up scan {scan_id}. Setting to 'running'.")
        conn.execute(
            "UPDATE scans SET status='running', started_at=? WHERE id=?", 
            [now, scan_id]
        )

        # Run the actual job
        await run_scan_job(scan_id, target, scan_type)
        
        print(f"DEBUG WORKER: Scan {scan_id} finished. Setting to 'done'.")
        conn.execute(
            "UPDATE scans SET status='done', finished_at=? WHERE id=?",
            [datetime.now(timezone.utc), scan_id],
        )
        
    except Exception as exc:
        print(f"DEBUG WORKER: Scan {scan_id} encountered an error: {exc}")
        try:
            conn.execute(
                "UPDATE scans SET status='error', finished_at=?, error_message=? WHERE id=?",
                [datetime.now(timezone.utc), str(exc), scan_id],
            )
        except Exception as e:
            print(f"DEBUG WORKER: Failed to update error status: {e}")
    finally:
        conn.close()
