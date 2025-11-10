"""
Create Admin User Script
Run this to create an admin user or make existing user admin
"""

from werkzeug.security import generate_password_hash
from database.db_connection import get_db_connection
import sys

def create_admin_user(username, email, password):
    """Create a new admin user"""
    conn = get_db_connection()
    if not conn:
        print("❌ Database connection failed!")
        return False
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Check if user already exists
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            print(f"⚠️  User with email {email} already exists!")
            response = input("Make this user admin? (yes/no): ")
            if response.lower() == 'yes':
                cursor.execute("UPDATE users SET is_admin = TRUE WHERE email = %s", (email,))
                conn.commit()
                print(f"✅ User {email} is now an admin!")
                return True
            else:
                print("❌ Operation cancelled.")
                return False
        
        # Hash password
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        
        # Create admin user
        cursor.execute(
            "INSERT INTO users (username, email, password, is_admin) VALUES (%s, %s, %s, TRUE)",
            (username, email, hashed_password)
        )
        conn.commit()
        
        print("\n" + "="*60)
        print("✅ Admin user created successfully!")
        print("="*60)
        print(f"Username: {username}")
        print(f"Email: {email}")
        print(f"Password: {password}")
        print(f"Admin: Yes")
        print("="*60)
        print("\n⚠️  IMPORTANT: Change the password after first login!")
        print("You can now login with these credentials.\n")
        
        return True
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    finally:
        cursor.close()
        conn.close()

def make_user_admin(email):
    """Make an existing user an admin"""
    conn = get_db_connection()
    if not conn:
        print("❌ Database connection failed!")
        return False
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Check if user exists
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        
        if not user:
            print(f"❌ No user found with email: {email}")
            return False
        
        if user.get('is_admin'):
            print(f"ℹ️  User {email} is already an admin!")
            return True
        
        # Make admin
        cursor.execute("UPDATE users SET is_admin = TRUE WHERE email = %s", (email,))
        conn.commit()
        
        print(f"✅ User {email} ({user['username']}) is now an admin!")
        return True
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    finally:
        cursor.close()
        conn.close()

def list_admins():
    """List all admin users"""
    conn = get_db_connection()
    if not conn:
        print("❌ Database connection failed!")
        return
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT username, email, created_at FROM users WHERE is_admin = TRUE")
        admins = cursor.fetchall()
        
        if not admins:
            print("ℹ️  No admin users found.")
            return
        
        print("\n" + "="*60)
        print("Admin Users:")
        print("="*60)
        for admin in admins:
            print(f"Username: {admin['username']}")
            print(f"Email: {admin['email']}")
            print(f"Created: {admin['created_at']}")
            print("-"*60)
    
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        cursor.close()
        conn.close()

def remove_admin(email):
    """Remove admin privileges from a user"""
    conn = get_db_connection()
    if not conn:
        print("❌ Database connection failed!")
        return False
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        
        if not user:
            print(f"❌ No user found with email: {email}")
            return False
        
        if not user.get('is_admin'):
            print(f"ℹ️  User {email} is not an admin!")
            return True
        
        cursor.execute("UPDATE users SET is_admin = FALSE WHERE email = %s", (email,))
        conn.commit()
        
        print(f"✅ Admin privileges removed from {email}")
        return True
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    finally:
        cursor.close()
        conn.close()

def interactive_menu():
    """Interactive menu for admin management"""
    while True:
        print("\n" + "="*60)
        print("Admin User Management")
        print("="*60)
        print("1. Create new admin user")
        print("2. Make existing user admin")
        print("3. List all admins")
        print("4. Remove admin privileges")
        print("5. Exit")
        print("="*60)
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == '1':
            print("\n--- Create New Admin User ---")
            username = input("Username: ").strip()
            email = input("Email: ").strip()
            password = input("Password: ").strip()
            
            if username and email and password:
                create_admin_user(username, email, password)
            else:
                print("❌ All fields are required!")
        
        elif choice == '2':
            print("\n--- Make Existing User Admin ---")
            email = input("User email: ").strip()
            if email:
                make_user_admin(email)
            else:
                print("❌ Email is required!")
        
        elif choice == '3':
            list_admins()
        
        elif choice == '4':
            print("\n--- Remove Admin Privileges ---")
            email = input("User email: ").strip()
            if email:
                confirm = input(f"Remove admin from {email}? (yes/no): ")
                if confirm.lower() == 'yes':
                    remove_admin(email)
            else:
                print("❌ Email is required!")
        
        elif choice == '5':
            print("\nGoodbye!")
            sys.exit(0)
        
        else:
            print("❌ Invalid choice. Please try again.")

def quick_setup():
    """Quick setup to create default admin"""
    print("\n" + "="*60)
    print("Quick Admin Setup")
    print("="*60)
    print("This will create a default admin user.")
    print("Email: admin@stockpredictor.com")
    print("Password: admin123")
    print("\n⚠️  IMPORTANT: Change this password after first login!")
    print("="*60)
    
    response = input("\nCreate default admin? (yes/no): ")
    if response.lower() == 'yes':
        create_admin_user('admin', 'admin@stockpredictor.com', 'admin123')
    else:
        print("Setup cancelled.")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("Stock Market Prediction System - Admin Management")
    print("="*60)
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'quick':
            quick_setup()
        elif sys.argv[1] == 'list':
            list_admins()
        else:
            print("Usage:")
            print("  python create_admin.py          - Interactive menu")
            print("  python create_admin.py quick    - Quick setup")
            print("  python create_admin.py list     - List admins")
    else:
        interactive_menu()