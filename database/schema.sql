-- Stock Market Prediction System Database Schema
-- Run this SQL script to create the database and tables

-- Create database
CREATE DATABASE IF NOT EXISTS stock_prediction_db;
USE stock_prediction_db;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_is_admin (is_admin)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Predictions table
CREATE TABLE IF NOT EXISTS predictions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    stock_symbol VARCHAR(20) NOT NULL,
    prediction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    predicted_values JSON,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_stock_symbol (stock_symbol),
    INDEX idx_prediction_date (prediction_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Watchlist table (NEW)
CREATE TABLE IF NOT EXISTS watchlist (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    stock_symbol VARCHAR(20) NOT NULL,
    stock_name VARCHAR(100),
    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    alert_price DECIMAL(10, 2) DEFAULT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_stock (user_id, stock_symbol),
    INDEX idx_user_id (user_id),
    INDEX idx_stock_symbol (stock_symbol)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create default admin user (password: admin123)
-- Note: Change this password in production!
INSERT INTO users (username, email, password, is_admin) VALUES 
('admin', 'admin@stockpredictor.com', 'pbkdf2:sha256:600000$8zrKxHqY$a8f0c3d5e8b4a9c0f1d2e3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4', TRUE)
ON DUPLICATE KEY UPDATE is_admin = TRUE;

-- Display tables
SHOW TABLES;

-- Display table structures
DESCRIBE users;
DESCRIBE predictions;
DESCRIBE watchlist;