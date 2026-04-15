

-- 1. Index on order_date (used in many WHERE conditions)
CREATE INDEX idx_lab_order_date
ON LAB_ORDER(order_date);

-- 2. Index on lab_order_id in LAB_ORDER_TEST (for JOINs)
CREATE INDEX idx_lot_order_id
ON LAB_ORDER_TEST(lab_order_id);

-- 3. Index on lab_order_test_id in LAB_RESULT (for JOINs)
CREATE INDEX idx_result_lot_id
ON LAB_RESULT(lab_order_test_id);