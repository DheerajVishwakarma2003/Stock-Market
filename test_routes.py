"""
Quick script to test if all routes are properly registered
Run this to verify your Flask app routes
"""

def test_routes():
    """Test if all required routes exist in app.py"""
    
    required_routes = [
        '/',
        '/register',
        '/login',
        '/logout',
        '/dashboard',
        '/predict',
        '/news',
        '/api/stock-news/<stock_symbol>',
        '/api/market-summary',
        '/admin'
    ]
    
    print("="*60)
    print("Flask Routes Checker")
    print("="*60)
    
    try:
        from app import app
        
        print("\nRegistered Routes:")
        print("-"*60)
        
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append(str(rule))
            print(f"✓ {rule}")
        
        print("\n" + "="*60)
        print("Route Verification:")
        print("="*60)
        
        # Check each required route
        all_good = True
        for route in required_routes:
            # Handle dynamic routes
            route_check = route.replace('<stock_symbol>', '')
            found = any(route_check in str(r) for r in app.url_map.iter_rules())
            
            if found:
                print(f"✓ {route}")
            else:
                print(f"✗ {route} - MISSING!")
                all_good = False
        
        print("\n" + "="*60)
        if all_good:
            print("✅ All routes are properly registered!")
            print("Your Flask app is ready to run.")
        else:
            print("❌ Some routes are missing!")
            print("Check your app.py file.")
        print("="*60)
        
        return all_good
        
    except ImportError as e:
        print(f"\n❌ Error importing app.py: {e}")
        print("\nMake sure:")
        print("1. You're in the correct directory")
        print("2. app.py exists")
        print("3. All imports in app.py are working")
        return False
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_routes()