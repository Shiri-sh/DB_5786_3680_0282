import psycopg2
from config import load_database_config

config = load_database_config()
conn = psycopg2.connect(
    host=config.host,
    port=config.port,
    dbname=config.name,
    user=config.user,
    password=config.password
)
cur = conn.cursor()
for table in ['departments', 'staff', 'staff_remote']:
    try:
        cur.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table}';")
        print(f"Columns for {table}:")
        for r in cur.fetchall():
            print(f"  {r[0]} ({r[1]})")
    except Exception as e:
        print(f"Error querying {table}: {e}")
cur.close()
conn.close()
