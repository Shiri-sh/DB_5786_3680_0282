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

tables_pks = [
    ('labs.diagnostic_equipment', 'equipment_id'),
    ('labs.lab_test', 'test_id'),
    ('labs.lab_order', 'lab_order_id'),
    ('labs.lab_technician', 'technician_id'),
    ('labs.lab_order_test', 'lab_order_test_id'),
    ('labs.lab_result', 'result_id'),
]

print("Syncing sequences in database...")
for table, pk in tables_pks:
    try:
        # Get sequence name
        seq_query = f"SELECT pg_get_serial_sequence('{table}', '{pk}');"
        cur.execute(seq_query)
        seq_name = cur.fetchone()[0]
        if seq_name:
            # Sync sequence to MAX(pk) + 1 (or MAX(pk) depending on setval behaviour)
            # setval(seq, val, true) means next nextval will return val+1.
            # So if we set it to MAX(pk), nextval will return MAX(pk)+1, which is perfect.
            sync_query = f"SELECT setval('{seq_name}', COALESCE(MAX({pk}), 1)) FROM {table};"
            cur.execute(sync_query)
            new_val = cur.fetchone()[0]
            print(f"  Synced {table} ({pk}) sequence to: {new_val}")
        else:
            print(f"  No sequence found for {table} ({pk})")
    except Exception as e:
        print(f"  Error syncing {table}: {e}")
        conn.rollback()
        continue

conn.commit()
cur.close()
conn.close()
print("Done!")
