"""
Login Debugging and Testing Script
Run this to diagnose login issues
"""

from werkzeug.security import generate_password_hash, check_password_hash
from database.db_connection import get_db_connection
import sys

def test_database_connection():
    """Test if database connection works"""
    print("=" * 60)
    print("Testing Database Connection")
    print("=" * 60)
    
    conn = get_db_connection()
    if conn:
        print("✓ Database connection successful!")
        
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM users")
        result = cursor.fetchone()
        print(f"✓ Found {result[0]} users in database")
        
        cursor.close()
        conn.close()
        return True
    else:
        print("✗ Database connection failed!")
        print("\nPlease check:")
        print("1. MySQL server is running")
        print("2. Database 'stock_prediction_db' exists")
        print("3. Credentials in .env file are correct")
        return False

def list_users():
    """List all users in database"""
    print("\n" + "=" * 60)
    print("Listing All Users")
    print("=" * 60)
    
    conn = get_db_connection()
    if not conn:
        print("✗ Cannot connect to database")
        return
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, username, email, created_at FROM users")
    users = cursor.fetchall()
    
    if users:
        print(f"\nFound {len(users)} user(s):\n")
        for user in users:
            print(f"ID: {user['id']}")
            print(f"Username: {user['username']}")
            print(f"Email: {user['email']}")
            print(f"Created: {user['created_at']}")
            print("-" * 40)
    else:
        print("No users found in database!")
        print("Please register a user first.")
    
    cursor.close()
    conn.close()

def create_test_user():
    """Create a test user for login testing"""
    print("\n" + "=" * 60)
    print("Creating Test User")
    print("=" * 60)
    
    test_email = "test@example.com"
    test_password = "test123"
    test_username = "testuser"
    
    conn = get_db_connection()
    if not conn:
        print("✗ Cannot connect to database")
        return
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Check if user already exists
        cursor.execute("SELECT * FROM users WHERE email = %s", (test_email,))
        existing = cursor.fetchone()
        
        if existing:
            print(f"⚠ User with email {test_email} already exists!")
            print(f"Username: {existing['username']}")
            return
        
        # Create new user
        hashed_password = generate_password_hash(test_password, method='pbkdf2:sha256')
        
        cursor.execute(
            "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
            (test_username, test_email, hashed_password)
        )
        conn.commit()
        
        print("✓ Test user created successfully!")
        print(f"\nLogin credentials:")
        print(f"Email: {test_email}")
        print(f"Password: {test_password}")
        print("\nUse these to test login on the website.")
        
    except Exception as e:
        print(f"✗ Error creating user: {e}")
    
    finally:
        cursor.close()
        conn.close()

def test_password_verification(email=None):
    """Test password hashing and verification"""
    print("\n" + "=" * 60)
    print("Testing Password Verification")
    print("=" * 60)
    
    if not email:
        email = input("\nEnter email to test: ").strip()
    
    password = input("Enter password to verify: ").strip()
    
    conn = get_db_connection()
    if not conn:
        print("✗ Cannot connect to database")
        return
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        
        if not user:
            print(f"✗ No user found with email: {email}")
            return
        
        print(f"\n✓ User found:")
        print(f"Username: {user['username']}")
        print(f"Email: {user['email']}")
        
        # Test password
        if check_password_hash(user['password'], password):
            print("\n✓ Password is CORRECT!")
            print("Login should work with these credentials.")
        else:
            print("\n✗ Password is INCORRECT!")
            print("This password does not match the stored hash.")
            
    except Exception as e:
        print(f"✗ Error: {e}")
    
    finally:
        cursor.close()
        conn.close()

def reset_user_password(email=None):
    """Reset password for a user"""
    print("\n" + "=" * 60)
    print("Reset User Password")
    print("=" * 60)
    
    if not email:
        email = input("\nEnter email to reset password: ").strip()
    
    new_password = input("Enter new password: ").strip()
    
    if len(new_password) < 6:
        print("✗ Password must be at least 6 characters!")
        return
    
    conn = get_db_connection()
    if not conn:
        print("✗ Cannot connect to database")
        return
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Check if user exists
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        
        if not user:
            print(f"✗ No user found with email: {email}")
            return
        
        # Update password
        hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256')
        cursor.execute(
            "UPDATE users SET password = %s WHERE email = %s",
            (hashed_password, email)
        )
        conn.commit()
        
        print("\n✓ Password reset successfully!")
        print(f"\nNew credentials:")
        print(f"Email: {email}")
        print(f"Password: {new_password}")
        print("\nYou can now login with these credentials.")
        
    except Exception as e:
        print(f"✗ Error: {e}")
    
    finally:
        cursor.close()
        conn.close()

def main_menu():
    """Main menu for testing"""
    while True:
        print("\n" + "=" * 60)
        print("  Login Debugging Menu")
        print("=" * 60)
        print("\n1. Test Database Connection")
        print("2. List All Users")
        print("3. Create Test User (test@example.com / test123)")
        print("4. Test Password Verification")
        print("5. Reset User Password")
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == '1':
            test_database_connection()
        elif choice == '2':
            list_users()
        elif choice == '3':
            create_test_user()
        elif choice == '4':
            test_password_verification()
        elif choice == '5':
            reset_user_password()
        elif choice == '6':
            print("\nGoodbye!")
            sys.exit(0)
        else:
            print("\n✗ Invalid choice. Please try again.")

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  Stock Market Prediction - Login Debug Tool")
    print("=" * 60)
    
    # First, test database connection
    if test_database_connection():
        main_menu()
    else:
        print("\n✗ Cannot proceed without database connection.")
        print("Please fix the database connection issue first.")