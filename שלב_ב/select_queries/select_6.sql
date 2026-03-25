-- story: the manager wants to see all urgent orders that are not completed and were ordered more than 2 days ago

-- one approach is to filter the orders by priority, status and order date
SELECT *
FROM LAB_ORDER
WHERE priority = 'URGENT'
AND status != 'COMPLETED'
AND order_date < CURRENT_DATE - INTERVAL '2 days';

-- second approach is to use BETWEEN to filter the order date
SELECT *
FROM LAB_ORDER
WHERE priority = 'URGENT'
AND status != 'COMPLETED'
AND order_date BETWEEN DATE '1900-01-01' AND CURRENT_DATE - INTERVAL '2 days';