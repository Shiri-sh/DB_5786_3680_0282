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
   הממשק אינו רק מבצע פעולות CRUD פשוטות, אלא משולב עמוק עם הלוגיקה הפנימית של בסיס הנתונים:
   * **פרוצדורות:** המערכת קוראת ישירות ל-`pr_update_all_order_prices` (עדכון מחירי כל ההזמנות) ול-`pr_promote_technicians` (קידום טכנאים עם בונוסים), ושולפת את ההודעות (`RAISE NOTICE`) שנוצרו בדאטהבייס כדי להציג אותן למשתמש.
   * **פונקציות ואינטגרציה:** מסך האנליטיקה משתמש בפונקציה `fn_get_doctor_workload` כדי להביא את עומס העבודה של רופאים, כאשר רשימת הרופאים עצמה נשלפת בזמן אמת מטבלת האינטגרציה ה-Staff החיצונית (`staff_remote`) שהוקמה בשלב ג'.

4. **מנגנון הגנה חכם מפני שגיאות (Constraint Catching):**
   במקרה של הפרת אילוצי דאטהבייס (למשל, ניסיון לעדכן הזמנה שכבר הושלמה, פעולה שנחסמת על ידי הטריגר `trg_status_protection`), האפליקציה לוכדת את הודעת השגיאה המדויקת מהשרת ומציגה אותה למשתמש בתיבת שיח ידידותית ומעוצבת, במקום לקרוס.

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

## 📸 תמונות מסך של המערכת בפעולה

להלן צילומי מסך המדגימים את המסכים המרכזיים של האפליקציה שיצרנו:

### 1. לוח הבקרה הראשי (Dashboard)
מציג את סטטוס החיבור לבסיס הנתונים ואת גרסת השרת הפעילה, ומאפשר ניווט מהיר ומעבר בין מצב כהה לבהיר.
![Dashboard](./DBProject_5786_3680_0282/שלב%20ה/screenshots/gui_screenshots/01_dashboard.png)

### 2. מסך ניהול הזמנות (CRUD LAB_ORDER)
ניהול מלא של הזמנות המעבדה, תצוגה בטבלה, טעינת רשומות, עדכון ומחיקה. שדות מפתח זר (כמו מזהה רופא) מוצגים כתיבת בחירה עם תיאור טקסטואלי נוח.
![CRUD Orders](./DBProject_5786_3680_0282/שלב%20ה/screenshots/gui_screenshots/02_crud_orders.png)

### 3. מסך ניהול טכנאים (CRUD LAB_TECHNICIAN)
הוספה ועדכון של טכנאי המעבדה בטבלה.
![CRUD Technicians](./DBProject_5786_3680_0282/שלב%20ה/screenshots/gui_screenshots/03_crud_technicians.png)

### 4. שאילתות אנליטיות ודוחות (Analytics)
הרצת שאילתות מורכבות משלב ב', קריאה לפרוצדורות שלב ד' עם קבלת Notice לוגים מהשרת, והרצת פונקציות עם בחירת רופא בזמן אמת מתוך מערכת ה-Staff החיצונית (שלב ג').
![Analytics](./DBProject_5786_3680_0282/שלב%20ה/screenshots/gui_screenshots/04_analytics.png)
