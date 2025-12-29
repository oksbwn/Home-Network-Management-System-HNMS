import duckdb
from pathlib import Path
from app.core.config import get_settings
import logging

logger = logging.getLogger(__name__)

def get_connection() -> duckdb.DuckDBPyConnection:
    """
    Returns a NEW DuckDB connection. 
    Opening a connection in DuckDB is fast and recommended for thread safety in web apps.
    Callers MUST call .close() when done.
    """
    settings = get_settings()
    db_path = Path(settings.db_path)
    
    # Ensure directory exists
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Open a new connection. 
    # This ensures each thread has its own transaction state.
    conn = duckdb.connect(str(db_path))
    
    
    return conn

def commit(conn: duckdb.DuckDBPyConnection) -> None:
    """Commits the given connection."""
    if conn:
        conn.commit()

def init_db() -> None:
    settings = get_settings()
    print(f"Initializing database at {settings.db_path}...")
    
    conn = get_connection()
    try:
        if settings.db_init_mode == "recreate":
            print("Recreating database tables...")
            conn.execute("""
                DROP TABLE IF EXISTS scan_schedules;
                DROP TABLE IF EXISTS device_ports;
                DROP TABLE IF EXISTS devices;
                DROP TABLE IF EXISTS scan_results;
                DROP TABLE IF EXISTS scans;
                DROP TABLE IF EXISTS config;
            """)

        print(f"Loading schema from {settings.db_schema_path}...")
        schema_sql = Path(settings.db_schema_path).read_text(encoding="utf-8")
        conn.execute(schema_sql)
        
        # Migrations
        migrate_db(conn)
        
        print("Database initialized successfully.")
        conn.commit()
    except Exception as e:
        print(f"ERROR during database initialization: {e}")
        raise e
    finally:
        conn.close()

def migrate_db(conn: duckdb.DuckDBPyConnection) -> None:
    """Adds missing columns to existing tables."""
    # Check if vendor/icon exist in devices
    cols = conn.execute("PRAGMA table_info('devices')").fetchall()
    col_names = [c[1] for c in cols]
    
    if 'vendor' not in col_names:
        print("Migration: Adding 'vendor' column to 'devices'")
        conn.execute("ALTER TABLE devices ADD COLUMN vendor TEXT")
    
    if 'icon' not in col_names:
        print("Migration: Adding 'icon' column to 'devices'")
        conn.execute("ALTER TABLE devices ADD COLUMN icon TEXT")

    if 'open_ports' not in col_names:
        print("Migration: Adding 'open_ports' column to 'devices'")
        conn.execute("ALTER TABLE devices ADD COLUMN open_ports TEXT")

    if 'status' not in col_names:
        print("Migration: Adding 'status' column to 'devices'")
        conn.execute("ALTER TABLE devices ADD COLUMN status TEXT DEFAULT 'unknown'")

    # Ensure device_status_history table exists
    conn.execute("""
        CREATE TABLE IF NOT EXISTS device_status_history (
            id TEXT PRIMARY KEY,
            device_id TEXT NOT NULL,
            status TEXT NOT NULL,
            changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Migration for device_ports UNIQUE constraint
    # DuckDB doesn't allow adding UNIQUE to existing tables.
    # We check if it exists by looking at indexes or trying a dummy insert (or just check table_info if supported)
    # Safer: check if we've already run this migration using a config key or checking schema
    # PRAGMA table_info doesn't show UNIQUE easily, but we can check the table definition
    master = conn.execute("SELECT sql FROM sqlite_master WHERE name = 'device_ports'").fetchone()
    if master and "UNIQUE" not in master[0]:
        print("Migration: Adding UNIQUE constraint to 'device_ports'")
        # Ensure we start fresh
        conn.execute("DROP TABLE IF EXISTS device_ports_new")
        conn.execute("""
            CREATE TABLE device_ports_new (
                device_id  TEXT NOT NULL,
                port       INTEGER NOT NULL,
                protocol   TEXT NOT NULL,
                service    TEXT,
                banner     TEXT,
                last_seen  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(device_id, port, protocol)
            );
        """)
        # De-duplicate: Keep the most recent last_seen and any service/banner
        conn.execute("""
            INSERT INTO device_ports_new (device_id, port, protocol, service, banner, last_seen)
            SELECT device_id, port, protocol, arg_max(service, last_seen), arg_max(banner, last_seen), MAX(last_seen)
            FROM device_ports
            GROUP BY device_id, port, protocol
        """)
        conn.execute("DROP TABLE device_ports")
        conn.execute("ALTER TABLE device_ports_new RENAME TO device_ports")
    
    conn.commit()
