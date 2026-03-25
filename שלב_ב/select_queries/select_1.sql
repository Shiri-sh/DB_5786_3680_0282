
-- story: the lab manager wants to know who of the technicians has the most results
-- one approach is to count the number of results for each technician and order them by that count
SELECT 
    tech.technician_id,
    tech.certification,
    COUNT(r.result_id) AS total_results
FROM LAB_TECHNICIAN tech
LEFT JOIN LAB_RESULT r ON tech.technician_id = r.technician_id
GROUP BY tech.technician_id, tech.certification
ORDER BY total_results DESC;

-- second approach is to use a subquery to count the results for each technician
SELECT 
    technician_id,
    certification,
    (
        SELECT COUNT(*) 
        FROM LAB_RESULT r 
        WHERE r.technician_id = tech.technician_id
    ) AS total_results
FROM LAB_TECHNICIAN tech;

-- JOIN + GROUP BY = יותר יעיל לרוב (פחות חישובים חוזרים)