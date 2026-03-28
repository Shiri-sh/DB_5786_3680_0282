
-- result dates must not be in the future
ALTER TABLE LAB_RESULT
ADD CONSTRAINT chk_result_date CHECK (result_date <= CURRENT_DATE);

-- check that it is not possible to insert a lab result with a future date
INSERT INTO LAB_RESULT (result_id, lab_order_test_id, technician_id, result_value, result_date) VALUES (20001, 1, 65, 'Low', '2024-09-01');
