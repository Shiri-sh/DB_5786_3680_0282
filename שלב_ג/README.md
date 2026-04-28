<div dir="rtl">

# 🔗 שלב 3 – אינטגרציה ומבטים (Integration & Views)

📜 שלב זה מתמקד באינטגרציה בין בסיס הנתונים של **מחלקת המעבדות (LABS)** לבין בסיס הנתונים של **ניהול כוח האדם (STAFF)** — מרכיב חיוני במערכת הניהול הכוללת של המרכז הרפואי. המטרה היא לבנות מבנה מאוחד המאפשר מבט מקיף על פעילות המעבדה, תוך שיוך כל בדיקה והזמנה לצוות הרפואי הרלוונטי.

כחלק מאינטגרציה זו, נוצרו מבטי SQL (Views) הן מנקודת המבט של המחלקה שלנו והן מנקודת המבט של המחלקה השותפה. מבטים אלו מספקים גישה יעילה ומותאמת לתפקיד לנתונים המשולבים, ומקלים על שליפה וניתוח של המידע הרלוונטי לצרכים התפעוליים של כל צד.

---

## 🗂️ דיאגרמות ERD ו-DSD

### ERD (מחלקת מעבדות - LABS)
> **TODO:** הוסיפי כאן את תמונת ה-ERD המקורית שלכם.
![ERD](images/Stage3/LABS_ERD.jpg)

### ERD (מחלקת כוח אדם - STAFF)
> **TODO:** הוסיפי כאן את תמונת ה-ERD שקיבלתם מהקבוצה השנייה.
![ERD](images/Stage3/STAFF_ERD.jpg)

### ERD משולב (Integration)
> **TODO:** צרפי תרשים המראה את הקשר בין Lab_Order ל-Staff.
![ERD_Integration](images/Stage3/Integrated_ERD.png)

---

## 🧠 החלטות אינטגרציה

- האינטגרציה בוצעה באמצעות **PostgreSQL's `postgres_fdw`** (Foreign Data Wrapper) המאפשר שאילתות ישירות מול בסיס הנתונים המרוחק.
- טבלאות מרוחקות הוגדרו כ**טבלאות זרות (Foreign Tables)** בבסיס הנתונים המקומי לצורך אינטגרציה לוגית בזמן אמת.
- הוחלט להשתמש ב-**LEFT JOIN** במבטים המשולבים כדי להבטיח שכל הזמנות המעבדה יוצגו, גם אם אין התאמה מלאה ב-ID מול טבלת הצוות הזר (בשל חוסר תיאום בנתוני המקור).
- **שקיפות:** כל השלבים הטכניים תועדו להלן כדי להראות את תהליך החיבור בין המערכות.

---

## 📝 תהליך האינטגרציה ופקודות SQL

> פקודות ה-SQL הבאות שימשו בתהליך האינטגרציה. לכל פקודה מצורף הסבר קצר על תפקידה.

### 1. הפעלת ה-Foreign Data Wrapper
הרחבה זו מאפשרת ל-PostgreSQL לגשת לטבלאות מבסיס נתונים אחר.

```sql
CREATE EXTENSION IF NOT EXISTS postgres_fdw;
```

2. הגדרת החיבור לשרת המרוחק
פקודה זו מגדירה את השרת החיצוני (ה-Database של הקבוצה השנייה).
```sql
CREATE SERVER staff_mgmt_server
FOREIGN DATA WRAPPER postgres_fdw
OPTIONS (host 'localhost', dbname 'HopitalLocalDB', port '5432');
```
3. יצירת מיפוי משתמש (User Mapping)
הגדרה כיצד המשתמש המקומי יתחבר למסד הנתונים המרוחק.
```sql
CREATE USER MAPPING FOR current_user
SERVER staff_mgmt_server
OPTIONS (user 'MyUser', password 'pass123');
```
4. גישה לטבלת הצוות המרוחקת
יצירת טבלה זרה המייצגת את טבלת ה-Staff מהאגף השני

```sql
CREATE FOREIGN TABLE staff_remote (
    "StaffId" INTEGER,
    "FirstName" VARCHAR(50),
    "LastName" VARCHAR(50),
    "Phone" VARCHAR(20),
    "Status" VARCHAR(20),
    "Email" VARCHAR(100),
    "HireDate" DATE
) SERVER staff_mgmt_server
OPTIONS (schema_name 'public', table_name 'STAFF');
```
### מבטים (Views) ושאילתות אנליטיות
סעיף זה מציג את מבטי ה-SQL שנוצרו כחלק משלב 3, המספקים תובנות עבור מחלקת המעבדות ומחלקת כוח האדם.

---

מבט 1 – מחלקת מעבדות: סקירת הזמנות ובדיקות
תיאור: מבט זה משלב נתונים פנימיים של המעבדה כדי להציג את פרטי הבדיקות שהוזמנו ועלויותיהן
```sql
CREATE OR REPLACE VIEW view_labs_internal AS
SELECT 
    t.test_name, 
    t.cost, 
    o.order_date, 
    o.status AS order_status
FROM LAB_TEST t
JOIN LAB_ORDER_TEST ot ON t.test_id = ot.test_id
JOIN LAB_ORDER o ON ot.lab_order_id = o.lab_order_id;
```
![view1](images/Stage3/view_1.jpg)

---
מבט 2 – מבט אינטגרטיבי: שיוך הזמנות לרופאים (STAFF)
תיאור: מבט זה מבצע את האינטגרציה בפועל. הוא מחבר בין הזמנת מעבדה (מתוך LABS) לבין הרופא שהזמין אותה (מתוך STAFF הזר).
```sql
CREATE OR REPLACE VIEW view_integrated_lab_results AS
SELECT 
    lo.lab_order_id,
    lo.order_date,
    sr."FirstName" || ' ' || sr."LastName" AS ordering_doctor,
    sr."Email" AS doctor_contact,
    lo.status AS lab_status,
    lo.priority
FROM LAB_ORDER lo
LEFT JOIN staff_remote sr ON lo.doctor_id = sr."StaffId";
```
![view2](images/Stage3/view_2.jpg)

---
מבט 3 -  נקודת מבט של צוות חיצוני
תיאור: מבט זה מספק מדריך של הצוות הרפואי המעורב
```sql
CREATE OR REPLACE VIEW view_external_staff_directory AS
SELECT "StaffId", "FirstName", "LastName", "Email", "Status", "HireDate"
FROM staff_remote
```
![view3](images/Stage3/view_3.jpg)

---

שאילתה 1
מצא את כל ההזמנות שבוצעו על ידי רופאים בכירים (שנשכרו לפני 2024)
```sql
SELECT * FROM view_integrated_lab_results r
JOIN view_external_staff_directory s ON r.ordering_doctor = (s."FirstName" || ' ' || s."LastName")
WHERE s."HireDate" < '2024-01-01';
```
![query1](images/Stage3/query_1.jpg)

---

שאילתה 2 
סיכום סדרי עדיפויות במעבדה לפי רופא מזמין
```sql
SELECT ordering_doctor, priority, COUNT(*) as total_orders
FROM view_integrated_lab_results
WHERE ordering_doctor IS NOT NULL
GROUP BY ordering_doctor, priority;
```
![query2](images/Stage3/query_2.jpg)

---

## סיכום
בשלב אינטגרציה זה:

בוצע חיבור טכני בין שני בסיסי נתונים נפרדים באמצעות Foreign Data Wrappers.

הוקם גשר לוגי המאפשר שיוך בזמן אמת של פעולות מעבדה לאנשי צוות.

תועדו כל השלבים להבטחת שקיפות מלאה כנדרש.

נוצרו כלים אנליטיים (Views) המאפשרים הפקת תובנות משולבות משני העולמות.
