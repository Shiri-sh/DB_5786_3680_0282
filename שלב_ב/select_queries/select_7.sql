-- story: the manager wants to see all lab results with the technician id, order id and test name
-- one approach is to join the results with the orders, tests and technicians, and select the relevant columns

SELECT 
    r.result_date,
    o.lab_order_id,
    t.test_name,
    r.result_value,
    tech.staff_id
FROM LAB_RESULT r
JOIN LAB_ORDER_TEST ot ON r.lab_order_test_id = ot.lab_order_test_id
JOIN LAB_ORDER o ON ot.lab_order_id = o.lab_order_id
JOIN LAB_TEST t ON ot.test_id = t.test_id
JOIN LAB_TECHNICIAN tech ON r.technician_id = tech.technician_id
ORDER BY r.result_date DESC;

-- second approach is to use subqueries to get the order id, test name and technician id for each result
SELECT 
    r.result_date,
    (
        SELECT ot.lab_order_id
        FROM LAB_ORDER_TEST ot
        WHERE ot.lab_order_test_id = r.lab_order_test_id
    ) AS lab_order_id,
    (
        SELECT t.test_name
        FROM LAB_TEST t
        JOIN LAB_ORDER_TEST ot ON t.test_id = ot.test_id
        WHERE ot.lab_order_test_id = r.lab_order_test_id
    ) AS test_name,
    r.result_value,
    (
        SELECT tech.staff_id
        FROM LAB_TECHNICIAN tech
        WHERE tech.technician_id = r.technician_id
    ) AS staff_id
FROM LAB_RESULT r
ORDER BY r.result_date;