-- the cost of lab tests must be positive
ALTER TABLE LAB_TEST
ADD CONSTRAINT chk_cost_positive CHECK (cost > 0);

-- result dates must not be in the future
ALTER TABLE LAB_RESULT
ADD CONSTRAINT chk_result_date CHECK (result_date <= CURRENT_DATE);

-- maintenance dates must not be too far in the past
ALTER TABLE DIAGNOSTIC_EQUIPMENT
ADD CONSTRAINT chk_maintenance CHECK (maintenance_date > '2000-01-01');