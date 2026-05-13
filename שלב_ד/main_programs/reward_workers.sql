DO $$
DECLARE
    v_cursor REFCURSOR;
    v_doc_id INT := 101; -- רופא לדוגמה מה-Staff
BEGIN
    -- זימון פונקציה (שמחזירה RefCursor)
    v_cursor := fn_get_doctor_workload(v_doc_id);
    RAISE NOTICE 'Cursor for doctor % is ready.', v_doc_id;

    -- זימון פרוצדורה
    CALL pr_promote_technicians(5, 100); -- טכנאים עם 5 בדיקות מקבלים 100 נקודות
END $$;
