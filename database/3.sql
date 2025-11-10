-- Accuracy Tracking Database Schema
-- Add these tables to track prediction accuracy

USE stock_prediction_db;

-- 1. Create prediction_accuracy table to store actual vs predicted comparisons
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

-- 2. Create model_performance table to track overall model statistics
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

-- 3. Create user_accuracy_stats table for user-specific statistics
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

-- 4. Add columns to existing predictions table (safe version)
-- Check and add columns one by one

-- Add confidence_score
SET @col_exists = 0;
SELECT COUNT(*) INTO @col_exists 
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_SCHEMA = 'stock_prediction_db' 
  AND TABLE_NAME = 'predictions' 
  AND COLUMN_NAME = 'confidence_score';

SET @query = IF(@col_exists = 0,
    'ALTER TABLE predictions ADD COLUMN confidence_score DECIMAL(5, 2) DEFAULT NULL AFTER predicted_values',
    'SELECT "confidence_score column already exists" AS info');
PREPARE stmt FROM @query;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Add prediction_status
SET @col_exists = 0;
SELECT COUNT(*) INTO @col_exists 
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_SCHEMA = 'stock_prediction_db' 
  AND TABLE_NAME = 'predictions' 
  AND COLUMN_NAME = 'prediction_status';

SET @query = IF(@col_exists = 0,
    'ALTER TABLE predictions ADD COLUMN prediction_status ENUM("pending", "verified", "expired") DEFAULT "pending" AFTER confidence_score',
    'SELECT "prediction_status column already exists" AS info');
PREPARE stmt FROM @query;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Add verification_date
SET @col_exists = 0;
SELECT COUNT(*) INTO @col_exists 
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_SCHEMA = 'stock_prediction_db' 
  AND TABLE_NAME = 'predictions' 
  AND COLUMN_NAME = 'verification_date';

SET @query = IF(@col_exists = 0,
    'ALTER TABLE predictions ADD COLUMN verification_date TIMESTAMP NULL DEFAULT NULL AFTER prediction_status',
    'SELECT "verification_date column already exists" AS info');
PREPARE stmt FROM @query;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 5. Create stored procedure to calculate accuracy
DELIMITER $$

CREATE PROCEDURE IF NOT EXISTS calculate_prediction_accuracy(
    IN pred_id INT
)
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

-- 6. Create view for accuracy dashboard
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

-- 7. Create view for model leaderboard
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

-- 8. Create view for user leaderboard
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

-- 9. Insert sample data for testing (optional)
-- You can uncomment these lines after running your first prediction

-- Sample accuracy tracking
/*
INSERT INTO prediction_accuracy 
(prediction_id, user_id, stock_symbol, prediction_date, target_date, predicted_price, actual_price, model_used, confidence_score)
VALUES 
(1, 1, 'RELIANCE.NS', '2025-01-01', '2025-01-08', 2500.00, 2478.50, 'LSTM', 85.5),
(2, 1, 'TCS.NS', '2025-01-01', '2025-01-08', 3800.00, 3825.75, 'Random Forest', 78.3);
*/

-- Verify tables were created
SHOW TABLES LIKE '%accuracy%';
SHOW TABLES LIKE '%performance%';

-- Show structure of new tables
DESCRIBE prediction_accuracy;
DESCRIBE model_performance;
DESCRIBE user_accuracy_stats;

SELECT '✅ Accuracy tracking schema created successfully!' AS status;