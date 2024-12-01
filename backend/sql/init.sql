CREATE DATABASE IF NOT EXISTS very_important_company_db;
USE very_important_company_db;


CREATE TABLE employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50),
    password VARCHAR(50), 
    email VARCHAR(100),
    salary INT,
    ssn VARCHAR(11),  
    bank_account VARCHAR(20),  
    department VARCHAR(50)
);

CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    price DECIMAL(10,2),
    description TEXT,
    stock INT,
    supplier_id INT,
    cost_price DECIMAL(10,2)  
);

CREATE TABLE customer_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(20),
    address TEXT,
    credit_card_number VARCHAR(16),  
    credit_card_cvv VARCHAR(4),      
    purchase_history TEXT
);

CREATE TABLE financial_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    transaction_date DATE,
    amount DECIMAL(10,2),
    transaction_type VARCHAR(50),
    account_number VARCHAR(20),
    description TEXT
);

INSERT INTO employees (username, password, email, salary, ssn, bank_account, department) VALUES
('admin', 'admin123', 'admin@company.com', 100000, '123-45-6789', 'BA123456789', 'Executive'),
('john_doe', 'password123', 'john@company.com', 65000, '987-65-4321', 'BA987654321', 'Sales'),
('jane_smith', 'jane456', 'jane@company.com', 70000, '456-78-9123', 'BA456789123', 'IT'),
('bob_wilson', 'bob789', 'bob@company.com', 55000, '789-12-3456', 'BA789123456', 'Marketing');

INSERT INTO products (name, price, description, stock, supplier_id, cost_price) VALUES
('Laptop Pro X', 1299.99, 'High-performance laptop', 50, 1, 899.99),
('SmartPhone Y', 699.99, 'Latest smartphone model', 100, 2, 449.99),
('Tablet Z', 499.99, 'Premium tablet device', 75, 1, 299.99),
('Wireless Earbuds', 149.99, 'Premium wireless earbuds', 200, 3, 89.99);

INSERT INTO customer_data (name, email, phone, address, credit_card_number, credit_card_cvv, purchase_history) VALUES
('Alice Johnson', 'alice@email.com', '555-0101', '123 Main St', '4532123456789012', '123', 'Laptop Pro X, SmartPhone Y'),
('Bob Brown', 'bob@email.com', '555-0102', '456 Oak Ave', '4532987654321098', '456', 'Tablet Z'),
('Carol White', 'carol@email.com', '555-0103', '789 Pine Rd', '4532456789012345', '789', 'Wireless Earbuds'),
('David Lee', 'david@email.com', '555-0104', '321 Elm St', '4532890123456789', '321', 'SmartPhone Y, Wireless Earbuds');

INSERT INTO financial_records (transaction_date, amount, transaction_type, account_number, description) VALUES
('2024-01-01', 50000.00, 'PAYMENT', 'AC123456', 'Supplier payment'),
('2024-01-02', 25000.00, 'RECEIPT', 'AC789012', 'Customer payment'),
('2024-01-03', 35000.00, 'PAYMENT', 'AC345678', 'Inventory purchase'),
('2024-01-04', 45000.00, 'RECEIPT', 'AC901234', 'Bulk order payment');


CREATE USER IF NOT EXISTS 'web_user'@'%' IDENTIFIED BY 'password123';
GRANT ALL PRIVILEGES ON very_important_company_db.* TO 'web_user'@'%';
GRANT SELECT ON mysql.* TO 'web_user'@'%';
GRANT PROCESS ON *.* TO 'web_user'@'%';
GRANT SHOW DATABASES ON *.* TO 'web_user'@'%';
GRANT FILE ON *.* TO 'web_user'@'%';
GRANT SUPER ON *.* TO 'web_user'@'%';


CREATE USER IF NOT EXISTS 'target'@'%' IDENTIFIED BY 'password123';
GRANT ALL PRIVILEGES ON *.* TO 'target'@'%' WITH GRANT OPTION;
GRANT SELECT ON mysql.* TO 'target'@'%';
GRANT PROCESS ON *.* TO 'target'@'%';
GRANT FILE ON *.* TO 'target'@'%';
GRANT SHOW DATABASES ON *.* TO 'target'@'%';
GRANT SUPER ON *.* TO 'target'@'%';
GRANT CREATE USER ON *.* TO 'target'@'%';
GRANT RELOAD ON *.* TO 'target'@'%';

FLUSH PRIVILEGES;