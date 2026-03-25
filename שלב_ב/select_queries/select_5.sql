-- story: the manager wants to see the equipment that was maintained more than a year ago, and how many days have passed since the last maintenance

-- one approach is to filter the equipment by maintenance date, calculate the days since maintenance and order them by that

SELECT 
    equipment_id,
    equipment_name,
    maintenance_date,
    CURRENT_DATE - maintenance_date AS days_since_maintenance
FROM DIAGNOSTIC_EQUIPMENT
WHERE maintenance_date < CURRENT_DATE - INTERVAL '1 year'
ORDER BY days_since_maintenance DESC;

-- this query retrieves all equipment that has not been maintained for at least one year by comparing the year part of the current date with the year of the last maintenance date.
-- this approach is not fully accurate because it only compares the year values and ignores the exact difference in months and days.
SELECT 
    equipment_id,
    equipment_name,
    maintenance_date,
    CURRENT_DATE - maintenance_date AS days_since_maintenance
FROM DIAGNOSTIC_EQUIPMENT
WHERE 
    EXTRACT(YEAR FROM CURRENT_DATE) - EXTRACT(YEAR FROM maintenance_date) >= 1
ORDER BY days_since_maintenance DESC;