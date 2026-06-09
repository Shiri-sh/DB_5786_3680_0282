# DB Project - Hospital Management System
**Selected Division**: Laboratory & Diagnostics Division

### 🧑‍💻 Authors
- Shiri Shachor
- Yael Shushan

---

## Table of Contents
* [Stage 1 — ERD, DSD & Database Creation](./שלב_א/README.MD)
* [Stage 2 — SQL Queries, Updates & Constraints](./שלב_ב/README.md)
* [Stage 3 — Integration & Foreign Data Wrapper (FDW)](./שלב_ג/README.md)
* [Stage 4 — Database Programming (PL/pgSQL)](./שלב_ד/README.md)
* [Stage 5 — Graphical User Interface (GUI)](#stage-5--graphical-user-interface-gui---שלב-ה)

---

# Stage 5 – Graphical User Interface (GUI) - שלב ה'

חלק זה מתאר את הממשק הגרפי (GUI) שנבנה עבור מערכת ניהול המעבדה הרפואית. הממשק מאפשר עבודה שוטפת מול בסיס הנתונים בצורה ידידותית וחזותית, תוך הפעלת כל היכולות הלוגיות והאינטגרטיביות שפותחו בשלבים הקודמים.

---

## 🛠️ הסבר על דרך העבודה והכלים לפיתוח המערכת

ממשק המשתמש נבנה כיישום שולחני (Desktop Application) תוך שימוש בשפת **Python** וארכיטקטורת שכבות מסודרת שמפרידה בין הלוגיקה העסקית, החיבור לבסיס הנתונים ושכבת התצוגה:

1. **CustomTkinter (עיצוב הממשק):**
   בחרנו להשתמש בספריית `customtkinter` (הרחבה מודרנית לספריית `tkinter` המובנית של פייתון). הספרייה מספקת רכיבים ויזואליים יפהפיים (כפתורים מעוגלים, טפסים מודרניים, תפריטי צד מבוססי ניווט) ותומכת באופן מובנה בהחלפה מהירה בין **מצב כהה (Dark Mode)** ל**מצב בהיר (Light Mode)**.

2. **Psycopg2-binary & Connection Pooling (ניהול מסד הנתונים):**
   החיבור ל-PostgreSQL מנוהל באמצעות מנגנון **Connection Pool** (בריכת חיבורים) דרך כלי ה-`ThreadedConnectionPool` של `psycopg2`. שיטה זו מונעת פתיחה וסגירה מרובה של חיבורים בכל פעולה, משפרת ביצועים ומאפשרת טיפול בריבוי תהליכים (Multi-threading).

3. **שילוב פונקציות ופרוצדורות משלב ד':**
   המשק משולב עמוק עם הלוגיקה הפנימית של בסיס הנתונים:
   * **פרוצדורות:** המערכת קוראת ישירות ל-`pr_update_all_order_prices` (עדכון מחירי כל ההזמנות) ול-`pr_promote_technicians` (קידום טכנאים עם בונוסים), ושולפת את ההודעות (`RAISE NOTICE`) שנוצרו בדאטהבייס כדי להציג אותן למשתמש בדו-שיח מפורט.
   * **פונקציות ואינטגרציה:** מסך האנליטיקה משתמש בפונקציה `fn_get_doctor_workload` כדי להביא את עומס העבודה של רופאים, כאשר רשימת הרופאים עצמה נשלפת בזמן אמת מטבלת האינטגרציה ה-Staff החיצונית (`staff_remote`) שהוקמה בשלב ג'.

4. **מנגנון הגנה חכם מפני שגיאות (Constraint & Trigger Interception):**
   במקרה של הפרת אילוצי דאטהבייס (למשל, ניסיון לעדכן הזמנה שכבר הושלמה אשר נחסמת על ידי הטריגר `trg_status_protection`), האפליקציה לוכדת את הודעת השגיאה המדויקת מהשרת ומציגה אותה למשתמש בתיבת שיח ידידותית ומעוצבת, במקום לקרוס.

---

## 🚀 הוראות כניסה והפעלה של המערכת

הקוד והקבצים המלאים של הממשק מאורגנים בתיקיית ההגשה [DBProject_5786_3680_0282/שלב ה](./DBProject_5786_3680_0282/שלב%20ה/).

### שלבי הרצה מהירים:
1. **הפעלת בסיס הנתונים:** ודאו שקונטיינר ה-Docker של ה-Postgres שלכן פועל (`docker compose up -d db`).
2. **ניווט לתיקיית שלב ה':**
   ```bash
   cd "DBProject_5786_3680_0282/שלב ה"
   ```
3. **יצירת והפעלת סביבה וירטואלית:**
   ```bash
   python -m venv .venv
   # הפעלה בחלונות (PowerShell):
   .venv\Scripts\Activate.ps1
   ```
4. **התקנת הספריות הנדרשות:**
   ```bash
   pip install -r requirements.txt
   ```
5. **הגדרת קובץ `.env`:** העתיקו את קובץ `.env.example` לקובץ `.env` ועדכנו בו את פרטי החיבור לשרת (שרת מקומי: `localhost`, משתמש: `MyUser`, סיסמה: `pass1234`, בסיס נתונים: `Hospital`).
6. **הרצת האפליקציה:**
   ```bash
   python main.py
   ```

---

## 📸 גלריית תמונות מסך מקיפה של המערכת

להלן צילומי מסך המדגימים את המסכים השונים, את מצבי התצוגה (מצב בהיר ומצב כהה) ואת ביצוע הפעולות מול מסד הנתונים:

### 🌤️ ממשק במצב בהיר (Light Mode)

#### 1. לוח הבקרה הראשי (Dashboard) - מצב בהיר
לוח הבקרה המציג את פרטי החיבור וגרסת מסד הנתונים הנוכחית.
![Dashboard - Light Mode](./DBProject_5786_3680_0282/שלב%20ה/screenshots/01_light_dashboard.png)

#### 2. מודול ניהול הזמנות (CRUD Lab Orders) - מצב בהיר
טופס מילוי וניהול הזמנות המעבדה בשילוב עם טבלת הנתונים.
![CRUD Orders - Light Mode](./DBProject_5786_3680_0282/שלב%20ה/screenshots/02_light_crud_orders.png)

#### 3. מודול ניהול טכנאים (CRUD Lab Technicians) - מצב בהיר
מסך להוספה, עדכון ומחיקת טכנאי המעבדה עם תיבות בחירה חכמות למקצוע/הסמכה ומזהי עובדים.
![CRUD Technicians - Light Mode](./DBProject_5786_3680_0282/שלב%20ה/screenshots/03_light_crud_technicians.png)

#### 4. שאילתות ודוחות (Analytics & Reports) - מצב בהיר
מסך האנליטיקה המציג את תוצאות הדוח של 5 הבדיקות הפופולריות ביותר.
![Analytics - Light Mode](./DBProject_5786_3680_0282/שלב%20ה/screenshots/04_light_analytics.png)

---

### 🌙 ממשק במצב כהה (Dark Mode)

#### 5. לוח הבקרה הראשי (Dashboard) - מצב כהה
לוח הבקרה עם התאמה מלאה לעיצוב הכהה.
![Dashboard - Dark Mode](./DBProject_5786_3680_0282/שלב%20ה/screenshots/05_dark_dashboard.png)

#### 6. מודול ניהול הזמנות (CRUD Lab Orders) - מצב כהה
![CRUD Orders - Dark Mode](./DBProject_5786_3680_0282/שלב%20ה/screenshots/06_dark_crud_orders.png)

#### 7. מודול ניהול טכנאים (CRUD Lab Technicians) - מצב כהה
![CRUD Technicians - Dark Mode](./DBProject_5786_3680_0282/שלב%20ה/screenshots/07_dark_crud_technicians.png)

#### 8. שאילתות ודוחות (Analytics & Reports) - מצב כהה
שאילתת מעקב אחר הזמנות דחופות שממתינות מעל 48 שעות.
![Analytics - Dark Mode](./DBProject_5786_3680_0282/שלב%20ה/screenshots/08_dark_analytics.png)

---

### ⚡ פעולות מסד נתונים, אילוצים ויומני ריצה (Interactions & Logs)

#### 9. הפעלת אילוצים וחסימת טריגר (Trigger Database Block)
צילום מסך המדגים את לכידת השגיאה מהשרת כאשר המשתמש מנסה לעדכן הזמנה בסטטוס `COMPLETED`. הטריגר `trg_status_protection` הודף את השינוי, ובסיס הנתונים דוחה את הטרנזקציה. המערכת מציגה את השגיאה כהלכה בתיבת דו-שיח ייעודית מבלי לקרוס.
![Trigger Status Protection Error](./DBProject_5786_3680_0282/שלב%20ה/screenshots/09_trigger_error_dialog.png)

#### 10. הרצת פרוצדורה וקבלת יומן ריצה (Stored Procedure Notice Logs)
הרצת הפרוצדורה `pr_promote_technicians` לקבלת בונוסים. המערכת שולפת ומציגה בתוך חלון גלילה מיוחד את ה-`RAISE NOTICE` המועברים ישירות מהשרת (רשימת העובדים שקיבלו בונוס וכמות הבדיקות שביצעו).
![Stored Procedure Notice Logs](./DBProject_5786_3680_0282/שלב%20ה/screenshots/10_procedure_notice_dialog.png)
