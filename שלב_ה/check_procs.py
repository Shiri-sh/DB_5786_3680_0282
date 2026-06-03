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

# Query procedures
cur.execute("""
    SELECT routine_schema, routine_name, routine_type
    FROM information_schema.routines
    WHERE routine_schema NOT IN ('pg_catalog', 'information_schema')
    ORDER BY routine_schema, routine_name;
""")
rows = cur.fetchall()
print("Procedures & Functions in database:")
for r in rows:
    print(f"Schema: {r[0]} | Name: {r[1]} | Type: {r[2]}")

cur.close()
conn.close()
