-- Update the priority of lab orders that are in 'IN_PROGRESS' status and were ordered more than 3 days ago to 'URGENT'.
-- This helps to identify orders that may require immediate attention and ensure that they are processed in a timely manner.
UPDATE LAB_ORDER
SET priority = 'URGENT'
WHERE status = 'IN_PROGRESS'
AND order_date < CURRENT_DATE - INTERVAL '3 days';