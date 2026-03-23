import random
from datetime import datetime, timedelta

# הגדרות כלליות
NUM_RECORDS = 20000
FOREIGN_KEY_LIMIT = 500  # הנחנו שיש 500 רשומות בטבלאות האב (בדיקות, טכנאים, הזמנות)

def generate_random_date():
    start_date = datetime(2023, 1, 1)
    random_days = random.randint(0, 700)
    return (start_date + timedelta(days=random_days)).strftime('%Y-%m-%d')

# רשימת ערכים אפשריים לתוצאות
result_values = [
    '75 mg/dL', '120/80 mmHg', 'Negative', 'Positive', '5.2 mmol/L', 
    '14.1 g/dL', 'Normal', 'Abnormal - High', 'Abnormal - Low', 'Trace'
]

# יצירת קובץ עבור LAB_ORDER_TEST
with open('insert_order_tests.sql', 'w', encoding='utf-8') as f_order_test:
    f_order_test.write("-- 20,000 records for LAB_ORDER_TEST\n")
    
    # יצירת קובץ עבור LAB_RESULT (במקביל כדי לשמור על עקביות ה-ID)
    with open('insert_results.sql', 'w', encoding='utf-8') as f_result:
        f_result.write("-- 20,000 records for LAB_RESULT\n")
        
        for i in range(1, NUM_RECORDS + 1):
            # --- נתונים ל-LAB_ORDER_TEST ---
            lab_order_test_id = i
            lab_order_id = random.randint(1, FOREIGN_KEY_LIMIT)
            test_id = random.randint(1, FOREIGN_KEY_LIMIT)
            
            sql_order_test = f"INSERT INTO LAB_ORDER_TEST (lab_order_test_id, lab_order_id, test_id) VALUES ({lab_order_test_id}, {lab_order_id}, {test_id});\n"
            f_order_test.write(sql_order_test)
            
            # --- נתונים ל-LAB_RESULT ---
            result_id = i
            # כאן אנחנו משתמשים ב-lab_order_test_id שיצרנו הרגע כדי שלא תהיה שגיאת Foreign Key
            technician_id = random.randint(1, FOREIGN_KEY_LIMIT)
            val = random.choice(result_values)
            res_date = generate_random_date()
            
            sql_result = f"INSERT INTO LAB_RESULT (result_id, lab_order_test_id, technician_id, result_value, result_date) VALUES ({result_id}, {lab_order_test_id}, {technician_id}, '{val}', '{res_date}');\n"
            f_result.write(sql_result)

print("Finished! Created 'insert_order_tests.sql' and 'insert_results.sql' with 20,000 rows each.")