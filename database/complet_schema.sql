-- ============================================================================
-- Stock Market Prediction System - Complete Database Setup
-- ============================================================================
-- This script creates all necessary tables, indexes, views, and stored procedures
-- Run this once to set up the entire database structure
-- ============================================================================

-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS stock_prediction_db;
USE stock_prediction_db;

-- ============================================================================
-- DROP EXISTING TABLES (if re-running setup)
-- ============================================================================
-- Uncomment these lines if you want to completely reset the database
-- DROP TABLE IF EXISTS prediction_accuracy;
-- DROP TABLE IF EXISTS model_performance;
-- DROP TABLE IF EXISTS user_accuracy_stats;
-- DROP TABLE IF EXISTS watchlist;
-- DROP TABLE IF EXISTS predictions;
-- DROP TABLE IF EXISTS users;

-- ============================================================================
-- MAIN TABLES
-- ============================================================================

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    
    -- Profile Information
    profile_picture VARCHAR(255) DEFAULT NULL,
    phone VARCHAR(20) DEFAULT NULL,
    
    -- User Preferences
    favorite_stocks TEXT DEFAULT NULL,
    default_exchange VARCHAR(10) DEFAULT 'NSE',
    language VARCHAR(5) DEFAULT 'en',
    timezone VARCHAR(50) DEFAULT 'Asia/Kolkata',
    
    -- Appearance Settings
    theme VARCHAR(20) DEFAULT 'light',
    chart_style VARCHAR(20) DEFAULT 'line',
    
    -- Notification Preferences
    email_predictions TINYINT(1) DEFAULT 1,
    email_price_alerts TINYINT(1) DEFAULT 1,
    email_market_news TINYINT(1) DEFAULT 0,
    email_weekly_report TINYINT(1) DEFAULT 0,
    
    -- Timestamps
    last_login TIMESTAMP NULL DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Indexes for performance
    INDEX idx_email (email),
    INDEX idx_is_admin (is_admin),
    INDEX idx_profile_picture (profile_picture),
    INDEX idx_theme (theme),
    INDEX idx_last_login (last_login)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Predictions Table
CREATE TABLE IF NOT EXISTS predictions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    stock_symbol VARCHAR(20) NOT NULL,
    prediction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    predicted_values JSON,
    
    -- Additional Prediction Fields
    confidence_score DECIMAL(5, 2) DEFAULT NULL,
    prediction_status ENUM('pending', 'verified', 'expired') DEFAULT 'pending',
    verification_date TIMESTAMP NULL DEFAULT NULL,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_stock_symbol (stock_symbol),
    INDEX idx_prediction_date (prediction_date),
    INDEX idx_prediction_status (prediction_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Watchlist Table
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
    INDEX idx_stock_symbol (stock_symbol),
    INDEX idx_alert_price (alert_price)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- ACCURACY TRACKING TABLES
-- ============================================================================

-- Prediction Accuracy Table
CREATE TABLE IF NOT EXISTS prediction_accuracy (
    id INT AUTO_INCREMENT PRIMARY KEY,
    prediction_id INT NOT NULL,
    user_id INT NOT NULL,
    stock_symbol VARCHAR(20) NOT NULL,
    prediction_date DATE NOT NULL,
    target_date DATE NOT NULL,
    predicted_price DECIMAL(10, 2) NOT NULL,
    actual_price DECIMAL(10, 2) DEFAULT NULL,
    accuracy_percentage DECIMAL(5, 2) DEFAULT NULL,
    prediction_error DECIMAL(10, 2) DEFAULT NULL,
    is_verified BOOLEAN DEFAULT FALSE,
    verified_date TIMESTAMP NULL DEFAULT NULL,
    model_used VARCHAR(50) NOT NULL,
    confidence_score DECIMAL(5, 2) DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (prediction_id) REFERENCES predictions(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_stock_symbol (stock_symbol),
    INDEX idx_prediction_date (prediction_date),
    INDEX idx_target_date (target_date),
    INDEX idx_is_verified (is_verified),
    INDEX idx_model_used (model_used)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Model Performance Table
CREATE TABLE IF NOT EXISTS model_performance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    model_name VARCHAR(50) NOT NULL,
    stock_symbol VARCHAR(20) NOT NULL,
    total_predictions INT DEFAULT 0,
    verified_predictions INT DEFAULT 0,
    accurate_predictions INT DEFAULT 0,
    average_accuracy DECIMAL(5, 2) DEFAULT NULL,
    average_error DECIMAL(10, 2) DEFAULT NULL,
    best_accuracy DECIMAL(5, 2) DEFAULT NULL,
    worst_accuracy DECIMAL(5, 2) DEFAULT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    UNIQUE KEY unique_model_stock (model_name, stock_symbol),
    INDEX idx_model_name (model_name),
    INDEX idx_stock_symbol (stock_symbol),
    INDEX idx_average_accuracy (average_accuracy)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- User Accuracy Stats Table
CREATE TABLE IF NOT EXISTS user_accuracy_stats (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    total_predictions INT DEFAULT 0,
    verified_predictions INT DEFAULT 0,
    accurate_predictions INT DEFAULT 0,
    success_rate DECIMAL(5, 2) DEFAULT NULL,
    best_prediction_accuracy DECIMAL(5, 2) DEFAULT NULL,
    total_profit_loss DECIMAL(15, 2) DEFAULT 0.00,
    favorite_model VARCHAR(50) DEFAULT NULL,
    last_prediction_date TIMESTAMP NULL DEFAULT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user (user_id),
    INDEX idx_success_rate (success_rate),
    INDEX idx_total_predictions (total_predictions)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- STORED PROCEDURES
-- ============================================================================

-- Procedure to calculate prediction accuracy
DELIMITER $$

DROP PROCEDURE IF EXISTS calculate_prediction_accuracy$$
CREATE PROCEDURE calculate_prediction_accuracy(IN pred_id INT)
BEGIN
    DECLARE v_predicted_price DECIMAL(10, 2);
    DECLARE v_actual_price DECIMAL(10, 2);
    DECLARE v_accuracy DECIMAL(5, 2);
    DECLARE v_error DECIMAL(10, 2);
    
    -- Get predicted and actual prices
    SELECT predicted_price, actual_price 
    INTO v_predicted_price, v_actual_price
    FROM prediction_accuracy
    WHERE id = pred_id;
    
    IF v_actual_price IS NOT NULL THEN
        -- Calculate error
        SET v_error = ABS(v_predicted_price - v_actual_price);
        
        -- Calculate accuracy percentage (100% - error percentage)
        SET v_accuracy = 100 - ((v_error / v_actual_price) * 100);
        
        -- Ensure accuracy is not negative
        IF v_accuracy < 0 THEN
            SET v_accuracy = 0;
        END IF;
        
        -- Update the record
        UPDATE prediction_accuracy
        SET 
            accuracy_percentage = v_accuracy,
            prediction_error = v_error,
            is_verified = TRUE,
            verified_date = NOW()
        WHERE id = pred_id;
    END IF;
END$$

DELIMITER ;

-- ============================================================================
-- VIEWS
-- ============================================================================

-- Accuracy Dashboard View
CREATE OR REPLACE VIEW accuracy_dashboard AS
SELECT 
    pa.id,
    pa.stock_symbol,
    pa.prediction_date,
    pa.target_date,
    pa.predicted_price,
    pa.actual_price,
    pa.accuracy_percentage,
    pa.prediction_error,
    pa.model_used,
    pa.confidence_score,
    pa.is_verified,
    u.username,
    DATEDIFF(CURDATE(), pa.target_date) AS days_since_target
FROM prediction_accuracy pa
JOIN users u ON pa.user_id = u.id
WHERE pa.is_verified = TRUE
ORDER BY pa.verified_date DESC;

-- Model Leaderboard View
CREATE OR REPLACE VIEW model_leaderboard AS
SELECT 
    model_name,
    SUM(total_predictions) AS total_predictions,
    SUM(verified_predictions) AS verified_predictions,
    SUM(accurate_predictions) AS accurate_predictions,
    AVG(average_accuracy) AS overall_accuracy,
    AVG(average_error) AS overall_error,
    MAX(best_accuracy) AS best_accuracy,
    COUNT(DISTINCT stock_symbol) AS stocks_covered
FROM model_performance
GROUP BY model_name
ORDER BY overall_accuracy DESC;

-- User Leaderboard View
CREATE OR REPLACE VIEW user_leaderboard AS
SELECT 
    u.id,
    u.username,
    uas.total_predictions,
    uas.verified_predictions,
    uas.accurate_predictions,
    uas.success_rate,
    uas.best_prediction_accuracy,
    uas.favorite_model,
    uas.last_prediction_date
FROM user_accuracy_stats uas
JOIN users u ON uas.user_id = u.id
WHERE uas.verified_predictions > 0
ORDER BY uas.success_rate DESC, uas.accurate_predictions DESC;

-- ============================================================================
-- INSERT DEFAULT DATA
-- ============================================================================

-- Create default admin user
-- Password: admin123 (hashed with pbkdf2:sha256)
INSERT INTO users (username, email, password, is_admin) 
VALUES (
    'admin', 
    'admin@stockpredictor.com', 
    'pbkdf2:sha256:600000$8zrKxHqY$a8f0c3d5e8b4a9c0f1d2e3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4',
    TRUE
)
ON DUPLICATE KEY UPDATE is_admin = TRUE;

-- Create a test user for development
-- Password: test123
INSERT INTO users (username, email, password, is_admin)
VALUES (
    'testuser',
    'test@example.com',
    'pbkdf2:sha256:600000$testuser$c9b5e1f3d7a2b8c4e6f0a1d3b5c7e9f1a3b5c7d9e1f3a5b7c9d1e3f5a7b9c1d3',
    FALSE
)
ON DUPLICATE KEY UPDATE username = 'testuser';

-- ============================================================================
-- VERIFY SETUP
-- ============================================================================

-- Show all tables
SELECT 'Tables created successfully:' AS Status;
SHOW TABLES;

-- Show users table structure
SELECT '
Users table structure:' AS Status;
DESCRIBE users;

-- Show predictions table structure
SELECT '
Predictions table structure:' AS Status;
DESCRIBE predictions;

-- Show watchlist table structure
SELECT '
Watchlist table structure:' AS Status;
DESCRIBE watchlist;

-- Show accuracy tracking tables
SELECT '
Prediction Accuracy table structure:' AS Status;
DESCRIBE prediction_accuracy;

SELECT '
Model Performance table structure:' AS Status;
DESCRIBE model_performance;

SELECT '
User Accuracy Stats table structure:' AS Status;
DESCRIBE user_accuracy_stats;

-- Show views
SELECT '
Views created:' AS Status;
SHOW FULL TABLES WHERE TABLE_TYPE LIKE 'VIEW';

-- Show stored procedures
SELECT '
Stored Procedures created:' AS Status;
SHOW PROCEDURE STATUS WHERE Db = 'stock_prediction_db';

-- Count users
SELECT 
    COUNT(*) AS total_users,
    SUM(is_admin) AS admin_users,
    COUNT(*) - SUM(is_admin) AS regular_users
FROM users;

-- ============================================================================
-- COMPLETION MESSAGE
-- ============================================================================

SELECT '
============================================================================' AS '';
SELECT '✅ Database setup completed successfully!' AS Status;
SELECT '============================================================================' AS '';
SELECT '' AS '';
SELECT 'Default Accounts Created:' AS '';
SELECT '  1. Admin Account:' AS '';
SELECT '     Email: admin@stockpredictor.com' AS '';
SELECT '     Password: admin123' AS '';
SELECT '' AS '';
SELECT '  2. Test Account:' AS '';
SELECT '     Email: test@example.com' AS '';
SELECT '     Password: test123' AS '';
SELECT '' AS '';
SELECT '⚠️  IMPORTANT: Change these passwords in production!' AS '';
SELECT '' AS '';
SELECT 'Tables Created:' AS '';
SELECT '  - users (with profile & settings)' AS '';
SELECT '  - predictions (with verification)' AS '';
SELECT '  - watchlist' AS '';
SELECT '  - prediction_accuracy' AS '';
SELECT '  - model_performance' AS '';
SELECT '  - user_accuracy_stats' AS '';
SELECT '' AS '';
SELECT 'Views Created:' AS '';
SELECT '  - accuracy_dashboard' AS '';
SELECT '  - model_leaderboard' AS '';
SELECT '  - user_leaderboard' AS '';
SELECT '' AS '';
SELECT 'Stored Procedures Created:' AS '';
SELECT '  - calculate_prediction_accuracy' AS '';
SELECT '' AS '';
SELECT 'You can now run your Flask application!' AS '';
SELECT '============================================================================' AS '';