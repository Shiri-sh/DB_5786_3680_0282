DO $$
DECLARE
    v_total_cost DECIMAL;
    v_order_id INT := 1; -- נניח לבדיקה
BEGIN
    -- זימון פונקציה
    v_total_cost := fn_calculate_order_total(v_order_id);
    RAISE NOTICE 'The total cost for order % is %', v_order_id, v_total_cost;
    
    -- זימון פרוצדורה
    CALL pr_update_all_order_prices();
    RAISE NOTICE 'All order prices have been synchronized.';
END $$;