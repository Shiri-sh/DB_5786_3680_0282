-- story: the manager wants to see the number of lab results per month and year. Know how many tests are managed to be deliver each month

-- one approach is to extract the year and month from the result date, group by them and count the results
SELECT 
    EXTRACT(YEAR FROM result_date) AS year,
    EXTRACT(MONTH FROM result_date) AS month,
    COUNT(*) AS total_results
FROM LAB_RESULT
GROUP BY year, month
ORDER BY year, month;