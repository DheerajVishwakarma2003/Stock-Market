"""
Quick Start Script for Stock Market Prediction System
Run this after setting up database and dependencies
"""

import os
import sys

def check_dependencies():
    """Check if all required packages are installed"""
    print("Checking dependencies...")
    required_packages = [
        'flask', 'pandas', 'numpy', 'sklearn', 
        'tensorflow', 'matplotlib', 'yfinance', 'mysql'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} - MISSING")
            missing.append(package)
    
    if missing:
        print(f"\n❌ Missing packages: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("\n✓ All dependencies installed!\n")
    return True

def check_directories():
    """Ensure all required directories exist"""
    print("Checking directories...")
    dirs = [
        'static/css', 'static/js', 'static/plots',
        'templates', 'model', 'utils', 'database'
    ]
    
    for directory in dirs:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created: {directory}")
        else:
            print(f"✓ {directory}")
    
    print("\n✓ All directories ready!\n")
    return True

def check_database():
    """Check database connection"""
    print("Checking database connection...")
    try:
        from database.db_connection import get_db_connection
        conn = get_db_connection()
        
        if conn:
            print("✓ Database connected successfully!")
            conn.close()
            return True
        else:
            print("✗ Database connection failed")
            print("\nPlease check:")
            print("1. MySQL server is running")
            print("2. Database credentials in .env file are correct")
            print("3. Database 'stock_prediction_db' exists")
            return False
    
    except Exception as e:
        print(f"✗ Database error: {e}")
        return False

def test_stock_fetch():
    """Test stock data fetching"""
    print("\nTesting stock data fetch...")
    try:
        from utils.data_fetch import fetch_stock_data
        data = fetch_stock_data("AAPL", period="1mo")
        
        if data is not None and not data.empty:
            print(f"✓ Successfully fetched {len(data)} records for AAPL")
            return True
        else:
            print("✗ Failed to fetch stock data")
            print("Check your internet connection")
            return False
    
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def create_env_file():
    """Create .env file if it doesn't exist"""
    if not os.path.exists('.env'):
        print("\n⚠ .env file not found. Creating from template...")
        
        env_content = """# Database Configuration
DB_HOST=localhost
DB_NAME=stock_prediction_db
DB_USER=root
DB_PASSWORD=your_password_here

# Flask Configuration
SECRET_KEY=change_this_to_random_secret_key
FLASK_ENV=development
FLASK_DEBUG=True
"""
        
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("✓ Created .env file")
        print("⚠ IMPORTANT: Edit .env and set your MySQL password!")
        return False
    
    return True

def run_setup():
    """Run complete setup check"""
    print("="*60)
    print("  Stock Market Prediction System - Setup Check")
    print("="*60 + "\n")
    
    checks = [
        ("Environment File", create_env_file),
        ("Directories", check_directories),
        ("Dependencies", check_dependencies),
        ("Database", check_database),
        ("Stock Data API", test_stock_fetch),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append(result)
            print()
        except Exception as e:
            print(f"✗ {name} check failed: {e}\n")
            results.append(False)
    
    print("="*60)
    
    if all(results):
        print("✅ All checks passed! System is ready.")
        print("\nTo start the application, run:")
        print("  python app.py")
        print("\nThen open: http://localhost:5000")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("1. Edit .env file with correct database password")
        print("2. Run: pip install -r requirements.txt")
        print("3. Start MySQL server")
        print("4. Run: python database/db_connection.py")
    
    print("="*60)

if __name__ == "__main__":
    run_setup()