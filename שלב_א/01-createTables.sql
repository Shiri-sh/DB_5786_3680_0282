-- =========================
-- LAB_ORDER
-- =========================
CREATE TABLE LAB_ORDER (
    lab_order_id INT PRIMARY KEY,
    visit_id INT NOT NULL,
    doctor_id INT NOT NULL,
    order_date DATE NOT NULL,
    status VARCHAR(20) NOT NULL,
    priority VARCHAR(20) NOT NULL,

    CONSTRAINT chk_status CHECK (status IN ('ORDERED', 'IN_PROGRESS', 'COMPLETED')),
    CONSTRAINT chk_priority CHECK (priority IN ('NORMAL', 'URGENT'))
);

-- =========================
-- LAB_TEST
-- =========================
CREATE TABLE LAB_TEST (
    test_id INT PRIMARY KEY,
    test_name VARCHAR(100) NOT NULL,
    description VARCHAR(255),
    normal_range VARCHAR(50),
    cost NUMERIC(10,2) NOT NULL,
    sample_type VARCHAR(50)
);

-- =========================
-- DIAGNOSTIC_EQUIPMENT
-- =========================
CREATE TABLE DIAGNOSTIC_EQUIPMENT (
    equipment_id INT PRIMARY KEY,
    equipment_name VARCHAR(100) NOT NULL,
    department_id INT NOT NULL,
    maintenance_date DATE NOT NULL
);

-- =========================
-- LAB_TECHNICIAN
-- =========================
CREATE TABLE LAB_TECHNICIAN (
    technician_id INT PRIMARY KEY,
    staff_id INT NOT NULL,
    certification VARCHAR(100) NOT NULL
);

-- =========================
-- LAB_ORDER_TEST (קשר)
-- =========================
CREATE TABLE LAB_ORDER_TEST (
    lab_order_test_id INT PRIMARY KEY,
    lab_order_id INT NOT NULL,
    test_id INT NOT NULL,

    FOREIGN KEY (lab_order_id) REFERENCES LAB_ORDER(lab_order_id),
    FOREIGN KEY (test_id) REFERENCES LAB_TEST(test_id)
);

-- =========================
-- LAB_RESULT
-- =========================
CREATE TABLE LAB_RESULT (
    result_id INT PRIMARY KEY,
    lab_order_test_id INT UNIQUE NOT NULL,
    technician_id INT NOT NULL,
    result_value VARCHAR(100) NOT NULL,
    result_date DATE NOT NULL,

    FOREIGN KEY (lab_order_test_id) REFERENCES LAB_ORDER_TEST(lab_order_test_id),
    FOREIGN KEY (technician_id) REFERENCES LAB_TECHNICIAN(technician_id)
);