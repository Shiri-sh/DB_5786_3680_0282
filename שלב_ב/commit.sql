-- Step 1: Show initial state
SELECT * FROM LAB_TEST;

-- Step 2: Start transaction
BEGIN;

-- Step 3: Perform update
UPDATE LAB_TEST
SET cost = cost * 1.1;

-- Step 4: Show updated state
SELECT * FROM LAB_TEST;

-- Step 5: Commit
COMMIT;

-- Step 6: Show final state (should remain changed)
SELECT * FROM LAB_TEST;