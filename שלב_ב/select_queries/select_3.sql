
-- story: the managar wants to see orders that are not completed but have some results done, bottelneck
-- one approach is to join the orders with the tests and results, filter by status and count the results
SELECT 
    o.lab_order_id,
    o.status,
    COUNT(DISTINCT ot.test_id) AS total_tests,
    COUNT(r.result_id) AS results_done
FROM LAB_ORDER o
JOIN LAB_ORDER_TEST ot ON o.lab_order_id = ot.lab_order_id
LEFT JOIN LAB_RESULT r ON ot.lab_order_test_id = r.lab_order_test_id
WHERE o.status != 'COMPLETED'
GROUP BY o.lab_order_id, o.status
HAVING COUNT(r.result_id) > 0;