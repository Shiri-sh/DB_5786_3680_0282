-- story: delete lab order tests that have no associated results, as they may represent incomplete or abandoned orders, 
-- and removing them can help to clean up the database and improve data integrity.

-- BEFORE
SELECT *
FROM LAB_ORDER_TEST ot
WHERE NOT EXISTS (
    SELECT 1
    FROM LAB_RESULT r
    WHERE r.lab_order_test_id = ot.lab_order_test_id
);

-- DELETE
DELETE FROM LAB_ORDER_TEST ot
WHERE NOT EXISTS (
    SELECT 1
    FROM LAB_RESULT r
    WHERE r.lab_order_test_id = ot.lab_order_test_id
);

-- AFTER
SELECT *
FROM LAB_ORDER_TEST ot
WHERE NOT EXISTS (
    SELECT 1
    FROM LAB_RESULT r
    WHERE r.lab_order_test_id = ot.lab_order_test_id
);