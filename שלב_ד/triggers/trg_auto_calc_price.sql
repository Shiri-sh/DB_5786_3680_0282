CREATE OR REPLACE FUNCTION fn_trg_update_price() 
RETURNS TRIGGER AS $$
DECLARE
    v_new_test_cost DECIMAL(10,2);
BEGIN
    SELECT cost INTO v_new_test_cost 
    FROM LAB_TEST 
    WHERE test_id = NEW.test_id;

    UPDATE LAB_ORDER 
    SET total_price = COALESCE(total_price, 0) + v_new_test_cost
    WHERE lab_order_id = NEW.lab_order_id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_after_test_added
AFTER INSERT ON labs.LAB_ORDER_TEST
FOR EACH ROW EXECUTE FUNCTION fn_trg_update_price();

-- before insert
SELECT lab_order_id, total_price 
FROM labs.LAB_ORDER 
WHERE lab_order_id = 1;

-- insert
INSERT INTO labs.LAB_ORDER_TEST (lab_order_id, test_id) 
VALUES (1, 2);

-- after insert
SELECT lab_order_id, total_price 
FROM labs.LAB_ORDER 
WHERE lab_order_id = 1;