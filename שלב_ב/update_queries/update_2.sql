-- Update the description of lab tests that cost more than $1000 to indicate that they are expensive.
UPDATE LAB_TEST
SET description = description || ' (Expensive Test)'
WHERE cost > 1000;