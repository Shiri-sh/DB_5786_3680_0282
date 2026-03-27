
-- Update the status of lab orders to 'COMPLETED' if all associated tests have results.

--before update
SELECT o.lab_order_id, o.status
FROM LAB_ORDER o
JOIN LAB_ORDER_TEST ot ON o.lab_order_id = ot.lab_order_id
LEFT JOIN LAB_RESULT r ON ot.lab_order_test_id = r.lab_order_test_id
GROUP BY o.lab_order_id, o.status
HAVING COUNT(ot.test_id) = COUNT(r.result_id);

-- update
UPDATE LAB_ORDER
SET status = 'COMPLETED'
WHERE lab_order_id IN (
    SELECT o.lab_order_id
    FROM LAB_ORDER o
    JOIN LAB_ORDER_TEST ot ON o.lab_order_id = ot.lab_order_id
    LEFT JOIN LAB_RESULT r ON ot.lab_order_test_id = r.lab_order_test_id
    GROUP BY o.lab_order_id
    HAVING COUNT(ot.test_id) = COUNT(r.result_id)
);

-- after update
SELECT o.lab_order_id, o.status
FROM LAB_ORDER o
JOIN LAB_ORDER_TEST ot ON o.lab_order_id = ot.lab_order_id
LEFT JOIN LAB_RESULT r ON ot.lab_order_test_id = r.lab_order_test_id
GROUP BY o.lab_order_id, o.status
HAVING COUNT(ot.test_id) = COUNT(r.result_id);