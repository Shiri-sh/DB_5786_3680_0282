-- Delete all lab orders that were placed more than two years ago and are still in 'ORDERED' status.
--  This helps to clean up old orders that were never completed or canceled, and free up storage space in

-- BEFORE
SELECT * FROM LAB_ORDER
WHERE status = 'ORDERED'
AND order_date < CURRENT_DATE - INTERVAL '2 year';

-- delete from deepest table first
DELETE FROM LAB_RESULT
WHERE lab_order_test_id IN (
    SELECT lab_order_test_id
    FROM LAB_ORDER_TEST
    WHERE lab_order_id IN (
        SELECT lab_order_id
        FROM LAB_ORDER
        WHERE status = 'ORDERED'
        AND order_date < CURRENT_DATE - INTERVAL '2 year'
    )
);

-- delete from middle table
DELETE FROM LAB_ORDER_TEST
WHERE lab_order_id IN (
    SELECT lab_order_id
    FROM LAB_ORDER
    WHERE status = 'ORDERED'
    AND order_date < CURRENT_DATE - INTERVAL '2 year'
);

-- delete from main table
DELETE FROM LAB_ORDER
WHERE status = 'ORDERED'
AND order_date < CURRENT_DATE - INTERVAL '2 year';

-- AFTER
SELECT * FROM LAB_ORDER
WHERE status = 'ORDERED'
AND order_date < CURRENT_DATE - INTERVAL '2 year';