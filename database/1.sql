-- Simple Profile & Settings Schema Update
-- Run this in MySQL to add profile columns to users table

USE stock_prediction_db;

-- Add columns one by one (safer approach)

-- Profile picture
ALTER TABLE users ADD COLUMN profile_picture VARCHAR(255) DEFAULT NULL;

-- Phone number
ALTER TABLE users ADD COLUMN phone VARCHAR(20) DEFAULT NULL;

-- Favorite stocks (stored as JSON text)
ALTER TABLE users ADD COLUMN favorite_stocks TEXT DEFAULT NULL;

-- Default exchange preference
ALTER TABLE users ADD COLUMN default_exchange VARCHAR(10) DEFAULT 'NSE';

-- Language preference
ALTER TABLE users ADD COLUMN language VARCHAR(5) DEFAULT 'en';

-- Timezone
ALTER TABLE users ADD COLUMN timezone VARCHAR(50) DEFAULT 'Asia/Kolkata';

-- Theme preference
ALTER TABLE users ADD COLUMN theme VARCHAR(20) DEFAULT 'light';

-- Chart style
ALTER TABLE users ADD COLUMN chart_style VARCHAR(20) DEFAULT 'line';

-- Email notification preferences
ALTER TABLE users ADD COLUMN email_predictions TINYINT(1) DEFAULT 1;
ALTER TABLE users ADD COLUMN email_price_alerts TINYINT(1) DEFAULT 1;
ALTER TABLE users ADD COLUMN email_market_news TINYINT(1) DEFAULT 0;
ALTER TABLE users ADD COLUMN email_weekly_report TINYINT(1) DEFAULT 0;

-- Last login timestamp
ALTER TABLE users ADD COLUMN last_login TIMESTAMP NULL DEFAULT NULL;

-- Updated timestamp
ALTER TABLE users ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;

-- Add indexes for better performance
CREATE INDEX idx_profile_picture ON users(profile_picture);
CREATE INDEX idx_theme ON users(theme);
CREATE INDEX idx_last_login ON users(last_login);

-- Verify the changes
DESCRIBE users;

-- Show sample data
SELECT 
    id, 
    username, 
    email, 
    theme,
    language,
    default_exchange
FROM users 
LIMIT 3;

-- Success message
SELECT 'All profile columns added successfully! You can now use the profile page.' AS message;