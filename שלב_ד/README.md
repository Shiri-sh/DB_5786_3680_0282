# Stage 4 – Database Programming (PL/pgSQL)

This stage turns the static schema into server-side business logic using **PL/pgSQL**. Procedures, functions, and triggers live in the database engine so you get data integrity, audit-friendly behavior, transactional safety, and efficient handling of complex lab workflows.

## Table of contents

- [Project layout](#project-layout)
- [Schema modifications](#schema-modifications)
- [Functions](#functions)
- [Stored procedures](#stored-procedures)
- [Triggers](#triggers)
- [Main programs and verification](#main-programs-and-verification)
- [Quick reference](#quick-reference--plpgsql-concepts-used)

---

## Project layout

| Path | Description |
|------|-------------|
| `alterTables.sql` | Adds `total_price` and `bonus_points` columns |
| `functions/` | Reusable calculation and workload logic |
| `procedures/` | Batch updates and HR-style promotions |
| `triggers/` | Status protection and automatic price recalculation |
| `main_programs/` | `DO` blocks for integration testing |

**Suggested deploy order:** `alterTables.sql` → functions → procedures → triggers → main programs.

---

## Schema modifications

Persistent computed columns avoid expensive recalculations on every read and keep financial snapshots stable when test prices change later.

| Column | Table | Role |
|--------|-------|------|
| `total_price` | `LAB_ORDER` | Cached order total (snapshot, not live `SUM` on current prices) |
| `bonus_points` | `LAB_TECHNICIAN` | Performance / promotion tracking |

```sql
ALTER TABLE labs.LAB_ORDER ADD COLUMN total_price DECIMAL(10, 2) DEFAULT 0;
ALTER TABLE labs.LAB_TECHNICIAN ADD COLUMN bonus_points INT DEFAULT 0;
```

---

## Functions

### `fn_get_doctor_workload`

Loads urgent, non-completed orders for a doctor. Validates the doctor against `staff_remote` (Stage 3 integration) before opening a cursor.

**PL/pgSQL features:** `REFCURSOR`, remote validation, `EXCEPTION` / `RAISE NOTICE`.

```sql
CREATE OR REPLACE FUNCTION fn_get_doctor_workload(p_doctor_id INT) 
RETURNS REFCURSOR AS $$
DECLARE
    row_count INT;
    my_cursor REFCURSOR := 'doctor_cursor';
BEGIN
    -- בדיקה אם הרופא קיים במערכת ה-Staff (שימוש באינטגרציה)
    SELECT COUNT(*) INTO row_count FROM staff_remote WHERE staffid = p_doctor_id;
    
    IF row_count = 0 THEN
        RAISE EXCEPTION 'Doctor with ID % not found in Staff system', p_doctor_id;
    END IF;

    OPEN my_cursor FOR 
        SELECT lab_order_id, order_date, priority 
        FROM labs.LAB_ORDER 
        WHERE doctor_id = p_doctor_id AND priority = 'URGENT' AND status != 'COMPLETED';
    
    RETURN my_cursor;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Error in fn_get_doctor_workload: %', SQLERRM;
        RETURN NULL;
END;
$$ LANGUAGE plpgsql;
```

---

### `fn_calculate_order_total`

Computes the total cost for one order by walking its tests. Uses current `LAB_TEST.cost` values in a controlled loop so the result can be stored as a snapshot on the order row.

**PL/pgSQL features:** explicit `CURSOR`, `FETCH` loop, `EXIT WHEN NOT FOUND`.

```sql
CREATE OR REPLACE FUNCTION fn_calculate_order_total(p_order_id INT) 
RETURNS DECIMAL AS $$
DECLARE
    v_total DECIMAL(10,2) := 0;
    v_test_cost DECIMAL(10,2);
    -- Explicit Cursor
    cur_tests CURSOR FOR 
        SELECT t.cost 
        FROM labs.LAB_TEST t
        JOIN labs.LAB_ORDER_TEST ot ON t.test_id = ot.test_id
        WHERE ot.lab_order_id = p_order_id ;
BEGIN
    OPEN cur_tests;
    LOOP
        FETCH cur_tests INTO v_test_cost;
        EXIT WHEN NOT FOUND;
        v_total := v_total + v_test_cost;
    END LOOP;
    CLOSE cur_tests;
    
    RETURN v_total;
END;
$$ LANGUAGE plpgsql;
```

---

## Stored procedures

### `pr_update_all_order_prices`

Batch-syncs `LAB_ORDER.total_price` for every order by calling `fn_calculate_order_total`.

**PL/pgSQL features:** `RECORD`, `FOR … IN SELECT` loop, `UPDATE`, explicit `COMMIT`.

```sql
CREATE OR REPLACE PROCEDURE pr_update_all_order_prices()
AS $$
DECLARE
    r_order RECORD; -- שימוש ב-Record
BEGIN
    FOR r_order IN SELECT lab_order_id FROM labs.LAB_ORDER LOOP
        UPDATE labs.LAB_ORDER 
        SET total_price = fn_calculate_order_total(r_order.lab_order_id)
        WHERE lab_order_id = r_order.lab_order_id;
    END LOOP;
    COMMIT;
END;
$$ LANGUAGE plpgsql;
```

---

### `pr_promote_technicians`

Awards bonus points to technicians who completed at least `p_min_tests` results.

| Parameter | Meaning |
|-----------|---------|
| `p_min_tests` | Minimum completed results to qualify |
| `p_bonus_amount` | Points added per qualifying technician (must be ≥ 0) |

**PL/pgSQL features:** aggregate cursor (`GROUP BY` / `HAVING`), input validation (`RAISE EXCEPTION`), multi-row `UPDATE`, `RAISE NOTICE`.

```sql
CREATE OR REPLACE PROCEDURE pr_promote_technicians(p_min_tests INT, p_bonus_amount INT)
AS $$
DECLARE
    v_tech_id INT;
    v_count INT;
BEGIN
    IF p_bonus_amount < 0 THEN
        RAISE EXCEPTION 'Bonus cannot be negative';
    END IF;

    FOR v_tech_id, v_count IN   
        SELECT technician_id, COUNT(*) 
        FROM labs.LAB_RESULT 
        GROUP BY technician_id 
        HAVING COUNT(*) >= p_min_tests 
    LOOP
        UPDATE labs.LAB_TECHNICIAN 
        SET bonus_points = bonus_points + p_bonus_amount
        WHERE technician_id = v_tech_id;
        
        RAISE NOTICE 'Technician % received % bonus points for % tests', v_tech_id, p_bonus_amount, v_count;
    END LOOP;
END;
$$ LANGUAGE plpgsql;
```

---

## Triggers

### Status protection — `trg_status_protection`

Blocks changing an order out of `COMPLETED` status so finished lab reports cannot be rewritten at the engine level.

| Object | Type | Event |
|--------|------|-------|
| `fn_trg_check_status` | Trigger function | `BEFORE UPDATE` on `labs.LAB_ORDER` |
| `trg_status_protection` | Trigger | Per row |

```sql
CREATE OR REPLACE FUNCTION fn_trg_check_status() 
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.status = 'COMPLETED' AND NEW.status != 'COMPLETED' THEN
        RAISE EXCEPTION 'Cannot change status once an order is COMPLETED';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_status_protection
BEFORE UPDATE ON labs.LAB_ORDER
FOR EACH ROW EXECUTE FUNCTION fn_trg_check_status();
```

---

### Auto price calculation — `trg_after_test_added`

After a row is inserted into `LAB_ORDER_TEST`, recalculates and updates `LAB_ORDER.total_price` for that order.

| Object | Type | Event |
|--------|------|-------|
| `fn_trg_update_price` | Trigger function | `AFTER INSERT` on `labs.LAB_ORDER_TEST` |
| `trg_after_test_added` | Trigger | Per row |

```sql
CREATE OR REPLACE FUNCTION fn_trg_update_price() 
RETURNS TRIGGER AS $$
BEGIN
    UPDATE LAB_ORDER 
    SET total_price = fn_calculate_order_total(NEW.lab_order_id)
    WHERE lab_order_id = NEW.lab_order_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_after_test_added
AFTER INSERT ON labs.LAB_ORDER_TEST
FOR EACH ROW EXECUTE FUNCTION fn_trg_update_price();
```

---

## Main programs and verification

Anonymous `DO` blocks exercise functions, procedures, and triggers. Run them in pgAdmin (or `psql`) after all objects are created.

### Block A – Financial management

1. Calls `fn_calculate_order_total` for a sample order.
2. Calls `pr_update_all_order_prices()` to sync all orders.

**Expected:** `RAISE NOTICE` messages with the computed total and a synchronization success message.

```sql
DO $$
DECLARE
    v_total_cost DECIMAL;
    v_order_id INT := 1; -- נניח לבדיקה
BEGIN
    -- זימון פונקציה
    v_total_cost := fn_calculate_order_total(v_order_id);
    RAISE NOTICE 'The total cost for order % is %', v_order_id, v_total_cost;
    
    -- זימון פרוצדורה
    CALL pr_update_all_order_prices();
    RAISE NOTICE 'All order prices have been synchronized.';
END $$;
```

**Screenshot (Block A):**

> TODO: Add pgAdmin **Messages** / **Data Output** screenshot after running Block A.

---

### Block B – Staff performance

1. Opens `fn_get_doctor_workload` for a sample doctor ID.
2. Calls `pr_promote_technicians(5, 100)`.

**Expected:** Cursor-ready notice plus promotion notices per qualifying technician.

```sql
DO $$
DECLARE
    v_cursor REFCURSOR;
    v_doc_id INT := 101; -- רופא לדוגמה מה-Staff
BEGIN
    -- זימון פונקציה (שמחזירה RefCursor)
    v_cursor := fn_get_doctor_workload(v_doc_id);
    RAISE NOTICE 'Cursor for doctor % is ready.', v_doc_id;

    -- זימון פרוצדורה
    CALL pr_promote_technicians(5, 100); -- טכנאים עם 5 בדיקות מקבלים 100 נקודות
END $$;
```

**Screenshot (Block B):**

> TODO: Add screenshot showing notices after running Block B.

---

### Block C – Trigger integrity

This update **should fail** if status protection is installed:

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
| `DO` blocks | Block A, Block B |
