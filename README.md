# CRMS - Campus Resource Management System

A premium, role-based web application designed to streamline the management, booking, and maintenance of campus resources like computer labs, seminar halls, and A/V equipment. 

Built with a sleek, responsive holographic glassmorphism UI, this system provides specialized portals for Students, Staff, Department Heads (HODs), and System Admins.

## ✨ Key Features

* **Role-Based Access Control (RBAC):** Different dashboards and permissions for Students, Staff, HODs, and Admins.
* **Resource Booking Engine:** Users can request specific time slots for resources, including a required "purpose" for the booking to prevent conflicts.
* **Global Campus Schedule:** A transparent, anonymized view of all upcoming bookings to help users avoid scheduling conflicts.
* **Issue Reporting System:** Users can report maintenance issues (e.g., broken projectors), which Admins can track and resolve.
* **HOD Approval Pipeline:** Department heads get a dedicated queue to approve or reject resource requests from their department.
* **Premium UI/UX:** A modern glassmorphic interface with a seamless, user-specific Dark/Light Mode toggle that saves to local storage.

## 🛠️ Technology Stack

* **Backend:** Python, Flask, Flask-Session
* **Database:** MySQL (flask_mysqldb)
* **Frontend:** HTML5, CSS3 (CSS Variables for Theming), Vanilla JavaScript
* **Security:** Werkzeug Password Hashing

---

## 🗄️ Database Structure (MySQL)

To set up the database from scratch, run the following SQL commands in your MySQL client or phpMyAdmin.

```sql
-- Create the Database
CREATE DATABASE crms;
USE crms;

-- 1. Department Table
CREATE TABLE department (
    department_id INT AUTO_INCREMENT PRIMARY KEY,
    department_name VARCHAR(100) NOT NULL UNIQUE
);

-- Insert Default Departments
INSERT INTO department (department_name) VALUES 
('Computer Science'), ('Artificial Intelligence'), ('Civil Engineering'), 
('Data Science'), ('Electrical Engineering'), ('Electronics and Communication'), 
('Information Technology'), ('Mechanical Engineering');

-- 2. Users Table
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role ENUM('student', 'staff', 'hod', 'admin') DEFAULT 'student',
    department_id INT,
    FOREIGN KEY (department_id) REFERENCES department(department_id)
);

-- 3. Resources Table
CREATE TABLE resources (
    resource_id INT AUTO_INCREMENT PRIMARY KEY,
    resource_name VARCHAR(100) NOT NULL,
    resource_type ENUM('Lab', 'Equipment', 'Venue') NOT NULL,
    status ENUM('available', 'maintenance') DEFAULT 'available',
    department_id INT,
    FOREIGN KEY (department_id) REFERENCES department(department_id)
);

-- 4. Bookings Table (Includes 'purpose' column)
CREATE TABLE bookings (
    booking_id INT AUTO_INCREMENT PRIMARY KEY,
    booking_date DATE NOT NULL,
    time_slot VARCHAR(50) NOT NULL,
    purpose VARCHAR(255) NOT NULL,
    user_id INT,
    resource_id INT,
    department_id INT,
    status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
    approved_by INT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (resource_id) REFERENCES resources(resource_id),
    FOREIGN KEY (department_id) REFERENCES department(department_id),
    FOREIGN KEY (approved_by) REFERENCES users(user_id)
);

-- 5. Issues Table
CREATE TABLE issues (
    issue_id INT AUTO_INCREMENT PRIMARY KEY,
    resource_id INT NULL,
    reported_by INT,
    department_id INT,
    description TEXT NOT NULL,
    status ENUM('open', 'resolved') DEFAULT 'open',
    FOREIGN KEY (resource_id) REFERENCES resources(resource_id),
    FOREIGN KEY (reported_by) REFERENCES users(user_id),
    FOREIGN KEY (department_id) REFERENCES department(department_id)
);
Markdown
# CRMS - Campus Resource Management System

A premium, role-based web application designed to streamline the management, booking, and maintenance of campus resources like computer labs, seminar halls, and A/V equipment. 

Built with a sleek, responsive holographic glassmorphism UI, this system provides specialized portals for Students, Staff, Department Heads (HODs), and System Admins.

## ✨ Key Features

* **Role-Based Access Control (RBAC):** Different dashboards and permissions for Students, Staff, HODs, and Admins.
* **Resource Booking Engine:** Users can request specific time slots for resources, including a required "purpose" for the booking to prevent conflicts.
* **Global Campus Schedule:** A transparent, anonymized view of all upcoming bookings to help users avoid scheduling conflicts.
* **Issue Reporting System:** Users can report maintenance issues (e.g., broken projectors), which Admins can track and resolve.
* **HOD Approval Pipeline:** Department heads get a dedicated queue to approve or reject resource requests from their department.
* **Premium UI/UX:** A modern glassmorphic interface with a seamless, user-specific Dark/Light Mode toggle that saves to local storage.

## 🛠️ Technology Stack

* **Backend:** Python, Flask, Flask-Session
* **Database:** MySQL (flask_mysqldb)
* **Frontend:** HTML5, CSS3 (CSS Variables for Theming), Vanilla JavaScript
* **Security:** Werkzeug Password Hashing

---

## 🗄️ Database Structure (MySQL)

To set up the database from scratch, run the following SQL commands in your MySQL client or phpMyAdmin.

```sql
-- Create the Database
CREATE DATABASE crms;
USE crms;

-- 1. Department Table
CREATE TABLE department (
    department_id INT AUTO_INCREMENT PRIMARY KEY,
    department_name VARCHAR(100) NOT NULL UNIQUE
);

-- Insert Default Departments
INSERT INTO department (department_name) VALUES 
('Computer Science'), ('Artificial Intelligence'), ('Civil Engineering'), 
('Data Science'), ('Electrical Engineering'), ('Electronics and Communication'), 
('Information Technology'), ('Mechanical Engineering');

-- 2. Users Table
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role ENUM('student', 'staff', 'hod', 'admin') DEFAULT 'student',
    department_id INT,
    FOREIGN KEY (department_id) REFERENCES department(department_id)
);

-- 3. Resources Table
CREATE TABLE resources (
    resource_id INT AUTO_INCREMENT PRIMARY KEY,
    resource_name VARCHAR(100) NOT NULL,
    resource_type ENUM('Lab', 'Equipment', 'Venue') NOT NULL,
    status ENUM('available', 'maintenance') DEFAULT 'available',
    department_id INT,
    FOREIGN KEY (department_id) REFERENCES department(department_id)
);

-- 4. Bookings Table (Includes 'purpose' column)
CREATE TABLE bookings (
    booking_id INT AUTO_INCREMENT PRIMARY KEY,
    booking_date DATE NOT NULL,
    time_slot VARCHAR(50) NOT NULL,
    purpose VARCHAR(255) NOT NULL,
    user_id INT,
    resource_id INT,
    department_id INT,
    status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
    approved_by INT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (resource_id) REFERENCES resources(resource_id),
    FOREIGN KEY (department_id) REFERENCES department(department_id),
    FOREIGN KEY (approved_by) REFERENCES users(user_id)
);

-- 5. Issues Table
CREATE TABLE issues (
    issue_id INT AUTO_INCREMENT PRIMARY KEY,
    resource_id INT NULL,
    reported_by INT,
    department_id INT,
    description TEXT NOT NULL,
    status ENUM('open', 'resolved') DEFAULT 'open',
    FOREIGN KEY (resource_id) REFERENCES resources(resource_id),
    FOREIGN KEY (reported_by) REFERENCES users(user_id),
    FOREIGN KEY (department_id) REFERENCES department(department_id)
);
🚀 Setup & Installation
Install Dependencies:
Make sure you have Python installed. Then install the required libraries:

Bash
pip install Flask Flask-MySQLdb Werkzeug
Database Configuration:

Open XAMPP/WAMP or your MySQL command line.

Run the SQL schema provided above.

Open app.py and verify your database password matches line 11.

Run the Application:

Bash
python app.py
Access the Portal:
Go to http://127.0.0.1:5000/ in your web browser.
