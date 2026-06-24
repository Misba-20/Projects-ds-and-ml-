-- Create database
CREATE DATABASE IF NOT EXISTS nutrismart_ai;
USE nutrismart_ai;

-- =========================================================
-- USERS TABLE
-- =========================================================
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fullname VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(15),
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =========================================================
-- USER PROFILE TABLE
-- =========================================================
CREATE TABLE IF NOT EXISTS user_profile (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    age INT,
    gender VARCHAR(20),
    height FLOAT,
    weight FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- =========================================================
-- HEALTH PROFILES TABLE
-- =========================================================
CREATE TABLE IF NOT EXISTS health_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    age INT,
    gender VARCHAR(20),
    height FLOAT,
    weight FLOAT,
    bmi FLOAT,
    diseases TEXT,
    allergies TEXT,
    goal VARCHAR(100),
    lifestyle VARCHAR(100),
    food_preference VARCHAR(100),
    main_region VARCHAR(100),
    sub_region VARCHAR(100),
    water_intake FLOAT,
    sleep_hours FLOAT,
    activity_level VARCHAR(100),
    calorie_requirement INT,
    risk_level VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- =========================================================
-- ADMINS TABLE
-- =========================================================
CREATE TABLE IF NOT EXISTS admins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fullname VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =========================================================
-- DISEASES TABLE
-- =========================================================
CREATE TABLE IF NOT EXISTS diseases (
    id INT AUTO_INCREMENT PRIMARY KEY,
    disease_name VARCHAR(100) NOT NULL,
    description TEXT,
    foods_to_eat TEXT,
    foods_to_avoid TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =========================================================
-- ALLERGIES TABLE
-- =========================================================
CREATE TABLE IF NOT EXISTS allergies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    allergy_name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =========================================================
-- REGIONS TABLE
-- =========================================================
CREATE TABLE IF NOT EXISTS regions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    main_region VARCHAR(100) NOT NULL,
    sub_region VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =========================================================
-- FOODS TABLE
-- =========================================================
CREATE TABLE IF NOT EXISTS foods (
    id INT AUTO_INCREMENT PRIMARY KEY,
    food_name VARCHAR(150) NOT NULL,
    calories INT,
    protein DECIMAL(10,2),
    carbs DECIMAL(10,2),
    fat DECIMAL(10,2),
    fiber DECIMAL(10,2),
    food_category VARCHAR(100),
    suitable_disease VARCHAR(255),
    suitable_goal VARCHAR(255),
    food_preference VARCHAR(100),
    region VARCHAR(100),
    image VARCHAR(255),
    diet_type VARCHAR(100),
    meal_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =========================================================
-- MEAL PLANS TABLE
-- =========================================================
CREATE TABLE IF NOT EXISTS meal_plans (
    id INT AUTO_INCREMENT PRIMARY KEY,
    meal_name VARCHAR(150) NOT NULL,
    breakfast TEXT,
    lunch TEXT,
    dinner TEXT,
    snacks TEXT,
    target_goal VARCHAR(100),
    disease VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =========================================================
-- NUTRITION LOGS TABLE
-- =========================================================
CREATE TABLE IF NOT EXISTS nutrition_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    food_name VARCHAR(100),
    calories INT,
    protein DECIMAL(5,2),
    carbs DECIMAL(5,2),
    fat DECIMAL(5,2),
    log_date DATE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- =========================================================
-- WATER LOGS TABLE
-- =========================================================
CREATE TABLE IF NOT EXISTS water_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    glasses INT,
    log_date DATE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- =========================================================
-- WEIGHT LOGS TABLE
-- =========================================================
CREATE TABLE IF NOT EXISTS weight_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    weight DECIMAL(5,2),
    log_date DATE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- =========================================================
-- CHATBOT HISTORY TABLE
-- =========================================================
CREATE TABLE IF NOT EXISTS chatbot_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    question TEXT,
    answer TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- =========================================================
-- NOTIFICATIONS TABLE
-- =========================================================
CREATE TABLE IF NOT EXISTS notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255),
    message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =========================================================
-- ADMIN LOGS TABLE
-- =========================================================
CREATE TABLE IF NOT EXISTS admin_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    admin_id INT,
    action_performed VARCHAR(255),
    log_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (admin_id) REFERENCES admins(id) ON DELETE SET NULL
);

-- =========================================================
-- DEFAULT ADMIN
-- =========================================================
INSERT INTO admins (fullname, email, password) 
VALUES ('Administrator', 'admin@nutrismart.com', 
'pbkdf2:sha256:600000$1ZjZcK2vDcojTjIB$bef0e7cd60ed0c8e505ce10f970021e04a87d76d7d1352e9875bb5bbfb11cfc7');

-- =========================================================
-- SAMPLE FOOD DATA
-- =========================================================
INSERT INTO foods (food_name, calories, protein, carbs, fat, fiber, food_category, suitable_disease, region, diet_type, meal_type) VALUES
('Ragi Dosa', 180, 6, 32, 2, 4, 'Breakfast', 'Diabetes', 'Tamil Nadu', 'Diabetes Diet', 'Breakfast'),
('Oats', 150, 5, 27, 3, 4, 'Breakfast', 'Diabetes', 'Tamil Nadu', 'Diabetes Diet', 'Breakfast'),
('Brown Rice', 220, 5, 45, 2, 3, 'Lunch', 'Diabetes', 'Tamil Nadu', 'Diabetes Diet', 'Lunch'),
('Sprouts', 80, 7, 12, 1, 3, 'Snacks', 'None', 'India', 'Diabetes Diet', 'Snacks'),
('Millet Chapati', 200, 6, 38, 3, 4, 'Dinner', 'Diabetes', 'India', 'Diabetes Diet', 'Dinner'),
('Paneer', 280, 18, 8, 20, 1, 'Protein', 'None', 'India', 'High Protein Diet', 'Lunch'),
('Banana Shake', 350, 12, 55, 8, 2, 'Weight Gain', 'None', 'India', 'High Protein Diet', 'Breakfast'),
('Vegetable Soup', 90, 3, 10, 1, 3, 'Weight Loss', 'None', 'India', 'Low Calorie Diet', 'Lunch'),
('Grilled Chicken', 250, 30, 0, 12, 0, 'High Protein', 'None', 'India', 'High Protein Diet', 'Dinner'),
('Quinoa Bowl', 220, 8, 30, 5, 6, 'Healthy', 'None', 'India', 'Heart Healthy Diet', 'Lunch');