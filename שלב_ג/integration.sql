-- =====================================================================
-- STEP 1: Setup the Foreign Data Wrapper (FDW)
-- =====================================================================

-- Enable the extension to allow cross-database communication
CREATE EXTENSION IF NOT EXISTS postgres_fdw;

-- Create the foreign server object (Updated with correct dbname)
CREATE SERVER staff_mgmt_server
FOREIGN DATA WRAPPER postgres_fdw
OPTIONS (host 'localhost', dbname 'Hospital', port '5432');

-- Map your local user to the remote server credentials
CREATE USER MAPPING FOR current_user
SERVER staff_mgmt_server
OPTIONS (user 'MyUser', password 'pass123');

-- =====================================================================
-- STEP 2: Create Foreign Tables (Linking to the STAFF schema)
-- =====================================================================

CREATE FOREIGN TABLE staff_remote (
    staffid INTEGER,
    firstname VARCHAR(50),
    lastname VARCHAR(50),
    phone VARCHAR(20),
    email VARCHAR(100),
    status VARCHAR(20)
) SERVER staff_mgmt_server
OPTIONS (schema_name 'public', table_name 'staff');

-- =====================================================================
-- STEP 3: Database Integration Documentation
-- =====================================================================

COMMENT ON COLUMN labs.lab_order.doctor_id IS 'References StaffID from the remote Staff Management system';

-- =====================================================================
-- STEP 4: Creating Views (Requirement 7)
-- =====================================================================

-- VIEW 1: Lab Test & Equipment Status (Labs perspective)
CREATE OR REPLACE VIEW labs.view_test_equipment_status AS
SELECT 
    t.test_name,
    t.sample_type,
    e.equipment_name,
    e.maintenance_date
FROM labs.lab_test t
JOIN labs.diagnostic_equipment e ON t.equipment_id = e.equipment_id;

-- VIEW 2: Remote Staff Directory (Remote perspective)
CREATE OR REPLACE VIEW labs.view_remote_staff_directory AS
SELECT 
    firstname || ' ' || lastname AS full_name,
    email,
    status
FROM staff_remote
WHERE status = 'Active';

-- VIEW 3: Integrated Lab Orders with Doctors (Integration perspective)
CREATE OR REPLACE VIEW labs.view_lab_orders_with_doctors AS
SELECT 
    o.lab_order_id,
    o.order_date,
    o.status AS order_status,
    s.firstname || ' ' || s.lastname AS doctor_name,
    s.phone AS doctor_phone
FROM labs.lab_order o
JOIN staff_remote s ON o.doctor_id = s.staffid;

-- =====================================================================
-- STEP 5: Sample Queries on Views (Requirement 8)
-- =====================================================================

-- Queries for View 1 (Equipment Status)
-- 1. Find tests using equipment needing maintenance
SELECT test_name, equipment_name FROM labs.view_test_equipment_status WHERE maintenance_date < '2026-04-01';
-- 2. Count tests per equipment
SELECT equipment_name, COUNT(test_name) FROM labs.view_test_equipment_status GROUP BY equipment_name;

-- Queries for View 2 (Remote Staff)
-- 1. Find contact for a specific doctor
SELECT email FROM labs.view_remote_staff_directory WHERE full_name LIKE 'Guy%';
-- 2. List all active remote staff
SELECT * FROM labs.view_remote_staff_directory;

-- Queries for View 3 (Integrated Results)
-- 1. Show urgent pending orders and their doctors
SELECT lab_order_id, doctor_name, doctor_phone FROM labs.view_lab_orders_with_doctors WHERE order_status = 'ORDERED';
-- 2. Total orders summary per doctor
SELECT doctor_name, COUNT(lab_order_id) as total_orders FROM labs.view_lab_orders_with_doctors GROUP BY doctor_name;
