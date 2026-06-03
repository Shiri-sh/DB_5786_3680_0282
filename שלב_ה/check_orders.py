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

# Query active urgent orders
cur.execute("""
    SELECT o.lab_order_id, o.doctor_id, o.priority, o.status, d.firstname, d.lastname
    FROM labs.lab_order o
    LEFT JOIN public.staff_remote d ON o.doctor_id = d.staffid
    WHERE o.priority = 'URGENT' AND o.status != 'COMPLETED'
    LIMIT 20;
""")
rows = cur.fetchall()
print("Active urgent orders:")
for r in rows:
    print(f"Order: {r[0]} | Doctor ID: {r[1]} | Priority: {r[2]} | Status: {r[3]} | Doctor Name: {r[4]} {r[5]}")

cur.close()
conn.close()
