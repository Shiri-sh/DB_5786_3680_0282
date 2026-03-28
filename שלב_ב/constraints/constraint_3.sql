-- maintenance dates must not be too far in the past
ALTER TABLE DIAGNOSTIC_EQUIPMENT
ADD CONSTRAINT chk_maintenance CHECK (maintenance_date > '2010-01-01');

-- check that it is not possible to insert a diagnostic equipment with a maintenance date that is too far in the past
INSERT INTO DIAGNOSTIC_EQUIPMENT (equipment_id,equipment_name,department_id,maintenance_date) VALUES (501, 'Autoclave', 8, '2000-03-26');
