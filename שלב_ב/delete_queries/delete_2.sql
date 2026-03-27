
-- Delete diagnostic equipment that has not been maintained in the last 5 years.
-- There are too old and may not be safe to use, and removing them can help to free up storage space and reduce clutter in the database.

-- before deletion
SELECT * FROM DIAGNOSTIC_EQUIPMENT
WHERE maintenance_date < CURRENT_DATE - INTERVAL '5 years';

-- deletion
DELETE FROM DIAGNOSTIC_EQUIPMENT
WHERE maintenance_date < CURRENT_DATE - INTERVAL '5 years';

-- after deletion
SELECT * FROM DIAGNOSTIC_EQUIPMENT
WHERE maintenance_date < CURRENT_DATE - INTERVAL '5 years';