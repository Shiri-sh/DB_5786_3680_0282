-- =============================================
-- 1. DIAGNOSTIC_EQUIPMENT
-- =============================================
CREATE TABLE DIAGNOSTIC_EQUIPMENT (
    equipment_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    equipment_name TEXT NOT NULL,
    department_id INT NOT NULL,
    maintenance_date DATE NOT NULL
);

-- =============================================
-- 2. LAB_TEST
-- =============================================
CREATE TABLE LAB_TEST (
    test_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    test_name TEXT NOT NULL,
    description TEXT,
    normal_range TEXT,
    cost DECIMAL(10, 2) NOT NULL,
    equipment_id INT,
    sample_type TEXT,
    CONSTRAINT fk_test_equipment 
        FOREIGN KEY (equipment_id) 
        REFERENCES DIAGNOSTIC_EQUIPMENT(equipment_id)
        ON DELETE SET NULL
);

-- =============================================
-- 3. LAB_ORDER
-- =============================================
CREATE TABLE LAB_ORDER (
    lab_order_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    visit_id INT NOT NULL,
    doctor_id INT NOT NULL,
    order_date DATE NOT NULL DEFAULT CURRENT_DATE,
    status TEXT NOT NULL,
    priority TEXT NOT NULL,
    
    CONSTRAINT chk_status CHECK (status IN ('ORDERED', 'IN_PROGRESS', 'COMPLETED')),
    CONSTRAINT chk_priority CHECK (priority IN ('NORMAL', 'URGENT'))
);

-- =============================================
-- 4. LAB_TECHNICIAN
-- =============================================
CREATE TABLE LAB_TECHNICIAN (
    technician_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    staff_id INT NOT NULL,
    certification TEXT NOT NULL
);

-- =============================================
-- 5. LAB_ORDER_TEST
-- =============================================
CREATE TABLE LAB_ORDER_TEST (
    lab_order_test_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    lab_order_id INT NOT NULL,
    test_id INT NOT NULL,
    
    CONSTRAINT fk_lot_order 
        FOREIGN KEY (lab_order_id) 
        REFERENCES LAB_ORDER(lab_order_id) 
        ON DELETE CASCADE,
    CONSTRAINT fk_lot_test 
        FOREIGN KEY (test_id) 
        REFERENCES LAB_TEST(test_id) 
        ON DELETE RESTRICT
);

-- =============================================
-- 6. LAB_RESULT
-- =============================================
CREATE TABLE LAB_RESULT (
    result_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    lab_order_test_id INT NOT NULL UNIQUE, -- הבטחת תוצאה אחת לכל שורת הזמנה
    technician_id INT NOT NULL,
    result_value TEXT NOT NULL,
    result_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_result_order_test 
        FOREIGN KEY (lab_order_test_id) 
        REFERENCES LAB_ORDER_TEST(lab_order_test_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_result_technician 
        FOREIGN KEY (technician_id) 
        REFERENCES LAB_TECHNICIAN(technician_id)
);