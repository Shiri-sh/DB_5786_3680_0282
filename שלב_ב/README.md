

# Phase B – Queries and Constraints

---

# 1. SELECT Queries (Paired Queries)

---

## Query 1 – Description

השאילתה מחזירה את מספר תוצאות המעבדה שבוצעו על ידי כל טכנאי, ומדרגת אותם בסדר יורד לפי כמות התוצאות.

מטרת השאילתה היא לאפשר למנהל המעבדה לזהות את הטכנאים הפעילים ביותר ולנתח את עומס העבודה.

השאילתה אינה טריוויאלית מכיוון שהיא משלבת נתונים משתי טבלאות ומבצעת אגרגציה (COUNT).
### Method 1

<pre>
SELECT 
    tech.technician_id,
    tech.certification,
    COUNT(r.result_id) AS total_results
FROM LAB_TECHNICIAN tech
LEFT JOIN LAB_RESULT r ON tech.technician_id = r.technician_id
GROUP BY tech.technician_id, tech.certification
ORDER BY total_results DESC;
</pre>

Execution Screenshot:

---

### Method 2

<pre>
SELECT 
    technician_id,
    certification,
    (
        SELECT COUNT(*) 
        FROM LAB_RESULT r 
        WHERE r.technician_id = tech.technician_id
    ) AS total_results
FROM LAB_TECHNICIAN tech
ORDER BY total_results DESC;
</pre>

Execution Screenshot:

---

### Comparison Between Methods


Method 1:
משתמש ב־JOIN ו־GROUP BY כדי לחשב את כמות התוצאות לכל טכנאי בפעולה אחת.

Method 2:
משתמש בתת־שאילתה (correlated subquery) שמתבצעת עבור כל טכנאי בנפרד.

Which one is more efficient and why:

Method 1 יעילה יותר, מכיוון שהחישוב מתבצע בפעולה אחת על כל הנתונים.
Method 2 פחות יעילה, כי תת־השאילתה רצה שוב עבור כל שורה.
---

## Query 2 – Description

השאילתה מחזירה את הבדיקות הנפוצות ביותר במעבדה, על פי מספר הפעמים שכל בדיקה הוזמנה, ומציגה את 5 הבדיקות המובילות.

מטרת השאילתה היא לאפשר למנהל המעבדה לזהות אילו בדיקות הן הפופולריות ביותר, לצורך ניתוח ביקושים וקבלת החלטות תפעוליות.

השאילתה אינה טריוויאלית מכיוון שהיא משלבת נתונים ממספר טבלאות ומבצעת אגרגציה (COUNT) ומיון (ORDER BY).
### Method 1

<pre>
SELECT 
    t.test_name,
    COUNT(*) AS usage_count
FROM LAB_ORDER_TEST ot
JOIN LAB_TEST t ON ot.test_id = t.test_id
GROUP BY t.test_name
ORDER BY usage_count DESC
LIMIT 5;
</pre>

Execution Screenshot:

---

### Method 2

<pre>
SELECT 
    test_name,
    (
        SELECT COUNT(*) 
        FROM LAB_ORDER_TEST ot 
        WHERE ot.test_id = t.test_id
    ) AS usage_count
FROM LAB_TEST t
ORDER BY usage_count DESC
LIMIT 5;
</pre>

Execution Screenshot:

---

### Comparison Between Methods

Method 1:
משתמש ב־JOIN ו־GROUP BY כדי לחשב את מספר ההזמנות לכל בדיקה בפעולה אחת.

Method 2:
משתמש בתת־שאילתה שמחשבת את מספר ההזמנות עבור כל בדיקה בנפרד.

Which one is more efficient and why:

Method 1 יעילה יותר, מכיוון שהחישוב מתבצע בפעולה אחת על כל הנתונים.
Method 2 פחות יעילה, כי תת־השאילתה מתבצעת עבור כל שורה בטבלת הבדיקות.

---

## Query 5 – Description
השאילתה מחזירה ציוד שלא עבר תחזוקה במשך יותר משנה, יחד עם מספר הימים שעברו מאז התחזוקה האחרונה, וממיינת את התוצאות לפי משך הזמן שעבר.

מטרת השאילתה היא לאפשר למנהל המעבדה לזהות ציוד הדורש תחזוקה דחופה ולמנוע תקלות.

השאילתה אינה טריוויאלית מכיוון שהיא מבצעת חישובים על שדות תאריך ומשווה ביניהם.

### Method 1

<pre>
SELECT 
    equipment_id,
    equipment_name,
    maintenance_date,
    CURRENT_DATE - maintenance_date AS days_since_maintenance
FROM DIAGNOSTIC_EQUIPMENT
WHERE maintenance_date < CURRENT_DATE - INTERVAL '1 year'
ORDER BY days_since_maintenance DESC;
</pre>

Execution Screenshot:

---

### Method 2

<pre>
SELECT 
    equipment_id,
    equipment_name,
    maintenance_date,
    CURRENT_DATE - maintenance_date AS days_since_maintenance
FROM DIAGNOSTIC_EQUIPMENT
WHERE 
    EXTRACT(YEAR FROM CURRENT_DATE) - EXTRACT(YEAR FROM maintenance_date) >= 1
ORDER BY days_since_maintenance DESC;
</pre>

Execution Screenshot:

---

### Comparison Between Methods

Method 1:
משתמש בהפרש תאריכים מדויק (CURRENT_DATE - INTERVAL) כדי לזהות ציוד שלא טופל מעל שנה.

Method 2:
משתמש בפירוק התאריך (YEAR) ומשווה רק את השנה, ללא התחשבות בחודשים ובימים.

Which one is more efficient and why:

Method 1 מדויק יותר ולכן עדיף לשימוש בפועל.
Method 2 פחות מדויק, כי הוא עלול להחזיר תוצאות שגויות כאשר ההפרש הוא פחות משנה אך בשנים שונות.

---

## Query 7 – Description

השאילתה השאילתה מחזירה את כל תוצאות המעבדה יחד עם פרטים נוספים: מזהה הזמנה, שם הבדיקה, ערך התוצאה ומזהה הטכנאי שביצע אותה.

מטרת השאילתה היא לספק תצוגה מלאה ומרוכזת של נתוני התוצאות עבור שימוש בממשק המשתמש או לצורך ניתוח נתונים.

השאילתה אינה טריוויאלית מכיוון שהיא משלבת נתונים ממספר טבלאות באמצעות JOINים..
### Method 1

<pre>
SELECT 
    r.result_date,
    (
        SELECT ot.lab_order_id
        FROM LAB_ORDER_TEST ot
        WHERE ot.lab_order_test_id = r.lab_order_test_id
    ) AS lab_order_id,
    (
        SELECT t.test_name
        FROM LAB_TEST t
        JOIN LAB_ORDER_TEST ot ON t.test_id = ot.test_id
        WHERE ot.lab_order_test_id = r.lab_order_test_id
    ) AS test_name,
    r.result_value,
    (
        SELECT tech.staff_id
        FROM LAB_TECHNICIAN tech
        WHERE tech.technician_id = r.technician_id
    ) AS staff_id
FROM LAB_RESULT r
ORDER BY r.result_date;
</pre>

Execution Screenshot:

---

### Method 2

<pre>
SELECT 
    r.result_date,
    o.lab_order_id,
    t.test_name,
    r.result_value,
    tech.staff_id
FROM LAB_RESULT r
JOIN LAB_ORDER_TEST ot ON r.lab_order_test_id = ot.lab_order_test_id
JOIN LAB_ORDER o ON ot.lab_order_id = o.lab_order_id
JOIN LAB_TEST t ON ot.test_id = t.test_id
JOIN LAB_TECHNICIAN tech ON r.technician_id = tech.technician_id
ORDER BY r.result_date DESC;
</pre>

Execution Screenshot:

---

### Comparison Between Methods

Method 1:
משתמש במספר JOINים כדי להביא את כל הנתונים הרלוונטיים בפעולה אחת.

Method 2:
משתמש בתתי־שאילתות (subqueries) כדי להביא כל שדה בנפרד עבור כל שורה.

Which one is more efficient and why:

Method 1 יעילה יותר, מכיוון שהיא מבצעת את כל החיבורים בפעולה אחת.
Method 2 פחות יעילה, כי תתי־השאילתות מתבצעות מחדש עבור כל שורה בתוצאה.

---

# 2. Additional SELECT Queries

---

## Query 3

Description:
השאילתה מחזירה הזמנות שלא הושלמו אך כבר קיימות עבורן תוצאות חלקיות.

מטרת השאילתה היא לזהות צווארי בקבוק בתהליך, כלומר הזמנות שהחלו להתבצע אך טרם הסתיימו.

השאילתה אינה טריוויאלית מכיוון שהיא משלבת מספר טבלאות, מבצעת אגרגציה ומשתמשת בתנאי HAVING.

<pre>
SELECT 
    o.lab_order_id,
    o.status,
    COUNT(DISTINCT ot.test_id) AS total_tests,
    COUNT(r.result_id) AS results_done
FROM LAB_ORDER o
JOIN LAB_ORDER_TEST ot ON o.lab_order_id = ot.lab_order_id
LEFT JOIN LAB_RESULT r ON ot.lab_order_test_id = r.lab_order_test_id
WHERE o.status != 'COMPLETED'
GROUP BY o.lab_order_id, o.status
HAVING COUNT(r.result_id) > 0;
</pre>

Execution Screenshot:

---

## Query 6

Description:
השאילתה מחזירה את כל הזמנות המעבדה הדחופות שטרם הושלמו ואשר הוזמנו לפני יותר מיומיים.

מטרת השאילתה היא לאפשר למנהל המעבדה לזהות הזמנות דחופות שמתעכבות בטיפול, ולפעול להאצת הטיפול בהן.

השאילתה אינה טריוויאלית מכיוון שהיא משלבת מספר תנאי סינון על שדות שונים, כולל שימוש בחישוב על שדה תאריך.

<pre>
SELECT *
FROM LAB_ORDER
WHERE priority = 'URGENT'
AND status != 'COMPLETED'
AND order_date < CURRENT_DATE - INTERVAL '2 days';
</pre>

Execution Screenshot:

---

## Query 4

Description:
השאילתה מחזירה את מספר תוצאות המעבדה לפי שנה וחודש.

מטרת השאילתה היא לאפשר ניתוח מגמות וביצועים לאורך זמן, כגון עומס חודשי.

השאילתה אינה טריוויאלית מכיוון שהיא משתמשת בפירוק שדה תאריך ובאגרגציה.

<pre>
SELECT 
    EXTRACT(YEAR FROM result_date) AS year,
    EXTRACT(MONTH FROM result_date) AS month,
    COUNT(*) AS total_results
FROM LAB_RESULT
GROUP BY year, month
ORDER BY year, month;
</pre>

Execution Screenshot:

---

## Query 8

Description:
השאילתה מחזירה את כל הזמנות המעבדה יחד עם הבדיקות שבוצעו במסגרת כל הזמנה והעלות של כל בדיקה.

מטרת השאילתה היא לספק תצוגה מלאה של הזמנות לצורך הצגה בממשק משתמש או ניתוח נתונים.

השאילתה אינה טריוויאלית מכיוון שהיא משלבת נתונים ממספר טבלאות באמצעות JOINים.

<pre>
SELECT 
    o.lab_order_id,
    o.visit_id,
    o.doctor_id,
    o.status,
    o.priority,
    t.test_name,
    t.cost
FROM LAB_ORDER o
JOIN LAB_ORDER_TEST ot ON o.lab_order_id = ot.lab_order_id
JOIN LAB_TEST t ON ot.test_id = t.test_id
ORDER BY o.order_date DESC;
</pre>

Execution Screenshot:

---

# 3. DELETE Queries

---

## DELETE Query 1

Description:
השאילתה מוחקת הזמנות מעבדה ישנות (מעל שנתיים) שעדיין נמצאות בסטטוס "ORDERED".

מטרת השאילתה היא לנקות נתונים ישנים ולא רלוונטיים מהמערכת.

המחיקה מתבצעת במספר שלבים, בהתאם לתלויות בין הטבלאות, על מנת לשמור על שלמות הנתונים (תחילה תוצאות, לאחר מכן בדיקות ולבסוף ההזמנות).

<pre>
-- Delete all lab orders that were placed more than two years ago and are still in 'ORDERED' status.
--  This helps to clean up old orders that were never completed or canceled, and free up storage space in

-- BEFORE
SELECT * FROM LAB_ORDER
WHERE status = 'ORDERED'
AND order_date < CURRENT_DATE - INTERVAL '2 year';

-- delete from deepest table first
DELETE FROM LAB_RESULT
WHERE lab_order_test_id IN (
    SELECT lab_order_test_id
    FROM LAB_ORDER_TEST
    WHERE lab_order_id IN (
        SELECT lab_order_id
        FROM LAB_ORDER
        WHERE status = 'ORDERED'
        AND order_date < CURRENT_DATE - INTERVAL '2 year'
    )
);

-- delete from middle table
DELETE FROM LAB_ORDER_TEST
WHERE lab_order_id IN (
    SELECT lab_order_id
    FROM LAB_ORDER
    WHERE status = 'ORDERED'
    AND order_date < CURRENT_DATE - INTERVAL '2 year'
);

-- delete from main table
DELETE FROM LAB_ORDER
WHERE status = 'ORDERED'
AND order_date < CURRENT_DATE - INTERVAL '2 year';

-- AFTER
SELECT * FROM LAB_ORDER
WHERE status = 'ORDERED'
AND order_date < CURRENT_DATE - INTERVAL '2 year';
</pre>

Before Execution Screenshot:

After Execution Screenshot:

---

## DELETE Query 2

Description:
השאילתה מוחקת ציוד מעבדה שלא עבר תחזוקה במשך יותר מחמש שנים.

מטרת השאילתה היא להסיר ציוד ישן ולא תקין מהמערכת.

השאילתה משתמשת בתנאי על שדה תאריך לצורך סינון הנתונים למחיקה.

<pre>

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
</pre>

Before Execution Screenshot:

After Execution Screenshot:

---

## DELETE Query 3

Description:
השאילתה מוחקת רשומות של בדיקות הזמנה (LAB_ORDER_TEST) שאין להן תוצאות קשורות.

מטרת השאילתה היא לנקות נתונים לא שלמים או נטושים ולשפר את איכות הנתונים במערכת.

השאילתה אינה טריוויאלית מכיוון שהיא משתמשת בתת־שאילתה עם NOT EXISTS כדי לזהות רשומות ללא קשר לטבלה אחרת.

<pre>
-- story: delete lab order tests that have no associated results, as they may represent incomplete or abandoned orders, 
-- and removing them can help to clean up the database and improve data integrity.

-- BEFORE
SELECT *
FROM LAB_ORDER_TEST ot
WHERE NOT EXISTS (
    SELECT 1
    FROM LAB_RESULT r
    WHERE r.lab_order_test_id = ot.lab_order_test_id
);

-- DELETE
DELETE FROM LAB_ORDER_TEST ot
WHERE NOT EXISTS (
    SELECT 1
    FROM LAB_RESULT r
    WHERE r.lab_order_test_id = ot.lab_order_test_id
);

-- AFTER
SELECT *
FROM LAB_ORDER_TEST ot
WHERE NOT EXISTS (
    SELECT 1
    FROM LAB_RESULT r
    WHERE r.lab_order_test_id = ot.lab_order_test_id
);
</pre>

Before Execution Screenshot:

After Execution Screenshot:

---

# 4. UPDATE Queries

---

## UPDATE Query 1

Description:
השאילתה מעדכנת את סטטוס ההזמנות ל־"COMPLETED" במקרים בהם לכל הבדיקות המשויכות להזמנה קיימות תוצאות.

מטרת השאילתה היא לשמור על עקביות הנתונים ולהבטיח שהסטטוס של ההזמנה משקף את מצבה בפועל.

השאילתה אינה טריוויאלית מכיוון שהיא משלבת מספר טבלאות, מבצעת אגרגציה ומשתמשת בתת־שאילתה.

<pre>

-- Update the status of lab orders to 'COMPLETED' if all associated tests have results.

--before update
SELECT o.lab_order_id, o.status
FROM LAB_ORDER o
JOIN LAB_ORDER_TEST ot ON o.lab_order_id = ot.lab_order_id
LEFT JOIN LAB_RESULT r ON ot.lab_order_test_id = r.lab_order_test_id
GROUP BY o.lab_order_id, o.status
HAVING COUNT(ot.test_id) = COUNT(r.result_id);

-- update
UPDATE LAB_ORDER
SET status = 'COMPLETED'
WHERE lab_order_id IN (
    SELECT o.lab_order_id
    FROM LAB_ORDER o
    JOIN LAB_ORDER_TEST ot ON o.lab_order_id = ot.lab_order_id
    LEFT JOIN LAB_RESULT r ON ot.lab_order_test_id = r.lab_order_test_id
    GROUP BY o.lab_order_id
    HAVING COUNT(ot.test_id) = COUNT(r.result_id)
);

-- after update
SELECT o.lab_order_id, o.status
FROM LAB_ORDER o
JOIN LAB_ORDER_TEST ot ON o.lab_order_id = ot.lab_order_id
LEFT JOIN LAB_RESULT r ON ot.lab_order_test_id = r.lab_order_test_id
GROUP BY o.lab_order_id, o.status
HAVING COUNT(ot.test_id) = COUNT(r.result_id);
</pre>

Before Execution Screenshot:

After Execution Screenshot:

---

## UPDATE Query 2

Description:
השאילתה מעדכנת את תיאור הבדיקות שמחירן גבוה מערך מסוים, ומוסיפה להן ציון שהן בדיקות יקרות.

מטרת השאילתה היא להדגיש בדיקות יקרות לצורך הצגה בממשק המשתמש או לצורך ניתוח.

השאילתה משתמשת בתנאי על שדה מספרי לעדכון הנתונים.

<pre>
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
</pre>

Before Execution Screenshot:

After Execution Screenshot:

---

## UPDATE Query 3

Description:
השאילתה מעניקה הנחה של 10% לבדיקות שלא הוזמנו בשנה האחרונה.

מטרת השאילתה היא לעודד שימוש בבדיקות פחות פופולריות.

השאילתה אינה טריוויאלית מכיוון שהיא משתמשת בתת־שאילתה ובסינון על בסיס תאריך.

<pre>

-- story: apply a 10% discount to lab tests that have never been ordered, as they may be less popular or in lower demand, and this can help to incentivize customers to try them out and increase sales.
-- before update
SELECT test_id, description, cost
FROM LAB_TEST
WHERE test_id NOT IN (
    SELECT DISTINCT ot.test_id
    FROM LAB_ORDER_TEST ot
    JOIN LAB_ORDER o ON ot.lab_order_id = o.lab_order_id
    WHERE o.order_date >= CURRENT_DATE - INTERVAL '1 year'
);

UPDATE LAB_TEST
SET cost = cost * 0.9
WHERE test_id NOT IN (
    SELECT DISTINCT ot.test_id
    FROM LAB_ORDER_TEST ot
    JOIN LAB_ORDER o ON ot.lab_order_id = o.lab_order_id
    WHERE o.order_date >= CURRENT_DATE - INTERVAL '1 year'
);

-- after update
SELECT test_id, description, cost
FROM LAB_TEST
WHERE test_id NOT IN (
    SELECT DISTINCT ot.test_id
    FROM LAB_ORDER_TEST ot
    JOIN LAB_ORDER o ON ot.lab_order_id = o.lab_order_id
    WHERE o.order_date >= CURRENT_DATE - INTERVAL '1 year'
);



-- Update the priority of lab orders that are in 'IN_PROGRESS' status and were ordered more than 30 days ago to 'URGENT'.
-- This helps to identify orders that may require immediate attention and ensure that they are processed in a timely manner.

-- -- before update
-- SELECT lab_order_id, status, priority, order_date
-- FROM LAB_ORDER
-- WHERE status = 'IN_PROGRESS'
-- AND order_date < CURRENT_DATE - INTERVAL '30 days';

-- -- update
-- UPDATE LAB_ORDER
-- SET priority = 'URGENT'
-- WHERE status = 'IN_PROGRESS'
-- AND order_date < CURRENT_DATE - INTERVAL '30 days';

-- -- after update
-- SELECT lab_order_id, status, priority, order_date
-- FROM LAB_ORDER
-- WHERE status = 'IN_PROGRESS'
-- AND order_date < CURRENT_DATE - INTERVAL '30 days';</pre>

Before Execution Screenshot:

After Execution Screenshot:

---

# 5. Constraints

---

## Constraint 1

Description of the change:
האילוץ מוודא כי העלות של בדיקות מעבדה חייבת להיות חיובית.

מטרת האילוץ היא לשמור על תקינות הנתונים ולמנוע הכנסת ערכים לא הגיוניים למערכת.

<pre>
ALTER TABLE LAB_TEST
ADD CONSTRAINT chk_cost_positive CHECK (cost > 0);
</pre>

Attempt to insert invalid data:

<pre>
INSERT INTO LAB_TEST
(test_id, test_name, description, normal_range, cost, sample_type)
VALUES (501, 'Lipid Panel', 'Lipid Panel description', 'Normal', -354.31, 'Blood');
</pre>

Execution Screenshot (error message):

---

## Constraint 2

Description of the change:
האילוץ מוודא כי תאריך תוצאת בדיקה אינו יכול להיות בעתיד.

מטרת האילוץ היא להבטיח אמינות נתונים, שכן תוצאות בדיקה לא יכולות להתקבל לפני ביצוען בפועל.

<pre>
ALTER TABLE LAB_RESULT
ADD CONSTRAINT chk_result_date CHECK (result_date <= CURRENT_DATE);
</pre>

Attempt to insert invalid data:

<pre>
INSERT INTO LAB_RESULT (result_id, lab_order_test_id, technician_id, result_value, result_date) 
VALUES (20001, 1, 65, 'Low', '2024-09-01');
</pre>

Execution Screenshot (error message):

---

## Constraint 3

Description of the change:
האילוץ מוודא כי תאריך התחזוקה של ציוד אינו מוקדם מתאריך מסוים.

מטרת האילוץ היא למנוע הכנסת נתונים לא רלוונטיים או ישנים מדי למערכת.

<pre>
ALTER TABLE DIAGNOSTIC_EQUIPMENT
ADD CONSTRAINT chk_maintenance CHECK (maintenance_date > '2010-01-01');
</pre>

Attempt to insert invalid data:

<pre>
INSERT INTO DIAGNOSTIC_EQUIPMENT (equipment_id,equipment_name,department_id,maintenance_date) 
VALUES (501, 'Autoclave', 8, '2000-03-26');
</pre>

Execution Screenshot (error message):

---

# 6. Rollback and Commit

---

## Rollback Example

<pre>
BEGIN;

-- UPDATE statement

ROLLBACK;
</pre>

Before Execution Screenshot:

After UPDATE Screenshot:

After ROLLBACK Screenshot:

---

## Commit Example

<pre>
BEGIN;

-- UPDATE statement

COMMIT;
</pre>

Before Execution Screenshot:

After UPDATE Screenshot:

After COMMIT Screenshot:

