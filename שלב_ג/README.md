# 🔗 Stage 3 – Integration & Views

This stage focuses on the integration between the **Laboratory Department (LABS)** database and the **Staff Management (STAFF)** database—a vital component of the Medical Center’s overall management system. The goal is to build a unified structure that allows a comprehensive view of laboratory activity while associating every test and order with the relevant medical personnel from the external department.

---

## 🗂️ ERD and DSD Diagrams

### Staff Management (STAFF) - External ERD/DSD
![](images/staff_managment_DSD.png)
![](images/staff_managment_ERD.png)


### Integrated ERD
> **TODO:** Insert a diagram showing the logical link between `labs.lab_order` and the remote `staff`.
![](images/Stage3/Integrated_ERD.png)

---

## 🧠 Integration Decisions

*   **Technology:** Integration was implemented using **PostgreSQL's `postgres_fdw`** (Foreign Data Wrapper), enabling real-time cross-database communication without duplicating data.
*   **Schema Isolation:** All local tables remain within the `labs` schema to prevent naming conflicts with the external `public` schema.
*   **Linking Key:** The `doctor_id` column in the `lab_order` table was designated as the integration point, referencing the `staffid` from the remote database.
*   **Data Integrity:** A `LEFT JOIN` strategy was adopted for integrated views to ensure that lab orders are never omitted, even if a doctor's record is missing in the remote system.

---

## 📝 Integration Process and SQL Commands

### 1. Enabling the Wrapper
Enables the extension required for cross-server communication.
```sql
CREATE EXTENSION IF NOT EXISTS postgres_fdw;
```
---
### 2. Foreign Server Definition
Defines the connection to the external Medical Center database.
```sql
CREATE SERVER staff_mgmt_server
FOREIGN DATA WRAPPER postgres_fdw
OPTIONS (host 'localhost', dbname 'Hospital', port '5432');
```
---
3. User Mapping
Maps local credentials to the remote database to allow secure access.

```sql
CREATE USER MAPPING FOR current_user
SERVER staff_mgmt_server
OPTIONS (user 'MyUser', password 'pass123');
```

---
4. Remote Table Linkage
Creates a virtual "Foreign Table" representing the staff from the other department.

```sql
CREATE FOREIGN TABLE staff_remote (
    staffid INTEGER,
    firstname VARCHAR(50),
    lastname VARCHAR(50),
    phone VARCHAR(20),
    email VARCHAR(100),
    status VARCHAR(20)
) SERVER staff_mgmt_server
OPTIONS (schema_name 'public', table_name 'staff');
```
---
## 📊 SQL Views & Analytical Queries

### View 1: Equipment Maintenance Status
Description: A management view linking tests to the specific diagnostic equipment used, including maintenance schedules.

```sql
CREATE OR REPLACE VIEW labs.view_test_equipment_status AS
SELECT t.test_name, t.sample_type, e.equipment_name, e.maintenance_date
FROM labs.lab_test t
JOIN labs.diagnostic_equipment e ON t.equipment_id = e.equipment_id;
```
Data Sample: ``` SELECT * FROM labs.view_test_equipment_status LIMIT 10;```

![](images/v1.png)

#### Queries on View 1:
Query 1.1: Identify tests using equipment that requires maintenance (Before April 2026).

```sql
SELECT test_name, equipment_name 
FROM labs.view_test_equipment_status 
WHERE maintenance_date < '2026-04-01';
```
![](images/q1v1.png)

Query 1.2: Count the number of distinct tests performed by each piece of equipment.

```sql
SELECT equipment_name, COUNT(test_name) AS tests_count
FROM labs.view_test_equipment_status 
GROUP BY equipment_name;
```
![](images/q2v1.png)

### View 2: Remote Staff Directory
Description: Provides an updated directory of "Active" medical staff from the external Staff Management department.

```sql
CREATE OR REPLACE VIEW labs.view_remote_staff_directory AS
SELECT firstname || ' ' || lastname AS full_name, email, status
FROM staff_remote
WHERE status = 'Active';
```
Data Sample: ``` SELECT * FROM labs.view_remote_staff_directory LIMIT 10;```

![](images/v2.png)

#### Queries on View 2:
Query 2.1: Search for a specific doctor's contact information by name.

```sql
SELECT email FROM labs.view_remote_staff_directory 
WHERE full_name LIKE 'Guy%';
```
![](images/q1v2.png)

Query 2.2: Retrieve a full mailing list of all active remote medical personnel.

```sql
SELECT full_name, email FROM labs.view_remote_staff_directory;
```
![](images/q2v2.png)

### View 3: Integrated Lab Orders with Doctors
Description: The primary integration view. It joins local lab orders with the external doctor's identity and contact details.

```sql
CREATE OR REPLACE VIEW labs.view_lab_orders_with_doctors AS
SELECT o.lab_order_id, o.order_date, o.status AS order_status,
       s.firstname || ' ' || s.lastname AS doctor_name, s.phone AS doctor_phone
FROM labs.lab_order o
JOIN staff_remote s ON o.doctor_id = s.staffid;
```
Data Sample: SELECT * FROM labs.view_lab_orders_with_doctors LIMIT 10;

![](images/v3.png)

#### Queries on View 3:
Query 3.1: List all "URGENT" orders currently in "ORDERED" status to facilitate immediate contact with the doctor.

```sql
SELECT lab_order_id, doctor_name, doctor_phone 
FROM labs.view_lab_orders_with_doctors 
WHERE order_status = 'ORDERED';
```
![](images/q1v3.png)

Query 3.2: Summarize the total number of lab orders submitted by each doctor.

```sql
SELECT doctor_name, COUNT(lab_order_id) AS total_orders 
FROM labs.view_lab_orders_with_doctors 
GROUP BY doctor_name;
```
![](images/q2v3.png)

## Summary
#### In this integration phase:

1. Technical Connectivity: A robust connection was established between separate databases using FDW.

2. Logical Bridge: Real-time synchronization allows lab operations to be directly attributed to the correct medical staff.

3. Analytical Tools: Four diverse views and eight queries were developed to provide operational insights from both internal and integrated perspectives.
