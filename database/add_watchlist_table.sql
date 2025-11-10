-- Add Watchlist Table to Existing Database
-- Run this if you already have the database set up

USE stock_prediction_db;

-- Create watchlist table
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

-- Verify table was created
DESCRIBE watchlist;

-- Show all tables
SHOW TABLES;

SELECT 'Watchlist table created successfully!' as message;