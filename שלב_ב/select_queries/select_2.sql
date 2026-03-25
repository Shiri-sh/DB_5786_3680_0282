
-- story: the managar wants to see the most popular tests in the lab
-- one approach is to count the number of times each test was ordered and order them by that count
SELECT 
    t.test_name,
    COUNT(*) AS usage_count
FROM LAB_ORDER_TEST ot
JOIN LAB_TEST t ON ot.test_id = t.test_id
GROUP BY t.test_name
ORDER BY usage_count DESC
LIMIT 5;
-- second approach is to use a subquery to count the orders for each test
SELECT 
    test_name,
    (
        SELECT COUNT(*) 
        FROM LAB_ORDER_TEST ot 
        WHERE ot.test_id = t.test_id
    ) AS usage_count
FROM LAB_TEST t
ORDER BY usage_count DESC
LIMIT 5;