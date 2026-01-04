import duckdb
import os

DB_PATH = "backend/data/dns_logs.duckdb"

def inspect_db():
    if not os.path.exists(DB_PATH):
        print(f"Database file not found at {DB_PATH}")
        return

    try:
        conn = duckdb.connect(DB_PATH)
        
        # Check tables
        tables = conn.execute("SHOW TABLES").fetchall()
        print(f"Tables: {tables}")

        # Count total logs
        total_logs = conn.execute("SELECT COUNT(*) FROM dns_logs").fetchone()[0]
        print(f"Total DNS Logs: {total_logs}")

        # Count domains in dns_domains
        total_domains = conn.execute("SELECT COUNT(*) FROM dns_domains").fetchone()[0]
        print(f"Total Cached Domains: {total_domains}")

        # Check for blocked queries
        # Assuming there is a field indicating status. Let's describe the table first.
        schema = conn.execute("DESCRIBE dns_logs").fetchall()
        print("\nSchema of dns_logs:")
        for col in schema:
            print(col)

        # Check status distribution if 'status' column exists
        status_col_exists = any(col[0] == 'status' for col in schema)
        if status_col_exists:
            print("\nStatus Distribution:")
            dist = conn.execute("SELECT status, COUNT(*) FROM dns_logs GROUP BY status").fetchall()
            for status, count in dist:
                print(f"  {status}: {count}")
        else:
            print("\n'status' column not found in dns_logs")

        # Check dns_domains schema/content related to blocking
        print("\nSchema of dns_domains:")
        schema_domains = conn.execute("DESCRIBE dns_domains").fetchall()
        for col in schema_domains:
            print(col)
            
        is_blocked_exists = any(col[0] == 'is_blocked' for col in schema_domains)
        if is_blocked_exists:
             blocked_domains = conn.execute("SELECT COUNT(*) FROM dns_domains WHERE is_blocked = TRUE").fetchone()[0]
             print(f"\nBlocked Domains in Cache: {blocked_domains}")

        conn.close()

    except Exception as e:
        print(f"Error inspecting DB: {e}")

if __name__ == "__main__":
    inspect_db()
