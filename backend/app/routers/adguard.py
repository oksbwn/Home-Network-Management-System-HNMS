from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
from app.services.adguard import AdguardClient
from app.core.db import get_connection, commit
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class AdguardConfig(BaseModel):
    url: str
    username: Optional[str] = None
    password: Optional[str] = None
    interval: int = 5

@router.get("/config")
def get_config():
    conn = get_connection()
    try:
        row = conn.execute("SELECT config FROM integrations WHERE name = 'adguard'").fetchone()
        if not row:
            return None
        config = json.loads(row[0])
        # Mask password
        if config.get("password"):
            config["password"] = "******"
        
        # Check if actually working
        verified = config.get("verified", False)
        return {**config, "verified": verified}
    finally:
        conn.close()

@router.post("/config")
def save_config(config: AdguardConfig):
    conn = get_connection()
    try:
        # Check if table exists
        conn.execute("CREATE TABLE IF NOT EXISTS integrations (name TEXT PRIMARY KEY, config JSON)")
        
        # Store
        data = config.dict()
        # Verify immediately
        try:
            client = AdguardClient(data["url"], data["username"], data["password"])
            client.test_connection()
            data["verified"] = True
            data["last_check"] = "now" # placeholder, updated in verify
        except Exception as e:
            logger.warning(f"Adguard verification failed during save: {e}")
            data["verified"] = False
            data["error"] = str(e)
            
        conn.execute(
            "INSERT OR REPLACE INTO integrations (name, config) VALUES (?, ?)",
            ['adguard', json.dumps(data)]
        )
        commit(conn)
        return {"status": "saved", "verified": data["verified"]}
    except Exception as e:
        logger.error(f"Failed to save Adguard config: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@router.post("/verify")
def verify_connection(config: AdguardConfig):
    try:
        client = AdguardClient(config.url, config.username, config.password)
        client.test_connection()
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Connection failed: {str(e)}")

@router.post("/sync")
def trigger_sync(background_tasks: BackgroundTasks):
    conn = get_connection()
    try:
        row = conn.execute("SELECT config FROM integrations WHERE name = 'adguard'").fetchone()
        if not row:
            raise HTTPException(status_code=400, detail="Adguard not configured")
        
        conf = json.loads(row[0])
        if not conf.get("url"):
             raise HTTPException(status_code=400, detail="Adguard URL missing")
             
        client = AdguardClient(conf["url"], conf.get("username"), conf.get("password"))
        
        background_tasks.add_task(client.sync)
        return {"status": "queued", "message": "Adguard sync started in background"}
    finally:
        conn.close()
