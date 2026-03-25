### Stage 1
* Introduction
* System Screens
* ERD Diagram
* DSD Diagram
* Design Decisions
* Data Insertion Methods
  -- SQL INSERT Statements Mackoroo
  CSV Imports,
  Python Scripts --
* Backup and Restore
---

## Introduction

This project focuses on designing and implementing a database for the Laboratory & Diagnostics Division within a hospital management system.

The system is responsible for managing laboratory tests, including test definitions, lab orders created by doctors, test execution, and result recording. It also manages laboratory technicians and diagnostic equipment

The goal of this system is to ensure efficient tracking of laboratory processes and accurate storage of diagnostic data.

---
## System Screens-![linkToTheSite](https://aistudio.google.com/apps/88bbcf57-d648-4756-ba67-b17949258251?showPreview=true&showAssistant=true)
![dashboard](../images/stage1/labflow_screenshots/dashboard.png)
![LabTests](../images/stage1/labflow_screenshots/LabTests.png)
![labOrders](../images/stage1/labflow_screenshots/labOrders.png)
![results](../images/stage1/labflow_screenshots/results.png)
![technicians](../images/stage1/labflow_screenshots/technicians.png)
![equipment](../images/stage1/labflow_screenshots/equipment.png)

---
## ERD Diagram
![ERD](../images/stage1/ERD.png)

---
## DSD Diagram
![DSD](../images/stage1/DSD.png)

---
## Design Decisions

Several design decisions were made to ensure a realistic and efficient database structure:

* A separate table (Lab_Order_Test) was created to resolve the many-to-many relationship between lab orders and lab tests.
* The Lab_Result table stores the outcome of each test and is linked to both the test execution and the technician who performed it.
* Additional attributes such as status and priority were added to Lab_Order to reflect real-world hospital workflows.
* The system uses CHECK constraints to enforce valid values for fields such as order status and priority.
* Equipment is linked to lab tests to represent the dependency between tests and diagnostic tools.

These decisions improve data integrity, normalization, and alignment with real-world scenarios.

---
## Data Insertion Methods
### SQL INSERT statements - Mackoroo
![LAB_ORDER_INSERT](../images/stage1/LAB_ORDER_INSERT.png)
![LAB_TECHNICIAN_INSERT](../images/stage1/LAB_TECHNICIAN_INSERT.png)
![lab_order](../images/stage1/lab_order.png)


### CSV Imports
![CSV](../images/stage1/CSV.png)
![diagnostic_equipment](../images/stage1/diagnostic_equipment.png)
![import_csv](../images/stage1/import_csv.png)

### Python Scripts
![python](../images/stage1/python.png)
![insert_result](../images/stage1/insert_result.png)

---
##Backup and Restore
### Backup
### Restore

