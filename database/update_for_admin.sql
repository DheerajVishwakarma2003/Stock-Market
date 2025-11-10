-- Quick update script to add admin functionality to existing database
-- Run this if you already have the database set up

USE stock_prediction_db;

-- Add is_admin column to users table
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS is_admin BOOLEAN DEFAULT FALSE AFTER password;

-- Add index for performance
ALTER TABLE users 
ADD INDEX IF NOT EXISTS idx_is_admin (is_admin);

-- Verify the column was added
DESCRIBE users;

-- Show current users
SELECT id, username, email, is_admin, created_at FROM users;

-- Instructions to make a user admin:
-- UPDATE users SET is_admin = TRUE WHERE email = 'your_email@example.com';

COMMIT;