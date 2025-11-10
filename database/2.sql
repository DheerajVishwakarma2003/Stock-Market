-- Check existing columns and add only missing ones
-- Safe to run multiple times - won't cause duplicate column errors

USE stock_prediction_db;

-- First, let's see what columns we have
SELECT 'Current columns in users table:' AS info;
SHOW COLUMNS FROM users;

-- Add columns only if they don't exist (MySQL 5.7+ syntax)
-- If you get errors, it means the column already exists - that's OK!

-- Profile picture (probably exists)
SET @col_exists = 0;
SELECT COUNT(*) INTO @col_exists 
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_SCHEMA = 'stock_prediction_db' 
  AND TABLE_NAME = 'users' 
  AND COLUMN_NAME = 'profile_picture';

SET @query = IF(@col_exists = 0,
    'ALTER TABLE users ADD COLUMN profile_picture VARCHAR(255) DEFAULT NULL',
    'SELECT "profile_picture column already exists" AS info');
PREPARE stmt FROM @query;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Phone (probably exists)
SET @col_exists = 0;
SELECT COUNT(*) INTO @col_exists 
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_SCHEMA = 'stock_prediction_db' 
  AND TABLE_NAME = 'users' 
  AND COLUMN_NAME = 'phone';

SET @query = IF(@col_exists = 0,
    'ALTER TABLE users ADD COLUMN phone VARCHAR(20) DEFAULT NULL',
    'SELECT "phone column already exists" AS info');
PREPARE stmt FROM @query;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Favorite stocks
SET @col_exists = 0;
SELECT COUNT(*) INTO @col_exists 
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_SCHEMA = 'stock_prediction_db' 
  AND TABLE_NAME = 'users' 
  AND COLUMN_NAME = 'favorite_stocks';

SET @query = IF(@col_exists = 0,
    'ALTER TABLE users ADD COLUMN favorite_stocks TEXT DEFAULT NULL',
    'SELECT "favorite_stocks column already exists" AS info');
PREPARE stmt FROM @query;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Default exchange
SET @col_exists = 0;
SELECT COUNT(*) INTO @col_exists 
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_SCHEMA = 'stock_prediction_db' 
  AND TABLE_NAME = 'users' 
  AND COLUMN_NAME = 'default_exchange';

SET @query = IF(@col_exists = 0,
    'ALTER TABLE users ADD COLUMN default_exchange VARCHAR(10) DEFAULT "NSE"',
    'SELECT "default_exchange column already exists" AS info');
PREPARE stmt FROM @query;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Language
SET @col_exists = 0;
SELECT COUNT(*) INTO @col_exists 
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_SCHEMA = 'stock_prediction_db' 
  AND TABLE_NAME = 'users' 
  AND COLUMN_NAME = 'language';

SET @query = IF(@col_exists = 0,
    'ALTER TABLE users ADD COLUMN language VARCHAR(5) DEFAULT "en"',
    'SELECT "language column already exists" AS info');
PREPARE stmt FROM @query;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Timezone
SET @col_exists = 0;
SELECT COUNT(*) INTO @col_exists 
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_SCHEMA = 'stock_prediction_db' 
  AND TABLE_NAME = 'users' 
  AND COLUMN_NAME = 'timezone';

SET @query = IF(@col_exists = 0,
    'ALTER TABLE users ADD COLUMN timezone VARCHAR(50) DEFAULT "Asia/Kolkata"',
    'SELECT "timezone column already exists" AS info');
PREPARE stmt FROM @query;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Theme
SET @col_exists = 0;
SELECT COUNT(*) INTO @col_exists 
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_SCHEMA = 'stock_prediction_db' 
  AND TABLE_NAME = 'users' 
  AND COLUMN_NAME = 'theme';

SET @query = IF(@col_exists = 0,
    'ALTER TABLE users ADD COLUMN theme VARCHAR(20) DEFAULT "light"',
    'SELECT "theme column already exists" AS info');
PREPARE stmt FROM @query;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Chart style
SET @col_exists = 0;
SELECT COUNT(*) INTO @col_exists 
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_SCHEMA = 'stock_prediction_db' 
  AND TABLE_NAME = 'users' 
  AND COLUMN_NAME = 'chart_style';

SET @query = IF(@col_exists = 0,
    'ALTER TABLE users ADD COLUMN chart_style VARCHAR(20) DEFAULT "line"',
    'SELECT "chart_style column already exists" AS info');
PREPARE stmt FROM @query;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Email preferences
SET @col_exists = 0;
SELECT COUNT(*) INTO @col_exists 
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_SCHEMA = 'stock_prediction_db' 
  AND TABLE_NAME = 'users' 
  AND COLUMN_NAME = 'email_predictions';

SET @query = IF(@col_exists = 0,
    'ALTER TABLE users ADD COLUMN email_predictions TINYINT(1) DEFAULT 1',
    'SELECT "email_predictions column already exists" AS info');
PREPARE stmt FROM @query;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @col_exists = 0;
SELECT COUNT(*) INTO @col_exists 
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_SCHEMA = 'stock_prediction_db' 
  AND TABLE_NAME = 'users' 
  AND COLUMN_NAME = 'email_price_alerts';

SET @query = IF(@col_exists = 0,
    'ALTER TABLE users ADD COLUMN email_price_alerts TINYINT(1) DEFAULT 1',
    'SELECT "email_price_alerts column already exists" AS info');
PREPARE stmt FROM @query;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @col_exists = 0;
SELECT COUNT(*) INTO @col_exists 
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_SCHEMA = 'stock_prediction_db' 
  AND TABLE_NAME = 'users' 
  AND COLUMN_NAME = 'email_market_news';

SET @query = IF(@col_exists = 0,
    'ALTER TABLE users ADD COLUMN email_market_news TINYINT(1) DEFAULT 0',
    'SELECT "email_market_news column already exists" AS info');
PREPARE stmt FROM @query;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @col_exists = 0;
SELECT COUNT(*) INTO @col_exists 
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_SCHEMA = 'stock_prediction_db' 
  AND TABLE_NAME = 'users' 
  AND COLUMN_NAME = 'email_weekly_report';

SET @query = IF(@col_exists = 0,
    'ALTER TABLE users ADD COLUMN email_weekly_report TINYINT(1) DEFAULT 0',
    'SELECT "email_weekly_report column already exists" AS info');
PREPARE stmt FROM @query;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Last login
SET @col_exists = 0;
SELECT COUNT(*) INTO @col_exists 
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_SCHEMA = 'stock_prediction_db' 
  AND TABLE_NAME = 'users' 
  AND COLUMN_NAME = 'last_login';

SET @query = IF(@col_exists = 0,
    'ALTER TABLE users ADD COLUMN last_login TIMESTAMP NULL DEFAULT NULL',
    'SELECT "last_login column already exists" AS info');
PREPARE stmt FROM @query;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Updated at
SET @col_exists = 0;
SELECT COUNT(*) INTO @col_exists 
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_SCHEMA = 'stock_prediction_db' 
  AND TABLE_NAME = 'users' 
  AND COLUMN_NAME = 'updated_at';

SET @query = IF(@col_exists = 0,
    'ALTER TABLE users ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP',
    'SELECT "updated_at column already exists" AS info');
PREPARE stmt FROM @query;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Show final structure
SELECT 'Final users table structure:' AS info;
DESCRIBE users;

-- Show a sample user with new fields
SELECT 'Sample user data:' AS info;
SELECT 
    id, 
    username, 
    email,
    profile_picture,
    phone,
    theme,
    language,
    default_exchange,
    created_at
FROM users 
LIMIT 1;

SELECT '✅ Database schema check complete!' AS status;