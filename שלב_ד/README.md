# Stage 4 – Database Programming (PL/pgSQL)

This stage turns the static schema into server-side business logic using **PL/pgSQL**. Procedures, functions, and triggers live in the database engine so you get data integrity, audit-friendly behavior, transactional safety, and efficient handling of complex lab workflows.

## Table of contents

- [Project layout](#project-layout)
- [Schema modifications](#schema-modifications)
- [Functions](#functions)
- [Stored procedures](#stored-procedures)
- [Triggers](#triggers)
- [Main programs and verification](#main-programs-and-verification)

---

## Project layout

| Path | Description |
|------|-------------|
| [`alterTables.sql`](alterTables.sql) | Adds `total_price` and `bonus_points` columns |
| [`functions/`](functions/) | Reusable calculation and workload logic |
| [`procedures/`](procedures/) | Batch updates and HR-style promotions |
| [`triggers/`](triggers/) | Status protection and automatic price recalculation |
| [`main_programs/`](main_programs/) | `DO` blocks for integration testing |

**Suggested deploy order:** `alterTables.sql` → functions → procedures → triggers → main programs.

---

## Schema modifications

Persistent computed columns avoid expensive recalculations on every read and keep financial snapshots stable when test prices change later.

**File:** [`alterTables.sql`](alterTables.sql)

```sql
ALTER TABLE LAB_ORDER ADD COLUMN total_price DECIMAL(10, 2) DEFAULT 0;
ALTER TABLE LAB_TECHNICIAN ADD COLUMN bonus_points INT DEFAULT 0;
```

| Column | Table | Role |
|--------|-------|------|
| `total_price` | `LAB_ORDER` | Cached order total (snapshot, not live `SUM` on current prices) |
| `bonus_points` | `LAB_TECHNICIAN` | Performance / promotion tracking |

---

## Functions

### `fn_get_doctor_workload`

**File:** [`functions/fn_get_doctor_workload.sql`](functions/fn_get_doctor_workload.sql)

**Purpose:** Loads urgent, non-completed orders for a doctor. Validates the doctor against `staff_remote` (Stage 3 integration) before opening a cursor.

**PL/pgSQL features:** `REFCURSOR`, remote validation, `EXCEPTION` / `RAISE NOTICE`.

**Signature:** `fn_get_doctor_workload(p_doctor_id INT) → REFCURSOR`

---

### `fn_calculate_order_total`

**File:** [`functions/fn_calculate_order_total.sql`](functions/fn_calculate_order_total.sql)

**Purpose:** Computes the total cost for one order by walking its tests. Uses current `LAB_TEST.cost` values in a controlled loop so the result can be stored as a snapshot on the order row.

**PL/pgSQL features:** explicit `CURSOR`, `FETCH` loop, `EXIT WHEN NOT FOUND`.

**Signature:** `fn_calculate_order_total(p_order_id INT) → DECIMAL`

---

## Stored procedures

### `pr_update_all_order_prices`

**File:** [`procedures/pr_update_all_order_prices.sql`](procedures/pr_update_all_order_prices.sql)

**Purpose:** Batch-syncs `LAB_ORDER.total_price` for every order by calling `fn_calculate_order_total`.

**PL/pgSQL features:** `RECORD`, `FOR … IN SELECT` loop, `UPDATE`, explicit `COMMIT`.

---

### `pr_promote_technicians`

**File:** [`procedures/pr_promote_technicians.sql`](procedures/pr_promote_technicians.sql)

**Purpose:** Awards bonus points to technicians who completed at least `p_min_tests` results.

**PL/pgSQL features:** aggregate cursor (`GROUP BY` / `HAVING`), input validation (`RAISE EXCEPTION`), multi-row `UPDATE`, `RAISE NOTICE`.

**Parameters:**

| Parameter | Meaning |
|-----------|---------|
| `p_min_tests` | Minimum completed results to qualify |
| `p_bonus_amount` | Points added per qualifying technician (must be ≥ 0) |

---

## Triggers

### Status protection (`trg_status_protection`)

**File:** [`triggers/trg_check_status_sequence.sql`](triggers/trg_check_status_sequence.sql)

**Purpose:** Blocks changing an order out of `COMPLETED` status so finished lab reports cannot be rewritten at the engine level.

| Object | Type | Event |
|--------|------|-------|
| `fn_trg_check_status` | Trigger function | `BEFORE UPDATE` on `LAB_ORDER` |
| `trg_status_protection` | Trigger | Per row |

---

### Auto price calculation (`trg_after_test_added`)

**File:** [`triggers/trg_auto_calc_price.sql`](triggers/trg_auto_calc_price.sql)

**Purpose:** After a row is inserted into `LAB_ORDER_TEST`, recalculates and updates `LAB_ORDER.total_price` for that order.

| Object | Type | Event |
|--------|------|-------|
| `fn_trg_update_price` | Trigger function | `AFTER INSERT` on `LAB_ORDER_TEST` |
| `trg_after_test_added` | Trigger | Per row |

---

## Main programs and verification

Anonymous `DO` blocks exercise functions, procedures, and triggers. Run them in pgAdmin (or `psql`) after all objects are created.

### Block A – Financial management

**File:** [`main_programs/money_managment.sql`](main_programs/money_managment.sql)

1. Calls `fn_calculate_order_total` for a sample order.
2. Calls `pr_update_all_order_prices()` to sync all orders.

**Expected:** `RAISE NOTICE` messages with the computed total and a synchronization success message.

**Screenshot (Block A):**

> TODO: Add pgAdmin **Messages** / **Data Output** screenshot after running `money_managment.sql`.

---

### Block B – Staff performance

**File:** [`main_programs/reward_workers.sql`](main_programs/reward_workers.sql)

1. Opens `fn_get_doctor_workload` for a sample doctor ID.
2. Calls `pr_promote_technicians(5, 100)`.

**Expected:** Cursor-ready notice plus promotion notices per qualifying technician.

**Screenshot (Block B):**

> TODO: Add screenshot showing notices after running `reward_workers.sql`.

---

### Block C – Trigger integrity

Run manually (not in a separate file). This update **should fail** if status protection is installed:

```sql
UPDATE LAB_ORDER
SET status = 'IN_PROGRESS'
WHERE status = 'COMPLETED';
```

**Expected:** Error from `fn_trg_check_status` — transaction rejected for a completed order.

**Screenshot (Block C):**

> TODO: Add screenshot of the pgAdmin error proving the trigger blocked the update.

---

## Quick reference – PL/pgSQL concepts used

| Concept | Where used |
|---------|------------|
| `REFCURSOR` | `fn_get_doctor_workload` |
| Explicit cursor + loop | `fn_calculate_order_total` |
| `RECORD` + batch loop | `pr_update_all_order_prices` |
| Cursor over aggregates | `pr_promote_technicians` |
| `BEFORE` / `AFTER` triggers | Status lock, price auto-update |
| `DO` blocks | `main_programs/*.sql` |
