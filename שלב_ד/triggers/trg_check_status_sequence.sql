CREATE OR REPLACE FUNCTION fn_trg_check_status() 
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.status = 'COMPLETED' AND NEW.status != 'COMPLETED' THEN
        RAISE EXCEPTION 'Cannot change status once an order is COMPLETED';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_status_protection
BEFORE UPDATE ON labs.LAB_ORDER
FOR EACH ROW EXECUTE FUNCTION fn_trg_check_status();