from fastapi import APIRouter
from app.core.db import get_connection
from app.models.config import ConfigItem, ConfigUpdate

router = APIRouter()

@router.get("/", response_model=list[ConfigItem])
def list_config():
    conn = get_connection()
    try:
        rows = conn.execute("SELECT key, value FROM config").fetchall()
        return [ConfigItem(key=r[0], value=r[1] or "") for r in rows]
    finally:
        conn.close()

@router.get("/{key}", response_model=ConfigItem)
def get_config_item(key: str):
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT key, value FROM config WHERE key = ?", [key]
        ).fetchone()
        if not row:
            return ConfigItem(key=key, value="")
        return ConfigItem(key=row[0], value=row[1] or "")
    finally:
        conn.close()

@router.put("/{key}", response_model=ConfigItem)
def upsert_config_item(key: str, payload: ConfigUpdate):
    conn = get_connection()
    try:
        conn.execute(
            """
            INSERT INTO config (key, value)
            VALUES (?, ?)
            ON CONFLICT (key) DO UPDATE SET value = excluded.value, updated_at = now()
            """,
            [key, payload.value],
        )
        return ConfigItem(key=key, value=payload.value)
    finally:
        conn.close()

@router.post("/", response_model=list[ConfigItem])
def bulk_update_config(payload: dict[str, str]):
    conn = get_connection()
    try:
        results = []
        for key, value in payload.items():
            conn.execute(
                """
                INSERT INTO config (key, value)
                VALUES (?, ?)
                ON CONFLICT (key) DO UPDATE SET value = excluded.value, updated_at = now()
                """,
                [key, str(value)],
            )
            results.append(ConfigItem(key=key, value=str(value)))
        return results
    finally:
        conn.close()
