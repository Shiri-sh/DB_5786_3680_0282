-- Delete all lab orders that were placed more than a year ago and are still in 'ORDERED' status.
--  This helps to clean up old orders that were never completed or canceled, and free up storage space in
DELETE FROM LAB_ORDER
WHERE status = 'ORDERED'
AND order_date < CURRENT_DATE - INTERVAL '1 year';