import sys
import psycopg2
from config import load_database_config

print("Loading database config...")
config = load_database_config()
print(f"Config loaded: host={config.host}, port={config.port}, dbname={config.name}, user={config.user}")

try:
    print("Attempting to connect to PostgreSQL...")
    conn = psycopg2.connect(
        host=config.host,
        port=config.port,
        dbname=config.name,
        user=config.user,
        password=config.password,
        connect_timeout=3
    )
    print("Connection successful!")
    cur = conn.cursor()
    cur.execute("SELECT version();")
    print(f"PostgreSQL version: {cur.fetchone()[0]}")
    cur.close()
    conn.close()
    print("Connection closed.")
except Exception as e:
    print(f"Error connecting: {e}")
    sys.exit(1)
