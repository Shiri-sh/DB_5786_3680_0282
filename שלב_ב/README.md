

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

<pre>
-- SQL code here
</pre>

Before Execution Screenshot:

After Execution Screenshot:

---

## DELETE Query 2

Description:

<pre>
-- SQL code here
</pre>

Before Execution Screenshot:

After Execution Screenshot:

---

## DELETE Query 3

Description:

<pre>
-- SQL code here
</pre>

Before Execution Screenshot:

After Execution Screenshot:

---

# 4. UPDATE Queries

---

## UPDATE Query 1

Description:

<pre>
-- SQL code here
</pre>

Before Execution Screenshot:

After Execution Screenshot:

---

## UPDATE Query 2

Description:

<pre>
-- SQL code here
</pre>

Before Execution Screenshot:

After Execution Screenshot:

---

## UPDATE Query 3

Description:

<pre>
-- SQL code here
</pre>

Before Execution Screenshot:

After Execution Screenshot:

---

# 5. Constraints

---

## Constraint 1

Description of the change:

<pre>
ALTER TABLE ...
</pre>

Attempt to insert invalid data:

<pre>
INSERT INTO ...
</pre>

Execution Screenshot (error message):

---

## Constraint 2

Description of the change:

<pre>
ALTER TABLE ...
</pre>

Attempt to insert invalid data:

<pre>
INSERT INTO ...
</pre>

Execution Screenshot (error message):

---

## Constraint 3

Description of the change:

<pre>
ALTER TABLE ...
</pre>

Attempt to insert invalid data:

<pre>
INSERT INTO ...
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

