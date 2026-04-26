-- =====================================================================
-- STEP 1: Setup the Foreign Data Wrapper (FDW)
-- =====================================================================

-- Enable the extension to allow cross-database communication
CREATE EXTENSION IF NOT EXISTS postgres_fdw;

-- Create the foreign server object
CREATE SERVER staff_mgmt_server
FOREIGN DATA WRAPPER postgres_fdw
OPTIONS (host 'localhost', dbname 'HopitalLocalDB', port '5432');

-- Map your local user to the remote server credentials
-- Use the password you use to login to pgAdmin
CREATE USER MAPPING FOR current_user
SERVER staff_mgmt_server
OPTIONS (user 'MyUser', password 'pass123');

-- =====================================================================
-- STEP 2: Create Foreign Tables (Linking to the STAFF schema)
-- =====================================================================

-- This table represents the 'Staff' table from the other group's database
-- We define only the columns we need for integration
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
-- STEP 3: Database Integration (Local LABS schema)
-- =====================================================================

-- Ensure our local Lab_Order table has a column to link with the Staff ID
-- Based on your ERD, we use doctor_id to reference their StaffID
-- We can add a comment to document this design decision
COMMENT ON COLUMN Lab_Order.doctor_id IS 'References StaffID from the remote Staff Management system';

-- =====================================================================
-- STEP 4: Creating Views for the Report (Requirements 7-8)
-- =====================================================================

-- VIEW 1: Local Perspective (Our Labs data)
CREATE OR REPLACE VIEW view_labs_internal AS
SELECT t.test_name, t.cost, o.order_date, o.status
FROM Lab_Test t
JOIN Lab_Order_Test ot ON t.test_id = ot.test_id
JOIN Lab_Order o ON ot.lab_order_id = o.lab_order_id;

-- VIEW 2: Remote Perspective (The Staff data we received)
CREATE OR REPLACE VIEW view_external_staff_directory AS
SELECT staffid, firstname, lastname, email, status
FROM staff_remote;

-- VIEW 3: Integrated Perspective (The JOIN between both systems)
-- This view connects a lab order to the specific doctor from the Staff DB
CREATE OR REPLACE VIEW view_integrated_lab_results AS
SELECT 
    lo.lab_order_id,
    lo.order_date,
    sr.firstname || ' ' || sr.lastname AS doctor_name,
    sr.email AS doctor_contact,
    lo.status AS order_status
FROM Lab_Order lo
LEFT JOIN staff_remote sr ON lo.doctor_id = sr.staffid;

-- =====================================================================
-- STEP 5: Sample Queries on Views (For README documentation)
-- =====================================================================

-- Query 1: Find all lab orders assigned to a specific doctor from the Staff database
SELECT * FROM view_integrated_lab_results 
WHERE doctor_name IS NOT NULL;

-- Query 2: Summary of lab orders per doctor status
SELECT doctor_name, order_status 
FROM view_integrated_lab_results 
WHERE order_status = 'Completed';