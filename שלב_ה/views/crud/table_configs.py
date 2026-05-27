"""Declarative metadata for each laboratory table."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class FieldConfig:
    column: str
    label: str
    field_type: str = "text"  # text, int, float, date, choice, fk, readonly
    choices: list[str] = field(default_factory=list)
    fk_query: str | None = None
    required: bool = True
    readonly_on_create: bool = False


@dataclass
class TableConfig:
    table: str
    title: str
    pk: str
    fields: list[FieldConfig]
    list_sql: str
    fetch_sql: str
    insert_sql: str
    update_sql: str
    delete_sql: str
    lookup_label: str = "Record ID"


def build_table_configs(schema: str) -> dict[str, TableConfig]:
    s = schema
    staff_name = "COALESCE(st.firstname || ' ' || st.lastname, 'Staff #' || t.staff_id::text)"
    doctor_name = "COALESCE(d.firstname || ' ' || d.lastname, 'Doctor #' || o.doctor_id::text)"
    order_label = "o.lab_order_id::text || ' — ' || o.status || ' (' || o.priority || ')'"
    lot_label = (
        "lot.lab_order_test_id::text || ' — Order ' || o.lab_order_id::text"
        " || ' / ' || t.test_name"
    )

    return {
        "diagnostic_equipment": TableConfig(
            table="DIAGNOSTIC_EQUIPMENT",
            title="Diagnostic Equipment",
            pk="equipment_id",
            lookup_label="Equipment ID",
            list_sql=f"""
                SELECT equipment_id, equipment_name, department_id, maintenance_date
                FROM "{s}"."DIAGNOSTIC_EQUIPMENT"
                ORDER BY equipment_id
            """,
            fetch_sql=f"""
                SELECT equipment_id, equipment_name, department_id, maintenance_date
                FROM "{s}"."DIAGNOSTIC_EQUIPMENT" WHERE equipment_id = %s
            """,
            insert_sql=f"""
                INSERT INTO "{s}"."DIAGNOSTIC_EQUIPMENT"
                (equipment_name, department_id, maintenance_date)
                VALUES (%s, %s, %s) RETURNING equipment_id
            """,
            update_sql=f"""
                UPDATE "{s}"."DIAGNOSTIC_EQUIPMENT"
                SET equipment_name = %s, department_id = %s, maintenance_date = %s
                WHERE equipment_id = %s
            """,
            delete_sql=f'DELETE FROM "{s}"."DIAGNOSTIC_EQUIPMENT" WHERE equipment_id = %s',
            fields=[
                FieldConfig("equipment_id", "Equipment ID", "readonly", readonly_on_create=True),
                FieldConfig("equipment_name", "Equipment Name"),
                FieldConfig("department_id", "Department ID", "int"),
                FieldConfig("maintenance_date", "Maintenance Date", "date"),
            ],
        ),
        "lab_test": TableConfig(
            table="LAB_TEST",
            title="Lab Tests",
            pk="test_id",
            lookup_label="Test ID",
            list_sql=f"""
                SELECT t.test_id, t.test_name, t.cost, t.sample_type,
                       COALESCE(e.equipment_name, '—') AS equipment
                FROM "{s}"."LAB_TEST" t
                LEFT JOIN "{s}"."DIAGNOSTIC_EQUIPMENT" e ON t.equipment_id = e.equipment_id
                ORDER BY t.test_id
            """,
            fetch_sql=f"""
                SELECT test_id, test_name, description, normal_range, cost,
                       equipment_id, sample_type
                FROM "{s}"."LAB_TEST" WHERE test_id = %s
            """,
            insert_sql=f"""
                INSERT INTO "{s}"."LAB_TEST"
                (test_name, description, normal_range, cost, equipment_id, sample_type)
                VALUES (%s, %s, %s, %s, %s, %s) RETURNING test_id
            """,
            update_sql=f"""
                UPDATE "{s}"."LAB_TEST"
                SET test_name=%s, description=%s, normal_range=%s, cost=%s,
                    equipment_id=%s, sample_type=%s
                WHERE test_id = %s
            """,
            delete_sql=f'DELETE FROM "{s}"."LAB_TEST" WHERE test_id = %s',
            fields=[
                FieldConfig("test_id", "Test ID", "readonly", readonly_on_create=True),
                FieldConfig("test_name", "Test Name"),
                FieldConfig("description", "Description", required=False),
                FieldConfig("normal_range", "Normal Range", required=False),
                FieldConfig("cost", "Cost", "float"),
                FieldConfig(
                    "equipment_id",
                    "Equipment",
                    "fk",
                    fk_query=f"""
                        SELECT equipment_id, equipment_name
                        FROM "{s}"."DIAGNOSTIC_EQUIPMENT" ORDER BY equipment_name
                    """,
                    required=False,
                ),
                FieldConfig("sample_type", "Sample Type", required=False),
            ],
        ),
        "lab_order": TableConfig(
            table="LAB_ORDER",
            title="Lab Orders",
            pk="lab_order_id",
            lookup_label="Order ID",
            list_sql=f"""
                SELECT o.lab_order_id, o.visit_id, {doctor_name} AS doctor,
                       o.order_date, o.status, o.priority,
                       COALESCE(o.total_price, 0) AS total_price
                FROM "{s}"."LAB_ORDER" o
                LEFT JOIN staff_remote d ON o.doctor_id = d.staffid
                ORDER BY o.lab_order_id DESC
            """,
            fetch_sql=f"""
                SELECT lab_order_id, visit_id, doctor_id, order_date, status, priority,
                       COALESCE(total_price, 0) AS total_price
                FROM "{s}"."LAB_ORDER" WHERE lab_order_id = %s
            """,
            insert_sql=f"""
                INSERT INTO "{s}"."LAB_ORDER"
                (visit_id, doctor_id, order_date, status, priority)
                VALUES (%s, %s, %s, %s, %s) RETURNING lab_order_id
            """,
            update_sql=f"""
                UPDATE "{s}"."LAB_ORDER"
                SET visit_id=%s, doctor_id=%s, order_date=%s, status=%s, priority=%s
                WHERE lab_order_id = %s
            """,
            delete_sql=f'DELETE FROM "{s}"."LAB_ORDER" WHERE lab_order_id = %s',
            fields=[
                FieldConfig("lab_order_id", "Order ID", "readonly", readonly_on_create=True),
                FieldConfig("visit_id", "Visit ID", "int"),
                FieldConfig(
                    "doctor_id",
                    "Doctor",
                    "fk",
                    fk_query="""
                        SELECT staffid, firstname || ' ' || lastname AS full_name
                        FROM staff_remote ORDER BY full_name
                    """,
                ),
                FieldConfig("order_date", "Order Date", "date"),
                FieldConfig(
                    "status",
                    "Status",
                    "choice",
                    choices=["ORDERED", "IN_PROGRESS", "COMPLETED"],
                ),
                FieldConfig(
                    "priority",
                    "Priority",
                    "choice",
                    choices=["NORMAL", "URGENT"],
                ),
                FieldConfig("total_price", "Total Price", "readonly", required=False),
            ],
        ),
        "lab_technician": TableConfig(
            table="LAB_TECHNICIAN",
            title="Lab Technicians",
            pk="technician_id",
            lookup_label="Technician ID",
            list_sql=f"""
                SELECT t.technician_id, {staff_name} AS staff_member,
                       t.certification, COALESCE(t.bonus_points, 0) AS bonus_points
                FROM "{s}"."LAB_TECHNICIAN" t
                LEFT JOIN staff_remote st ON t.staff_id = st.staffid
                ORDER BY t.technician_id
            """,
            fetch_sql=f"""
                SELECT technician_id, staff_id, certification,
                       COALESCE(bonus_points, 0) AS bonus_points
                FROM "{s}"."LAB_TECHNICIAN" WHERE technician_id = %s
            """,
            insert_sql=f"""
                INSERT INTO "{s}"."LAB_TECHNICIAN" (staff_id, certification)
                VALUES (%s, %s) RETURNING technician_id
            """,
            update_sql=f"""
                UPDATE "{s}"."LAB_TECHNICIAN"
                SET staff_id=%s, certification=%s
                WHERE technician_id = %s
            """,
            delete_sql=f'DELETE FROM "{s}"."LAB_TECHNICIAN" WHERE technician_id = %s',
            fields=[
                FieldConfig(
                    "technician_id", "Technician ID", "readonly", readonly_on_create=True
                ),
                FieldConfig(
                    "staff_id",
                    "Staff Member",
                    "fk",
                    fk_query="""
                        SELECT staffid, firstname || ' ' || lastname
                        FROM staff_remote ORDER BY 2
                    """,
                ),
                FieldConfig("certification", "Certification"),
                FieldConfig("bonus_points", "Bonus Points", "readonly", required=False),
            ],
        ),
        "lab_order_test": TableConfig(
            table="LAB_ORDER_TEST",
            title="Order Tests (Line Items)",
            pk="lab_order_test_id",
            lookup_label="Line Item ID",
            list_sql=f"""
                SELECT lot.lab_order_test_id, {order_label} AS lab_order,
                       t.test_name AS test
                FROM "{s}"."LAB_ORDER_TEST" lot
                JOIN "{s}"."LAB_ORDER" o ON lot.lab_order_id = o.lab_order_id
                JOIN "{s}"."LAB_TEST" t ON lot.test_id = t.test_id
                ORDER BY lot.lab_order_test_id
            """,
            fetch_sql=f"""
                SELECT lab_order_test_id, lab_order_id, test_id
                FROM "{s}"."LAB_ORDER_TEST" WHERE lab_order_test_id = %s
            """,
            insert_sql=f"""
                INSERT INTO "{s}"."LAB_ORDER_TEST" (lab_order_id, test_id)
                VALUES (%s, %s) RETURNING lab_order_test_id
            """,
            update_sql=f"""
                UPDATE "{s}"."LAB_ORDER_TEST"
                SET lab_order_id=%s, test_id=%s
                WHERE lab_order_test_id = %s
            """,
            delete_sql=f'DELETE FROM "{s}"."LAB_ORDER_TEST" WHERE lab_order_test_id = %s',
            fields=[
                FieldConfig(
                    "lab_order_test_id", "Line Item ID", "readonly", readonly_on_create=True
                ),
                FieldConfig(
                    "lab_order_id",
                    "Lab Order",
                    "fk",
                    fk_query=f"""
                        SELECT lab_order_id, lab_order_id::text || ' — ' || status
                        FROM "{s}"."LAB_ORDER" ORDER BY lab_order_id DESC
                    """,
                ),
                FieldConfig(
                    "test_id",
                    "Test",
                    "fk",
                    fk_query=f"""
                        SELECT test_id, test_name FROM "{s}"."LAB_TEST" ORDER BY test_name
                    """,
                ),
            ],
        ),
        "lab_result": TableConfig(
            table="LAB_RESULT",
            title="Lab Results",
            pk="result_id",
            lookup_label="Result ID",
            list_sql=f"""
                SELECT r.result_id, {lot_label} AS order_test,
                       {staff_name} AS technician,
                       r.result_value, r.result_date
                FROM "{s}"."LAB_RESULT" r
                JOIN "{s}"."LAB_ORDER_TEST" lot ON r.lab_order_test_id = lot.lab_order_test_id
                JOIN "{s}"."LAB_ORDER" o ON lot.lab_order_id = o.lab_order_id
                JOIN "{s}"."LAB_TEST" t ON lot.test_id = t.test_id
                JOIN "{s}"."LAB_TECHNICIAN" tech ON r.technician_id = tech.technician_id
                LEFT JOIN staff_remote st ON tech.staff_id = st.staffid
                ORDER BY r.result_date DESC
            """,
            fetch_sql=f"""
                SELECT result_id, lab_order_test_id, technician_id,
                       result_value, result_date
                FROM "{s}"."LAB_RESULT" WHERE result_id = %s
            """,
            insert_sql=f"""
                INSERT INTO "{s}"."LAB_RESULT"
                (lab_order_test_id, technician_id, result_value, result_date)
                VALUES (%s, %s, %s, COALESCE(%s::timestamp, CURRENT_TIMESTAMP))
                RETURNING result_id
            """,
            update_sql=f"""
                UPDATE "{s}"."LAB_RESULT"
                SET lab_order_test_id=%s, technician_id=%s,
                    result_value=%s, result_date=%s
                WHERE result_id = %s
            """,
            delete_sql=f'DELETE FROM "{s}"."LAB_RESULT" WHERE result_id = %s',
            fields=[
                FieldConfig("result_id", "Result ID", "readonly", readonly_on_create=True),
                FieldConfig(
                    "lab_order_test_id",
                    "Order / Test Line",
                    "fk",
                    fk_query=f"""
                        SELECT lot.lab_order_test_id,
                               'Order ' || o.lab_order_id::text || ' — ' || t.test_name
                        FROM "{s}"."LAB_ORDER_TEST" lot
                        JOIN "{s}"."LAB_ORDER" o ON lot.lab_order_id = o.lab_order_id
                        JOIN "{s}"."LAB_TEST" t ON lot.test_id = t.test_id
                        ORDER BY lot.lab_order_test_id DESC
                    """,
                ),
                FieldConfig(
                    "technician_id",
                    "Technician",
                    "fk",
                    fk_query=f"""
                        SELECT t.technician_id,
                               COALESCE(st.firstname || ' ' || st.lastname,
                                        'Tech #' || t.technician_id::text)
                               || ' (' || t.certification || ')'
                        FROM "{s}"."LAB_TECHNICIAN" t
                        LEFT JOIN staff_remote st ON t.staff_id = st.staffid
                        ORDER BY 2
                    """,
                ),
                FieldConfig("result_value", "Result Value"),
                FieldConfig("result_date", "Result Date", "datetime", required=False),
            ],
        ),
    }


def editable_columns(config: TableConfig, *, creating: bool) -> list[FieldConfig]:
    cols: list[FieldConfig] = []
    for f in config.fields:
        if f.field_type == "readonly":
            continue
        if f.column == config.pk and creating:
            continue
        cols.append(f)
    return cols
