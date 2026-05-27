CREATE OR REPLACE FUNCTION fn_trg_check_status() 
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.status = 'COMPLETED' THEN
        RAISE EXCEPTION 'Transaction Rejected: This laboratory order is COMPLETED and locked. No modifications are allowed.';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_status_protection
BEFORE UPDATE ON labs.LAB_ORDER
FOR EACH ROW EXECUTE FUNCTION fn_trg_check_status();


-- בשאילתה הזו ננסה לעדכן ישירות הזמנה סגורה
UPDATE LAB_ORDER 
SET status = 'IN_PROGRESS' 
WHERE status = 'COMPLETED';
