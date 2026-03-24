import random
from datetime import datetime, timedelta

NUM_TESTS = 500
NUM_RECORDS = 20000
FOREIGN_KEY_LIMIT = 500  # עבור LAB_ORDER ו-LAB_TECHNICIAN

# -----------------------------
# מילון בדיקות → תוצאות הגיוניות
# -----------------------------
test_data = {
    "Complete Blood Count": ["4.5 x10^9/L", "5.2 x10^9/L", "Low", "High"],
    "Glucose Test": ["70 mg/dL", "95 mg/dL", "120 mg/dL", "High"],
    "Lipid Panel": ["Normal", "High Cholesterol", "Low HDL", "High LDL"],
    "Thyroid Function": ["TSH Normal", "TSH High", "TSH Low"],
    "Liver Function Test": ["Normal", "Elevated ALT", "Elevated AST"],
    "Hemoglobin A1c": ["5.4%", "6.2%", "7.1%", "High"],
    "Urinalysis": ["Normal", "Trace Protein", "Infection Detected"],
    "Electrolyte Panel": ["Normal", "Low Sodium", "High Potassium"],
    "Vitamin D Test": ["30 ng/mL", "20 ng/mL", "Deficient"],
    "Kidney Function Test": ["Normal", "Elevated Creatinine", "Reduced GFR"]
}

test_names = list(test_data.keys())

# -----------------------------
# פונקציות עזר
# -----------------------------
def generate_random_date():
    start_date = datetime(2023, 1, 1)
    return (start_date + timedelta(days=random.randint(0, 700))).strftime('%Y-%m-%d')

def random_cost():
    return round(random.uniform(50, 500), 2)

def random_sample_type():
    return random.choice(["Blood", "Urine", "Saliva"])

# -----------------------------
# יצירת LAB_TEST (500 רשומות)
# -----------------------------
test_mapping = {}  # test_id → test_name

with open('insert_lab_test.sql', 'w', encoding='utf-8') as f_test:
    f_test.write("-- 500 records for LAB_TEST\n")

    for i in range(1, NUM_TESTS + 1):
        test_name = random.choice(test_names)
        test_mapping[i] = test_name

        description = f"{test_name} description"
        normal_range = "Normal"
        cost = random_cost()
        sample = random_sample_type()

        sql = f"""INSERT INTO LAB_TEST 
(test_id, test_name, description, normal_range, cost, sample_type)
VALUES ({i}, '{test_name}', '{description}', '{normal_range}', {cost}, '{sample}');
"""
        f_test.write(sql)

# -----------------------------
# יצירת LAB_ORDER_TEST + LAB_RESULT
# -----------------------------
with open('insert_order_tests.sql', 'w', encoding='utf-8') as f_order_test, \
     open('insert_results.sql', 'w', encoding='utf-8') as f_result:

    f_order_test.write("-- 20,000 records for LAB_ORDER_TEST\n")
    f_result.write("-- 20,000 records for LAB_RESULT\n")

    for i in range(1, NUM_RECORDS + 1):

        # קשרים
        lab_order_test_id = i
        lab_order_id = random.randint(1, FOREIGN_KEY_LIMIT)
        test_id = random.randint(1, NUM_TESTS)

        # INSERT LAB_ORDER_TEST
        f_order_test.write(
            f"INSERT INTO LAB_ORDER_TEST (lab_order_test_id, lab_order_id, test_id) "
            f"VALUES ({lab_order_test_id}, {lab_order_id}, {test_id});\n"
        )

        # התאמת תוצאה לפי סוג בדיקה
        test_name = test_mapping[test_id]
        result_value = random.choice(test_data[test_name])

        technician_id = random.randint(1, FOREIGN_KEY_LIMIT)
        result_date = generate_random_date()

        # INSERT LAB_RESULT
        f_result.write(
            f"INSERT INTO LAB_RESULT (result_id, lab_order_test_id, technician_id, result_value, result_date) "
            f"VALUES ({i}, {lab_order_test_id}, {technician_id}, '{result_value}', '{result_date}');\n"
        )

print("✅ Done! Generated LAB_TEST (500), LAB_ORDER_TEST & LAB_RESULT (20,000 each)")