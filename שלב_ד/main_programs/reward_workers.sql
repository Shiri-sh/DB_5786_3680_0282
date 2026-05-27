DO $$
DECLARE
    v_cursor REFCURSOR;
    v_doc_id INT := 101;
BEGIN
    v_cursor := fn_get_doctor_workload(v_doc_id);
    RAISE NOTICE 'Cursor for doctor % is ready.', v_doc_id;

    LOOP
        FETCH v_cursor INTO v_order_id, v_order_date, v_priority;
        EXIT WHEN NOT FOUND; -- תנאי יציאה כשהסמן מתרוקן
        
        RAISE NOTICE 'Urgent Order ID: %, Date: %, Priority: %', v_order_id, v_order_date, v_priority;
    END LOOP;
    
    CLOSE v_cursor; 

    CALL pr_promote_technicians(5, 100);
END $$;
