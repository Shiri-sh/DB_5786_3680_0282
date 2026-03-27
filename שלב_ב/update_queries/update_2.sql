-- Update the description of lab tests that cost more than $1000 to indicate that they are expensive.

-- before update
SELECT test_id, description, cost
FROM LAB_TEST
WHERE cost > 400;

-- update
UPDATE LAB_TEST
SET description = description || ' (Expensive Test)'
WHERE cost > 400;

-- after update
SELECT test_id, description, cost
FROM LAB_TEST
WHERE cost > 400;