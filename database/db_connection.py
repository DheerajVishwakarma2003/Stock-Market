import mysql.connector
from mysql.connector import Error
import os

def get_db_connection():
    """
    Create and return a MySQL database connection
    Configure these values in environment variables for production
    """
    try:
        # Try to load from environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'stock_prediction_db'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            charset='utf8mb4',
            use_unicode=True
        )
        
        if connection.is_connected():
            return connection
    
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def initialize_database():
    """
    Initialize database and create tables if they don't exist
    Run this once during setup
    """
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', 'your_password_here')
        )
        
        cursor = connection.cursor()
        
        # Create database if not exists
        cursor.execute("CREATE DATABASE IF NOT EXISTS stock_prediction_db")
        cursor.execute("USE stock_prediction_db")
        
        # Create users table with is_admin field
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                is_admin BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_email (email),
                INDEX idx_is_admin (is_admin)
            )
        """)
        
        # Create predictions table
        cursor.execute("""
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
            )
        """)
        
        connection.commit()
        print("Database initialized successfully!")
        print("\nTo create an admin user, run:")
        print("  python create_admin.py")
        
        cursor.close()
        connection.close()
    
    except Error as e:
        print(f"Error initializing database: {e}")

if __name__ == "__main__":
    # Run this file directly to initialize the database
    initialize_database()