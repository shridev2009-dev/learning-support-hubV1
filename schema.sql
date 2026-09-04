-- Learning Support Hub - Database Schema
-- Run this in MySQL before starting the Flask app

CREATE DATABASE IF NOT EXISTS learning_hub;
USE learning_hub;

-- Student table
CREATE TABLE student (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    class VARCHAR(20)
);

-- Teacher table
CREATE TABLE teachers (
    teacher_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

-- Material table (uploaded by teacher, teacher login is hardcoded so no teacher_id FK)
CREATE TABLE material (
    material_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(150) NOT NULL,
    subject VARCHAR(50),
    content TEXT,
    uploaded_by VARCHAR(100),
    upload_date DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Quiz table (linked to a material/module)
CREATE TABLE quiz (
    quiz_id INT AUTO_INCREMENT PRIMARY KEY,
    material_id INT NOT NULL,
    question VARCHAR(255) NOT NULL,
    option_a VARCHAR(100),
    option_b VARCHAR(100),
    option_c VARCHAR(100),
    option_d VARCHAR(100),
    correct_answer CHAR(1),
    FOREIGN KEY (material_id) REFERENCES material(material_id) ON DELETE CASCADE
);

-- Progress table (tracks student quiz attempts)
CREATE TABLE progress (
    progress_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    quiz_id INT NOT NULL,
    score INT,
    date_attempted DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES student(student_id) ON DELETE CASCADE,
    FOREIGN KEY (quiz_id) REFERENCES quiz(quiz_id) ON DELETE CASCADE
);
