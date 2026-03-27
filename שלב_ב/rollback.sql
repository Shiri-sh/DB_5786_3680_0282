-- Step 1: Show initial state
SELECT * FROM LAB_TEST;

SELECT * FROM LAB_ORDER;

-- Step 2: Start transaction
BEGIN;

-- Step 3: Perform updates
UPDATE LAB_TEST
SET cost = cost * 1.2;

-- Step 4: Perform delete
DELETE FROM LAB_ORDER
WHERE status = 'ORDERED';

-- Step 5: Show changed state
SELECT * FROM LAB_TEST;

SELECT * FROM LAB_ORDER;

-- Step 6: Rollback
ROLLBACK;

-- Step 7: Show reverted state
SELECT * FROM LAB_TEST;

SELECT * FROM LAB_ORDER;