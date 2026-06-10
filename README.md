# DB Project - Hospital Management System
**Selected Division**: Laboratory & Diagnostics Division

###  Authors
- Shiri Shachor
- Yael Shushan

---

## Table of Contents
* [Stage 1 — ERD, DSD & Database Creation](./שלב_א/README.MD)
* [Stage 2 — SQL Queries, Updates & Constraints](./שלב_ב/README.md)
* [Stage 3 — Integration & Foreign Data Wrapper (FDW)](./שלב_ג/README.md)
* [Stage 4 — Database Programming (PL/pgSQL)](./שלב_ד/README.md)
* [Stage 5 — Graphical User Interface (GUI)](#stage-5--graphical-user-interface-gui)

---

# Stage 5 – Graphical User Interface (GUI)

This section describes the graphical user interface (GUI) built for the medical laboratory management system. The interface enables day-to-day work with the database in a friendly, visual way, while activating all the logical and integrative capabilities developed in the previous stages.

---

##  Development Approach and Tools

The user interface was built as a desktop application using **Python** and a structured layered architecture that separates business logic, database connectivity, and the presentation layer:

1. **CustomTkinter (UI Design):**
   We chose to use the `customtkinter` library (a modern extension of Python's built-in `tkinter` library). The library provides beautiful visual components (rounded buttons, modern forms, navigation-based side menus) and natively supports quick switching between **Dark Mode** and **Light Mode**.

2. **Psycopg2-binary & Connection Pooling (Database Management):**
   The connection to PostgreSQL is managed via a **Connection Pool** using `psycopg2`'s `ThreadedConnectionPool`. This approach avoids repeatedly opening and closing connections on every operation, improves performance, and supports multi-threading.

3. **Integration with Stage 4 Functions and Procedures:**
   The interface is deeply integrated with the database's internal logic:
   * **Procedures:** The system calls `pr_update_all_order_prices` (update all order prices) and `pr_promote_technicians` (promote technicians with bonuses) directly, and retrieves the messages (`RAISE NOTICE`) generated in the database to display them to the user in a detailed dialog.
   * **Functions and Integration:** The analytics screen uses the `fn_get_doctor_workload` function to fetch doctors' workloads, while the doctor list itself is pulled in real time from the external Staff integration table (`staff_remote`) established in Stage 3.

4. **Smart Error Protection Mechanism (Constraint & Trigger Interception):**
   In the event of a database constraint violation (for example, attempting to update an order that has already been completed, which is blocked by the `trg_status_protection` trigger), the application captures the exact error message from the server and displays it to the user in a friendly, styled dialog box, instead of crashing.

---

##  System Login and Startup Instructions

The full code and files for the interface are organized in the submission folder [DBProject_5786_3680_0282/שלב ה](./DBProject_5786_3680_0282/שלב%20ה/).

### Quick Start Steps:
1. **Start the database:** Make sure your Postgres Docker container is running (`docker compose up -d db`).
2. **Navigate to the Stage 5 folder:**
   ```bash
   cd "DBProject_5786_3680_0282/שלב ה"
   ```
3. **Create and activate a virtual environment:**
   ```bash
   python -m venv .venv
   # Activation on Windows (PowerShell):
   .venv\Scripts\Activate.ps1
   ```
4. **Install the required libraries:**
   ```bash
   pip install -r requirements.txt
   ```
5. **Configure the `.env` file:** Copy `.env.example` to `.env` and update the server connection details (local server: `localhost`, user: `MyUser`, password: `pass1234`, database: `Hospital`).
6. **Run the application:**
   ```bash
   python main.py
   ```

---

##  Comprehensive System Screenshot Gallery

Below are screenshots demonstrating the various screens, display modes (light mode and dark mode), and database operations in action:

###  Light Mode Interface

#### 1. Main Dashboard - Light Mode
The dashboard displaying connection details and the current database version.
![Dashboard - Light Mode](./DBProject_5786_3680_0282/שלב%20ה/screenshots/01_light_dashboard.png)

#### 2. Lab Orders Management Module (CRUD Lab Orders) - Light Mode
A form for filling in and managing lab orders, combined with the data table.
![CRUD Orders - Light Mode](./DBProject_5786_3680_0282/שלב%20ה/screenshots/02_light_crud_orders.png)

#### 3. Lab Technicians Management Module (CRUD Lab Technicians) - Light Mode
A screen for adding, updating, and deleting lab technicians with smart selection boxes for profession/certification and employee IDs.
![CRUD Technicians - Light Mode](./DBProject_5786_3680_0282/שלב%20ה/screenshots/03_light_crud_technicians.png)

#### 4. Queries and Reports (Analytics & Reports) - Light Mode
The analytics screen displaying the report results for the 5 most popular tests.
![Analytics - Light Mode](./DBProject_5786_3680_0282/שלב%20ה/screenshots/04_light_analytics.png)

---

###  Dark Mode Interface

#### 5. Main Dashboard - Dark Mode
The dashboard with full dark theme styling.
![Dashboard - Dark Mode](./DBProject_5786_3680_0282/שלב%20ה/screenshots/05_dark_dashboard.png)

#### 6. Lab Orders Management Module (CRUD Lab Orders) - Dark Mode
![CRUD Orders - Dark Mode](./DBProject_5786_3680_0282/שלב%20ה/screenshots/06_dark_crud_orders.png)

#### 7. Lab Technicians Management Module (CRUD Lab Technicians) - Dark Mode
![CRUD Technicians - Dark Mode](./DBProject_5786_3680_0282/שלב%20ה/screenshots/07_dark_crud_technicians.png)

#### 8. Queries and Reports (Analytics & Reports) - Dark Mode
A query tracking urgent orders that have been waiting for more than 48 hours.
![Analytics - Dark Mode](./DBProject_5786_3680_0282/שלב%20ה/screenshots/08_dark_analytics.png)

---
###  Database Operations, Constraints, and Runtime Logs (Interactions & Logs)

#### 9. Constraint Enforcement and Trigger Block (Trigger Database Block)
A screenshot demonstrating error capture from the server when the user attempts to update an order with status `COMPLETED`. The `trg_status_protection` trigger rejected the change, and the database rolled back the transaction. The system displays the error properly in a dedicated dialog without crashing.
![Trigger Status Protection Error](./DBProject_5786_3680_0282/שלב%20ה/screenshots/09_trigger_error_dialog.png)

#### 10. Stored Procedure Execution and Runtime Logs (Stored Procedure Notice Logs)
Running the `pr_promote_technicians` procedure for bonuses. The system retrieves and displays the `RAISE NOTICE` messages passed directly from the server in a special scrollable window (list of employees who received bonuses and the number of tests they performed).
![Stored Procedure Notice Logs](./DBProject_5786_3680_0282/שלב%20ה/screenshots/10_procedure_notice_dialog.png)

---

### Full CRUD Lifecycle Demonstration (Record Management)

Below are screenshots demonstrating step by step the operations for creating, updating, and deleting records in the database (performed on the diagnostic equipment table):

#### 11. Create Record
Filling in the form for new diagnostic equipment ("Automated Spectrometer X") and clicking Create. The system generates a new primary key and displays a confirmation message for a successful addition (ID: 501).
![CRUD Create Success](./DBProject_5786_3680_0282/שלב%20ה/screenshots/11_crud_create_success.png)

#### 12. Update Record
Loading the created record, updating its name to "Automated Spectrometer X2", and clicking Save. The system updates the record and displays a confirmation message for the successful update.
![CRUD Update Success](./DBProject_5786_3680_0282/שלב%20ה/screenshots/12_crud_update_success.png)

#### 13. Delete Record - Confirmation Dialog
Clicking Delete for the record. The system displays a dialog asking the user to confirm the permanent deletion of the record to prevent mistakes.
![CRUD Delete Confirm](./DBProject_5786_3680_0282/שלב%20ה/screenshots/13_crud_delete_confirm.png)

#### 14. Delete Record - Success Confirmation
After the user confirms, the record is permanently deleted and the interface confirms this in a dialog and clears the forms.
![CRUD Delete Success](./DBProject_5786_3680_0282/שלב%20ה/screenshots/14_crud_delete_success.png)

---


