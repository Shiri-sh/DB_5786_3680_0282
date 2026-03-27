
-- story: apply a 10% discount to lab tests that have never been ordered, as they may be less popular or in lower demand, and this can help to incentivize customers to try them out and increase sales.
-- before update
SELECT test_id, description, cost
FROM LAB_TEST
WHERE test_id NOT IN (
    SELECT DISTINCT ot.test_id
    FROM LAB_ORDER_TEST ot
    JOIN LAB_ORDER o ON ot.lab_order_id = o.lab_order_id
    WHERE o.order_date >= CURRENT_DATE - INTERVAL '1 year'
);

UPDATE LAB_TEST
SET cost = cost * 0.9
WHERE test_id NOT IN (
    SELECT DISTINCT ot.test_id
    FROM LAB_ORDER_TEST ot
    JOIN LAB_ORDER o ON ot.lab_order_id = o.lab_order_id
    WHERE o.order_date >= CURRENT_DATE - INTERVAL '1 year'
);

-- after update
SELECT test_id, description, cost
FROM LAB_TEST
WHERE test_id NOT IN (
    SELECT DISTINCT ot.test_id
    FROM LAB_ORDER_TEST ot
    JOIN LAB_ORDER o ON ot.lab_order_id = o.lab_order_id
    WHERE o.order_date >= CURRENT_DATE - INTERVAL '1 year'
);



-- Update the priority of lab orders that are in 'IN_PROGRESS' status and were ordered more than 30 days ago to 'URGENT'.
-- This helps to identify orders that may require immediate attention and ensure that they are processed in a timely manner.

-- -- before update
-- SELECT lab_order_id, status, priority, order_date
-- FROM LAB_ORDER
-- WHERE status = 'IN_PROGRESS'
-- AND order_date < CURRENT_DATE - INTERVAL '30 days';

-- -- update
-- UPDATE LAB_ORDER
-- SET priority = 'URGENT'
-- WHERE status = 'IN_PROGRESS'
-- AND order_date < CURRENT_DATE - INTERVAL '30 days';

-- -- after update
-- SELECT lab_order_id, status, priority, order_date
-- FROM LAB_ORDER
-- WHERE status = 'IN_PROGRESS'
-- AND order_date < CURRENT_DATE - INTERVAL '30 days';
