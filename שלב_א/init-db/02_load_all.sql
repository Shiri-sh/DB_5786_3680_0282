

-- insert base
\i '/docker-entrypoint-initdb.d/02_insert_base/insert_lab_order.sql'
\i '/docker-entrypoint-initdb.d/02_insert_base/insert_lab_technician.sql'
\i '/docker-entrypoint-initdb.d/02_insert_base/insert_lab_test.sql'

-- load equipment
\i '/docker-entrypoint-initdb.d/03_DataImportFiles/load_equipment.sql'

-- relations
\i '/docker-entrypoint-initdb.d/04_insert_relations/insert_order_tests.sql'

-- results
\i '/docker-entrypoint-initdb.d/05_insert_result/insert_results.sql'