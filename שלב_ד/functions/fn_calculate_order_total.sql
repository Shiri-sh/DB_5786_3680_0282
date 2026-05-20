CREATE OR REPLACE FUNCTION fn_calculate_order_total(p_order_id INT) 
RETURNS DECIMAL AS $$
DECLARE
    v_total DECIMAL(10,2) := 0;
    v_test_cost DECIMAL(10,2);
    -- Explicit Cursor
    cur_tests CURSOR FOR 
        SELECT t.cost 
        FROM labs.LAB_TEST t
        JOIN labs.LAB_ORDER_TEST ot ON t.test_id = ot.test_id
        WHERE ot.lab_order_id = p_order_id ;
BEGIN
    OPEN cur_tests;
    LOOP
        FETCH cur_tests INTO v_test_cost;
        EXIT WHEN NOT FOUND;
        v_total := v_total + v_test_cost;
    END LOOP;
    CLOSE cur_tests;
    
    RETURN v_total;
END;
$$ LANGUAGE plpgsql;