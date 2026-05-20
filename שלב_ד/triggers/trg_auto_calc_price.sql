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