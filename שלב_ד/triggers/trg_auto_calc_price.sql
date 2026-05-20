CREATE OR REPLACE FUNCTION fn_trg_update_price() 
RETURNS TRIGGER AS $$
BEGIN
    UPDATE LAB_ORDER 
    SET total_price = fn_calculate_order_total(NEW.lab_order_id)
    WHERE lab_order_id = NEW.lab_order_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_after_test_added
AFTER INSERT ON labs.LAB_ORDER_TEST
FOR EACH ROW EXECUTE FUNCTION fn_trg_update_price();

-- before insert
SELECT lab_order_id, total_price 
FROM LAB_ORDER 
WHERE lab_order_id = 1;

-- insert
INSERT INTO LAB_ORDER_TEST (lab_order_id, test_id) 
VALUES (1, 2);

-- after insert
SELECT lab_order_id, total_price 
FROM LAB_ORDER 
WHERE lab_order_id = 1;