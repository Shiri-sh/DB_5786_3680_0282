-- story: the manager wants to see all lab orders with their tests and costs, ordered by order date
-- one approach is to join the orders with the tests and select the relevant columns
SELECT 
    o.lab_order_id,
    o.visit_id,
    o.doctor_id,
    o.status,
    o.priority,
    t.test_name,
    t.cost
FROM LAB_ORDER o
JOIN LAB_ORDER_TEST ot ON o.lab_order_id = ot.lab_order_id
JOIN LAB_TEST t ON ot.test_id = t.test_id
ORDER BY o.order_date DESC;