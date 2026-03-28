-- the cost of lab tests must be positive
ALTER TABLE LAB_TEST
ADD CONSTRAINT chk_cost_positive CHECK (cost > 0);

-- check that it is not possible to insert a lab test with a negative cost
INSERT INTO LAB_TEST
(test_id, test_name, description, normal_range, cost, sample_type)
VALUES (501, 'Lipid Panel', 'Lipid Panel description', 'Normal', -354.31, 'Blood');