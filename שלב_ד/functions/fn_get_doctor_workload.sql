CREATE OR REPLACE FUNCTION fn_get_doctor_workload(p_doctor_id INT) 
RETURNS REFCURSOR AS $$
DECLARE
    row_count INT;
    my_cursor REFCURSOR := 'doctor_cursor';
BEGIN
    -- בדיקה אם הרופא קיים במערכת ה-Staff (שימוש באינטגרציה)
    SELECT COUNT(*) INTO row_count FROM staff_remote WHERE staffid = p_doctor_id;
    
    IF row_count = 0 THEN
        RAISE EXCEPTION 'Doctor with ID % not found in Staff system', p_doctor_id;
    END IF;

    OPEN my_cursor FOR 
        SELECT lab_order_id, order_date, priority 
        FROM labs.LAB_ORDER 
        WHERE doctor_id = p_doctor_id AND priority = 'URGENT' AND status != 'COMPLETED';
    
    RETURN my_cursor;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Error in fn_get_doctor_workload: %', SQLERRM;
        RETURN NULL;
END;
$$ LANGUAGE plpgsql;