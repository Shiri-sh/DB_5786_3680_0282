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

# Query doctor ID for Adi Asher
cur.execute("SELECT staffid FROM public.staff_remote WHERE firstname = 'Adi' AND lastname = 'Aser';")
row = cur.fetchone()
print(f"Adi Aser staffid: {row[0] if row else 'Not found'}")

# Query doctor ID for Adi Asher (or other spelling)
cur.execute("SELECT staffid, firstname, lastname FROM public.staff_remote WHERE firstname LIKE 'Adi%' OR lastname LIKE 'Asher%';")
print("Doctors matching 'Adi' or 'Asher':")
for r in cur.fetchall():
    print(f"  ID: {r[0]} | {r[1]} {r[2]}")

# Query all orders for Adi Asher's ID (let's find ID for Adi Asher)
cur.execute("SELECT staffid, firstname, lastname FROM public.staff_remote WHERE (firstname = 'Adi' AND lastname = 'Asher') OR (firstname = 'Adi' AND lastname = 'Asher');")
res = cur.fetchone()
if res:
    doc_id = res[0]
    print(f"Found Adi Asher with ID: {doc_id}")
    cur.execute(f"SELECT lab_order_id, priority, status FROM labs.lab_order WHERE doctor_id = {doc_id};")
    orders = cur.fetchall()
    print(f"Orders for Adi Asher (ID: {doc_id}):")
    for o in orders:
        print(f"  Order ID: {o[0]} | Priority: {o[1]} | Status: {o[2]}")
else:
    print("Adi Asher not found in staff_remote")

cur.close()
conn.close()
