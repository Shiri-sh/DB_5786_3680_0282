CREATE OR REPLACE PROCEDURE pr_promote_technicians(p_min_tests INT, p_bonus_amount INT)
AS $$
DECLARE
    v_tech_id INT;
    v_count INT;
BEGIN
    IF p_bonus_amount < 0 THEN
        RAISE EXCEPTION 'Bonus cannot be negative';
    END IF;

    FOR v_tech_id, v_count IN   
        SELECT technician_id, COUNT(*) 
        FROM labs.LAB_RESULT 
        GROUP BY technician_id 
        HAVING COUNT(*) >= p_min_tests 
    LOOP
        UPDATE labs.LAB_TECHNICIAN 
        SET bonus_points = bonus_points + p_bonus_amount
        WHERE technician_id = v_tech_id;
        
        RAISE NOTICE 'Technician % received % bonus points for % tests', v_tech_id, p_bonus_amount, v_count;
    END LOOP;
END;
$$ LANGUAGE plpgsql;