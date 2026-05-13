CREATE OR REPLACE PROCEDURE pr_update_all_order_prices()
AS $$
DECLARE
    r_order RECORD; -- שימוש ב-Record
BEGIN
    FOR r_order IN SELECT lab_order_id FROM LAB_ORDER LOOP
        UPDATE LAB_ORDER 
        SET total_price = fn_calculate_order_total(r_order.lab_order_id)
        WHERE lab_order_id = r_order.lab_order_id;
    END LOOP;
    COMMIT;
END;
$$ LANGUAGE plpgsql;