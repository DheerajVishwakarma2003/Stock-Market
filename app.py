from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import json
import os

from utils.technical_indicators import TechnicalIndicators, analyze_stock_technical
import yfinance as yf
import pytz
from werkzeug.utils import secure_filename
from PIL import Image
import json

# Import custom modules
from database.db_connection import get_db_connection
from utils.data_fetch import fetch_stock_data
from utils.preprocess import preprocess_data
from model.train_model import train_and_predict
from utils.news_fetcher import get_all_news, get_market_summary, get_trending_stocks

app = Flask(__name__)
app.secret_key = 'your_secret_key_here_change_in_production'

# Create necessary directories
os.makedirs('static/plots', exist_ok=True)
os.makedirs('model', exist_ok=True)



UPLOAD_FOLDER = 'static/uploads/avatars'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max file size

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ============================================================================
# PROFILE & SETTINGS ROUTES
# ============================================================================

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("Warning: PIL not available. Avatar upload will work but without optimization.")

# Configuration for file uploads
UPLOAD_FOLDER = 'static/uploads/avatars'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('static/images', exist_ok=True)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ============================================================================
# PROFILE & SETTINGS ROUTES
# ============================================================================

@app.route('/profile')
def profile():
    """User profile and settings page"""
    if 'user_id' not in session:
        flash('Please login first!', 'warning')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    if not conn:
        flash('Database connection error!', 'danger')
        return redirect(url_for('dashboard'))
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Get user data
        cursor.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
        user_data = cursor.fetchone()
        
        if not user_data:
            flash('User not found!', 'danger')
            return redirect(url_for('dashboard'))
        
        # Get prediction count
        cursor.execute("SELECT COUNT(*) as count FROM predictions WHERE user_id = %s", (session['user_id'],))
        prediction_count = cursor.fetchone()['count']
        
        # Get watchlist count
        cursor.execute("SELECT COUNT(*) as count FROM watchlist WHERE user_id = %s", (session['user_id'],))
        watchlist_count = cursor.fetchone()['count']
        
        user_stats = {
            'predictions': prediction_count,
            'watchlist': watchlist_count
        }
        
        # Parse JSON fields safely
        if user_data.get('favorite_stocks'):
            try:
                user_data['favorite_stocks'] = json.loads(user_data['favorite_stocks'])
            except:
                user_data['favorite_stocks'] = []
        else:
            user_data['favorite_stocks'] = []
        
        return render_template('profile.html', user=user_data, user_stats=user_stats)
    
    except Exception as e:
        print(f"Profile error: {e}")
        import traceback
        traceback.print_exc()
        flash('Error loading profile!', 'danger')
        return redirect(url_for('dashboard'))
    
    finally:
        cursor.close()
        conn.close()

@app.route('/update-profile', methods=['POST'])
def update_profile():
    """Update user profile information"""
    if 'user_id' not in session:
        flash('Please login first!', 'warning')
        return redirect(url_for('login'))
    
    username = request.form.get('username', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()
    
    if not username or not email:
        flash('Username and email are required!', 'danger')
        return redirect(url_for('profile'))
    
    conn = get_db_connection()
    if not conn:
        flash('Database connection error!', 'danger')
        return redirect(url_for('profile'))
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Check if email is already taken by another user
        cursor.execute(
            "SELECT id FROM users WHERE email = %s AND id != %s",
            (email, session['user_id'])
        )
        
        if cursor.fetchone():
            flash('Email already in use by another account!', 'danger')
            return redirect(url_for('profile'))
        
        # Update user profile
        cursor.execute("""
            UPDATE users 
            SET username = %s, email = %s, phone = %s
            WHERE id = %s
        """, (username, email, phone if phone else None, session['user_id']))
        
        conn.commit()
        
        # Update session
        session['username'] = username
        session['email'] = email
        
        flash('✅ Profile updated successfully!', 'success')
        return redirect(url_for('profile'))
    
    except Exception as e:
        print(f"Error updating profile: {e}")
        flash('Error updating profile!', 'danger')
        return redirect(url_for('profile'))
    
    finally:
        cursor.close()
        conn.close()

@app.route('/update-preferences', methods=['POST'])
def update_preferences():
    """Update user preferences"""
    if 'user_id' not in session:
        flash('Please login first!', 'warning')
        return redirect(url_for('login'))
    
    favorite_stocks = request.form.get('favorite_stocks', '[]')
    default_exchange = request.form.get('default_exchange', 'NSE')
    language = request.form.get('language', 'en')
    timezone = request.form.get('timezone', 'Asia/Kolkata')
    
    # Validate JSON
    try:
        json.loads(favorite_stocks)
    except:
        favorite_stocks = '[]'
    
    conn = get_db_connection()
    if not conn:
        flash('Database connection error!', 'danger')
        return redirect(url_for('profile'))
    
    cursor = conn.cursor()
    
    try:
        # Check if columns exist, if not use basic update
        cursor.execute("SHOW COLUMNS FROM users LIKE 'favorite_stocks'")
        has_columns = cursor.fetchone()
        
        if has_columns:
            cursor.execute("""
                UPDATE users 
                SET favorite_stocks = %s, 
                    default_exchange = %s,
                    language = %s,
                    timezone = %s
                WHERE id = %s
            """, (favorite_stocks, default_exchange, language, timezone, session['user_id']))
        else:
            print("Warning: Profile columns don't exist. Please run the SQL schema update.")
            flash('Please update database schema first!', 'warning')
            return redirect(url_for('profile'))
        
        conn.commit()
        flash('✅ Preferences updated successfully!', 'success')
        return redirect(url_for('profile'))
    
    except Exception as e:
        print(f"Error updating preferences: {e}")
        import traceback
        traceback.print_exc()
        flash('Error updating preferences!', 'danger')
        return redirect(url_for('profile'))
    
    finally:
        cursor.close()
        conn.close()

@app.route('/update-appearance', methods=['POST'])
def update_appearance():
    """Update appearance settings"""
    if 'user_id' not in session:
        flash('Please login first!', 'warning')
        return redirect(url_for('login'))
    
    theme = request.form.get('theme', 'light')
    chart_style = request.form.get('chart_style', 'line')
    
    conn = get_db_connection()
    if not conn:
        flash('Database connection error!', 'danger')
        return redirect(url_for('profile'))
    
    cursor = conn.cursor()
    
    try:
        # Check if columns exist
        cursor.execute("SHOW COLUMNS FROM users LIKE 'theme'")
        has_columns = cursor.fetchone()
        
        if has_columns:
            cursor.execute("""
                UPDATE users 
                SET theme = %s, chart_style = %s
                WHERE id = %s
            """, (theme, chart_style, session['user_id']))
        else:
            print("Warning: Appearance columns don't exist. Please run the SQL schema update.")
            flash('Please update database schema first!', 'warning')
            return redirect(url_for('profile'))
        
        conn.commit()
        flash('✅ Appearance settings updated!', 'success')
        return redirect(url_for('profile'))
    
    except Exception as e:
        print(f"Error updating appearance: {e}")
        flash('Error updating appearance!', 'danger')
        return redirect(url_for('profile'))
    
    finally:
        cursor.close()
        conn.close()

@app.route('/change-password', methods=['POST'])
def change_password():
    """Change user password"""
    if 'user_id' not in session:
        flash('Please login first!', 'warning')
        return redirect(url_for('login'))
    
    current_password = request.form.get('current_password', '')
    new_password = request.form.get('new_password', '')
    confirm_password = request.form.get('confirm_password', '')
    
    if not current_password or not new_password or not confirm_password:
        flash('All password fields are required!', 'danger')
        return redirect(url_for('profile'))
    
    if new_password != confirm_password:
        flash('New passwords do not match!', 'danger')
        return redirect(url_for('profile'))
    
    if len(new_password) < 8:
        flash('Password must be at least 8 characters long!', 'danger')
        return redirect(url_for('profile'))
    
    conn = get_db_connection()
    if not conn:
        flash('Database connection error!', 'danger')
        return redirect(url_for('profile'))
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Verify current password
        cursor.execute("SELECT password FROM users WHERE id = %s", (session['user_id'],))
        user = cursor.fetchone()
        
        if not user or not check_password_hash(user['password'], current_password):
            flash('Current password is incorrect!', 'danger')
            return redirect(url_for('profile'))
        
        # Update password
        hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256')
        cursor.execute(
            "UPDATE users SET password = %s WHERE id = %s",
            (hashed_password, session['user_id'])
        )
        
        conn.commit()
        flash('✅ Password changed successfully!', 'success')
        return redirect(url_for('profile'))
    
    except Exception as e:
        print(f"Error changing password: {e}")
        flash('Error changing password!', 'danger')
        return redirect(url_for('profile'))
    
    finally:
        cursor.close()
        conn.close()

@app.route('/update-notifications', methods=['POST'])
def update_notifications():
    """Update notification preferences"""
    if 'user_id' not in session:
        flash('Please login first!', 'warning')
        return redirect(url_for('login'))
    
    email_predictions = 'email_predictions' in request.form
    email_price_alerts = 'email_price_alerts' in request.form
    email_market_news = 'email_market_news' in request.form
    email_weekly_report = 'email_weekly_report' in request.form
    
    conn = get_db_connection()
    if not conn:
        flash('Database connection error!', 'danger')
        return redirect(url_for('profile'))
    
    cursor = conn.cursor()
    
    try:
        # Check if columns exist
        cursor.execute("SHOW COLUMNS FROM users LIKE 'email_predictions'")
        has_columns = cursor.fetchone()
        
        if has_columns:
            cursor.execute("""
                UPDATE users 
                SET email_predictions = %s,
                    email_price_alerts = %s,
                    email_market_news = %s,
                    email_weekly_report = %s
                WHERE id = %s
            """, (email_predictions, email_price_alerts, email_market_news, 
                  email_weekly_report, session['user_id']))
        else:
            flash('Please update database schema first!', 'warning')
            return redirect(url_for('profile'))
        
        conn.commit()
        flash('✅ Notification preferences updated!', 'success')
        return redirect(url_for('profile'))
    
    except Exception as e:
        print(f"Error updating notifications: {e}")
        flash('Error updating notification preferences!', 'danger')
        return redirect(url_for('profile'))
    
    finally:
        cursor.close()
        conn.close()

@app.route('/upload-avatar', methods=['POST'])
def upload_avatar():
    """Upload profile picture"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login first'})
    
    if 'avatar' not in request.files:
        return jsonify({'success': False, 'message': 'No file uploaded'})
    
    file = request.files['avatar']
    
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'})
    
    if not allowed_file(file.filename):
        return jsonify({'success': False, 'message': 'Invalid file type. Use PNG, JPG, or GIF'})
    
    try:
        # Generate unique filename
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = secure_filename(f"user_{session['user_id']}_{int(datetime.now().timestamp())}.{ext}")
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        # Save file
        if PIL_AVAILABLE:
            # Open and optimize image with PIL
            img = Image.open(file)
            
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # Resize to 400x400 maintaining aspect ratio
            img.thumbnail((400, 400), Image.Resampling.LANCZOS)
            
            # Save optimized image
            img.save(filepath, 'JPEG', quality=85, optimize=True)
        else:
            # Simple save without optimization
            file.save(filepath)
        
        # Update database
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'Database error'})
        
        cursor = conn.cursor()
        
        profile_picture_path = f"uploads/avatars/{filename}"
        
        # Check if column exists
        cursor.execute("SHOW COLUMNS FROM users LIKE 'profile_picture'")
        has_column = cursor.fetchone()
        
        if has_column:
            cursor.execute(
                "UPDATE users SET profile_picture = %s WHERE id = %s",
                (profile_picture_path, session['user_id'])
            )
            conn.commit()
        else:
            print("Warning: profile_picture column doesn't exist")
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True, 
            'message': 'Profile picture updated successfully!',
            'url': url_for('static', filename=profile_picture_path)
        })
    
    except Exception as e:
        print(f"Error uploading avatar: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Upload failed: {str(e)}'})
    
# ============================================================================
# HOME & AUTHENTICATION ROUTES
# ============================================================================

@app.route('/')
def index():
    """Home page route"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration route"""
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Hash password for security
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        
        conn = get_db_connection()
        if not conn:
            flash('Database connection error!', 'danger')
            return redirect(url_for('register'))
        
        cursor = conn.cursor()
        
        try:
            # Check if user already exists
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                flash('Email already registered!', 'danger')
                return redirect(url_for('register'))
            
            # Insert new user
            cursor.execute(
                "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                (username, email, hashed_password)
            )
            conn.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        
        except Exception as e:
            flash(f'Error during registration: {str(e)}', 'danger')
            return redirect(url_for('register'))
        
        finally:
            cursor.close()
            conn.close()
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login route"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        if not email or not password:
            flash('Please enter both email and password!', 'danger')
            return redirect(url_for('login'))
        
        conn = get_db_connection()
        if not conn:
            flash('Database connection error. Please try again.', 'danger')
            return redirect(url_for('login'))
        
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            
            if user:
                # Check if password matches
                if check_password_hash(user['password'], password):
                    session['user_id'] = user['id']
                    session['username'] = user['username']
                    session['email'] = user['email']
                    session['is_admin'] = user.get('is_admin', False)
                    flash(f'Welcome back, {user["username"]}!', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    flash('Invalid email or password!', 'danger')
            else:
                flash('Invalid email or password!', 'danger')
        
        except Exception as e:
            print(f"Login error: {e}")
            flash('An error occurred during login. Please try again.', 'danger')
        
        finally:
            cursor.close()
            conn.close()
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """User logout route"""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


# ============================================================================
# REAL-TIME PRICE API ROUTES
# ============================================================================

@app.route('/api/stock-price/<stock_symbol>')
def api_stock_price(stock_symbol):
    """
    Get real-time stock price data with intraday chart
    
    Returns:
    - Current price
    - Price change and percentage
    - Day high/low
    - Intraday price data for mini chart
    - Market status
    """
    try:
        ticker = yf.Ticker(stock_symbol)
        
        # Get current data
        info = ticker.info
        history = ticker.history(period='1d', interval='1m')
        
        if history.empty:
            # Try with longer period if 1d is empty
            history = ticker.history(period='5d', interval='5m')
        
        if history.empty:
            return jsonify({
                'success': False,
                'message': f'No data available for {stock_symbol}'
            })
        
        # Get current price (last available)
        current_price = history['Close'].iloc[-1]
        
        # Get previous close
        previous_close = info.get('previousClose', current_price)
        
        # Calculate change
        change = current_price - previous_close
        change_percent = (change / previous_close * 100) if previous_close else 0
        
        # Get day high and low
        day_high = history['High'].max()
        day_low = history['Low'].min()
        day_open = history['Open'].iloc[0]
        
        # Get stock name
        stock_name = info.get('longName', stock_symbol)
        if not stock_name or stock_name == stock_symbol:
            stock_name = info.get('shortName', stock_symbol.replace('.NS', '').replace('.BO', ''))
        
        # Check if market is open (IST timezone for Indian stocks)
        is_market_open = check_market_status(stock_symbol)
        
        # Prepare intraday data for chart (last 20 points)
        intraday_data = []
        for idx in history.index[-20:]:
            intraday_data.append({
                'time': idx.strftime('%H:%M'),
                'price': float(history.loc[idx, 'Close'])
            })
        
        return jsonify({
            'success': True,
            'data': {
                'symbol': stock_symbol,
                'name': stock_name,
                'price': float(current_price),
                'change': float(change),
                'changePercent': float(change_percent),
                'high': float(day_high),
                'low': float(day_low),
                'open': float(day_open),
                'previousClose': float(previous_close),
                'isMarketOpen': is_market_open,
                'intradayData': intraday_data,
                'timestamp': datetime.now().isoformat()
            }
        })
    
    except Exception as e:
        print(f"Error fetching stock price for {stock_symbol}: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Error fetching data: {str(e)}'
        })

def check_market_status(stock_symbol):
    """
    Check if market is currently open based on stock symbol
    
    Indian markets (NSE/BSE): 9:15 AM - 3:30 PM IST, Monday-Friday
    US markets: 9:30 AM - 4:00 PM EST, Monday-Friday
    """
    try:
        # Determine market based on stock symbol
        if '.NS' in stock_symbol or '.BO' in stock_symbol:
            # Indian market
            tz = pytz.timezone('Asia/Kolkata')
            now = datetime.now(tz)
            
            # Check if weekend
            if now.weekday() >= 5:  # Saturday = 5, Sunday = 6
                return False
            
            # Market hours: 9:15 AM - 3:30 PM
            market_open = now.replace(hour=9, minute=15, second=0, microsecond=0)
            market_close = now.replace(hour=15, minute=30, second=0, microsecond=0)
            
            return market_open <= now <= market_close
        
        else:
            # US market (default)
            tz = pytz.timezone('America/New_York')
            now = datetime.now(tz)
            
            # Check if weekend
            if now.weekday() >= 5:
                return False
            
            # Market hours: 9:30 AM - 4:00 PM EST
            market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
            market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
            
            return market_open <= now <= market_close
    
    except Exception as e:
        print(f"Error checking market status: {e}")
        return False

@app.route('/api/stock-prices/batch', methods=['POST'])
def api_batch_stock_prices():
    """
    Get prices for multiple stocks at once (more efficient)
    
    Request body: {"symbols": ["RELIANCE.NS", "TCS.NS", "INFY.NS"]}
    """
    try:
        data = request.get_json()
        symbols = data.get('symbols', [])
        
        if not symbols:
            return jsonify({
                'success': False,
                'message': 'No symbols provided'
            })
        
        results = {}
        
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                history = ticker.history(period='1d', interval='1m')
                
                if not history.empty:
                    current_price = history['Close'].iloc[-1]
                    previous_close = ticker.info.get('previousClose', current_price)
                    change = current_price - previous_close
                    change_percent = (change / previous_close * 100) if previous_close else 0
                    
                    results[symbol] = {
                        'success': True,
                        'price': float(current_price),
                        'change': float(change),
                        'changePercent': float(change_percent),
                        'isMarketOpen': check_market_status(symbol)
                    }
                else:
                    results[symbol] = {
                        'success': False,
                        'message': 'No data available'
                    }
            
            except Exception as e:
                results[symbol] = {
                    'success': False,
                    'message': str(e)
                }
        
        return jsonify({
            'success': True,
            'data': results,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })

@app.route('/api/market-status')
def api_market_status():
    """
    Get current market status for different exchanges
    """
    try:
        nse_open = check_market_status('RELIANCE.NS')
        bse_open = check_market_status('RELIANCE.BO')
        us_open = check_market_status('AAPL')
        
        ist = pytz.timezone('Asia/Kolkata')
        current_time_ist = datetime.now(ist)
        
        return jsonify({
            'success': True,
            'data': {
                'NSE': {
                    'isOpen': nse_open,
                    'name': 'National Stock Exchange',
                    'hours': '9:15 AM - 3:30 PM IST',
                    'timezone': 'Asia/Kolkata'
                },
                'BSE': {
                    'isOpen': bse_open,
                    'name': 'Bombay Stock Exchange',
                    'hours': '9:15 AM - 3:30 PM IST',
                    'timezone': 'Asia/Kolkata'
                },
                'US': {
                    'isOpen': us_open,
                    'name': 'US Stock Market',
                    'hours': '9:30 AM - 4:00 PM EST',
                    'timezone': 'America/New_York'
                },
                'currentTime': current_time_ist.strftime('%Y-%m-%d %H:%M:%S IST'),
                'timestamp': datetime.now().isoformat()
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })

@app.route('/api/stock-quote/<stock_symbol>')
def api_stock_quote(stock_symbol):
    """
    Get detailed stock quote information
    """
    try:
        ticker = yf.Ticker(stock_symbol)
        info = ticker.info
        history = ticker.history(period='1d')
        
        if history.empty:
            return jsonify({
                'success': False,
                'message': 'No data available'
            })
        
        current_price = history['Close'].iloc[-1]
        
        quote = {
            'symbol': stock_symbol,
            'name': info.get('longName', stock_symbol),
            'price': float(current_price),
            'currency': info.get('currency', 'INR'),
            'marketCap': info.get('marketCap', 0),
            'volume': int(info.get('volume', 0)),
            'avgVolume': int(info.get('averageVolume', 0)),
            'dayHigh': float(info.get('dayHigh', 0)),
            'dayLow': float(info.get('dayLow', 0)),
            'fiftyTwoWeekHigh': float(info.get('fiftyTwoWeekHigh', 0)),
            'fiftyTwoWeekLow': float(info.get('fiftyTwoWeekLow', 0)),
            'pe': info.get('trailingPE', None),
            'eps': info.get('trailingEps', None),
            'sector': info.get('sector', 'N/A'),
            'industry': info.get('industry', 'N/A'),
            'isMarketOpen': check_market_status(stock_symbol)
        }
        
        return jsonify({
            'success': True,
            'data': quote
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })


# ============================================================================
# DASHBOARD & PREDICTION ROUTES
# ============================================================================

@app.route('/dashboard')
def dashboard():
    """User dashboard showing prediction history"""
    if 'user_id' not in session:
        flash('Please login first!', 'warning')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    if not conn:
        flash('Database connection error!', 'danger')
        return render_template('dashboard.html', predictions=[])
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute(
            "SELECT * FROM predictions WHERE user_id = %s ORDER BY prediction_date DESC LIMIT 10",
            (session['user_id'],)
        )
        predictions = cursor.fetchall()
        
        # Parse JSON data for each prediction
        for prediction in predictions:
            if prediction['predicted_values']:
                try:
                    prediction['parsed_data'] = json.loads(prediction['predicted_values'])
                except:
                    prediction['parsed_data'] = None
        
        return render_template('dashboard.html', predictions=predictions)
    
    except Exception as e:
        print(f"Dashboard error: {e}")
        flash('Error loading dashboard!', 'danger')
        return render_template('dashboard.html', predictions=[])
    
    finally:
        cursor.close()
        conn.close()

@app.route('/predict', methods=['POST'])
def predict():
    """Stock prediction route"""
    if 'user_id' not in session:
        flash('Please login first!', 'warning')
        return redirect(url_for('login'))
    
    stock_symbol = request.form['stock_symbol'].upper()
    
    try:
        # Step 1: Fetch stock data
        print(f"Fetching data for {stock_symbol}...")
        stock_data = fetch_stock_data(stock_symbol)
        
        if stock_data is None or stock_data.empty:
            flash(f'No data found for stock symbol: {stock_symbol}', 'danger')
            return redirect(url_for('dashboard'))
        
        # Step 2: Preprocess data
        print("Preprocessing data...")
        processed_data = preprocess_data(stock_data)
        
        # Step 3: Train models and predict
        print("Training models and predicting...")
        result = train_and_predict(processed_data, stock_symbol)
        
        # Step 4: Save prediction to database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        prediction_data = {
            'best_model': result['best_model'],
            'predictions': result['predictions'].tolist()[:10],
            'metrics': result['metrics']
        }
        
        cursor.execute(
            "INSERT INTO predictions (user_id, stock_symbol, predicted_values) VALUES (%s, %s, %s)",
            (session['user_id'], stock_symbol, json.dumps(prediction_data))
        )
        conn.commit()
        cursor.close()
        conn.close()
        
        flash(f'Prediction successful for {stock_symbol}!', 'success')
        return render_template('result.html', 
                             stock_symbol=stock_symbol,
                             result=result,
                             plot_url=result['plot_path'])
    
    except Exception as e:
        print(f"Prediction error: {e}")
        flash(f'Error during prediction: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))

# ============================================================================
# NEWS & MARKET DATA ROUTES
# ============================================================================

@app.route('/news')
def news():
    """Market news and updates page"""
    try:
        # Get comprehensive news data
        print("Fetching news data...")
        news_data = get_all_news(limit=20)
        
        # Debug: Print what we got
        print(f"Market summary: {len(news_data.get('market_summary', {}))} items")
        print(f"Trending stocks: {len(news_data.get('trending_stocks', []))} items")
        print(f"Market news: {len(news_data.get('market_news', []))} items")
        print(f"Economic calendar: {len(news_data.get('economic_calendar', []))} items")
        
        # Ensure we have at least some data
        if not news_data.get('market_news'):
            print("No market news found, using placeholder data")
            from utils.news_fetcher import get_placeholder_news
            news_data['market_news'] = get_placeholder_news()
        
        return render_template('news.html', 
                             market_summary=news_data.get('market_summary', {}),
                             trending_stocks=news_data.get('trending_stocks', []),
                             market_news=news_data.get('market_news', []),
                             economic_calendar=news_data.get('economic_calendar', []))
    
    except Exception as e:
        print(f"Error loading news: {e}")
        import traceback
        traceback.print_exc()
        
        # Provide fallback data
        from utils.news_fetcher import get_placeholder_news
        return render_template('news.html', 
                             market_summary={}, 
                             trending_stocks=[], 
                             market_news=get_placeholder_news(),
                             economic_calendar=[])

@app.route('/api/stock-news/<stock_symbol>')
def api_stock_news(stock_symbol):
    """API endpoint to get news for specific stock"""
    try:
        from utils.news_fetcher import get_stock_news_yfinance
        news = get_stock_news_yfinance(stock_symbol, limit=10)
        return jsonify({'success': True, 'news': news})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/market-summary')
def api_market_summary():
    """API endpoint to get market summary"""
    try:
        summary = get_market_summary()
        return jsonify({'success': True, 'data': summary})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ============================================================================
# ADMIN ROUTES
# ============================================================================

@app.route('/admin')
def admin():
    """Admin dashboard to view all users and predictions - Admin only"""
    if 'user_id' not in session:
        flash('Please login first!', 'warning')
        return redirect(url_for('login'))
    
    # Check if user is admin
    conn = get_db_connection()
    if not conn:
        flash('Database connection error!', 'danger')
        return redirect(url_for('dashboard'))
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Check if current user is admin
        cursor.execute("SELECT is_admin FROM users WHERE id = %s", (session['user_id'],))
        user = cursor.fetchone()
        
        if not user or not user.get('is_admin', False):
            flash('Access denied! Admin privileges required.', 'danger')
            return redirect(url_for('dashboard'))
        
        # Get all users
        cursor.execute("SELECT id, username, email, created_at FROM users ORDER BY created_at DESC")
        users = cursor.fetchall()
        
        # Get all predictions count
        cursor.execute("SELECT COUNT(*) as total FROM predictions")
        total_predictions = cursor.fetchone()['total']
        
        # Get recent predictions
        cursor.execute("""
            SELECT p.id, p.stock_symbol, p.prediction_date, u.username, u.email
            FROM predictions p
            JOIN users u ON p.user_id = u.id
            ORDER BY p.prediction_date DESC
            LIMIT 20
        """)
        recent_predictions = cursor.fetchall()
        
        return render_template('admin.html', 
                             users=users, 
                             total_predictions=total_predictions,
                             recent_predictions=recent_predictions)
    
    except Exception as e:
        print(f"Admin error: {e}")
        flash('Error loading admin panel!', 'danger')
        return redirect(url_for('dashboard'))
    
    finally:
        cursor.close()
        conn.close()

# ============================================================================
# WATCHLIST ROUTES
# ============================================================================

@app.route('/watchlist')
def watchlist():
    """Display user's watchlist"""
    if 'user_id' not in session:
        flash('Please login first!', 'warning')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    if not conn:
        flash('Database connection error!', 'danger')
        return render_template('watchlist.html', watchlist_stocks=[])
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Get user's watchlist with current prices
        cursor.execute("""
            SELECT id, stock_symbol, stock_name, added_date, alert_price
            FROM watchlist 
            WHERE user_id = %s 
            ORDER BY added_date DESC
        """, (session['user_id'],))
        
        watchlist_stocks = cursor.fetchall()
        
        # Get current prices for watchlist stocks
        import yfinance as yf
        for stock in watchlist_stocks:
            try:
                ticker = yf.Ticker(stock['stock_symbol'])
                history = ticker.history(period='1d')
                
                if not history.empty:
                    current_price = history['Close'].iloc[-1]
                    prev_close = ticker.info.get('previousClose', current_price)
                    change = current_price - prev_close
                    change_pct = (change / prev_close * 100) if prev_close else 0
                    
                    stock['current_price'] = current_price
                    stock['change'] = change
                    stock['change_pct'] = change_pct
                    stock['is_positive'] = change >= 0
                else:
                    stock['current_price'] = None
                    stock['change'] = 0
                    stock['change_pct'] = 0
                    stock['is_positive'] = True
            except:
                stock['current_price'] = None
                stock['change'] = 0
                stock['change_pct'] = 0
                stock['is_positive'] = True
        
        return render_template('watchlist.html', watchlist_stocks=watchlist_stocks)
    
    except Exception as e:
        print(f"Watchlist error: {e}")
        flash('Error loading watchlist!', 'danger')
        return render_template('watchlist.html', watchlist_stocks=[])
    
    finally:
        cursor.close()
        conn.close()

@app.route('/watchlist/add', methods=['POST'])
def add_to_watchlist():
    """Add stock to watchlist"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login first'})
    
    stock_symbol = request.form.get('stock_symbol', '').upper().strip()
    
    if not stock_symbol:
        return jsonify({'success': False, 'message': 'Stock symbol is required'})
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection error'})
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Get stock name from yfinance
        import yfinance as yf
        ticker = yf.Ticker(stock_symbol)
        info = ticker.info
        stock_name = info.get('longName', stock_symbol.replace('.NS', '').replace('.BO', ''))
        
        # Check if already in watchlist
        cursor.execute("""
            SELECT id FROM watchlist 
            WHERE user_id = %s AND stock_symbol = %s
        """, (session['user_id'], stock_symbol))
        
        if cursor.fetchone():
            return jsonify({'success': False, 'message': 'Stock already in watchlist'})
        
        # Add to watchlist
        cursor.execute("""
            INSERT INTO watchlist (user_id, stock_symbol, stock_name)
            VALUES (%s, %s, %s)
        """, (session['user_id'], stock_symbol, stock_name))
        
        conn.commit()
        
        return jsonify({
            'success': True, 
            'message': f'{stock_symbol} added to watchlist',
            'stock_name': stock_name
        })
    
    except Exception as e:
        print(f"Error adding to watchlist: {e}")
        return jsonify({'success': False, 'message': str(e)})
    
    finally:
        cursor.close()
        conn.close()

@app.route('/watchlist/remove/<int:watchlist_id>', methods=['POST'])
def remove_from_watchlist(watchlist_id):
    """Remove stock from watchlist"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login first'})
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection error'})
    
    cursor = conn.cursor()
    
    try:
        # Delete from watchlist (ensure it belongs to user)
        cursor.execute("""
            DELETE FROM watchlist 
            WHERE id = %s AND user_id = %s
        """, (watchlist_id, session['user_id']))
        
        conn.commit()
        
        if cursor.rowcount > 0:
            return jsonify({'success': True, 'message': 'Removed from watchlist'})
        else:
            return jsonify({'success': False, 'message': 'Stock not found in watchlist'})
    
    except Exception as e:
        print(f"Error removing from watchlist: {e}")
        return jsonify({'success': False, 'message': str(e)})
    
    finally:
        cursor.close()
        conn.close()

@app.route('/watchlist/set-alert', methods=['POST'])
def set_price_alert():
    """Set price alert for watchlist stock"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login first'})
    
    watchlist_id = request.form.get('watchlist_id')
    alert_price = request.form.get('alert_price')
    
    if not watchlist_id or not alert_price:
        return jsonify({'success': False, 'message': 'Missing parameters'})
    
    try:
        alert_price = float(alert_price)
    except ValueError:
        return jsonify({'success': False, 'message': 'Invalid price'})
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection error'})
    
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE watchlist 
            SET alert_price = %s 
            WHERE id = %s AND user_id = %s
        """, (alert_price, watchlist_id, session['user_id']))
        
        conn.commit()
        
        return jsonify({'success': True, 'message': f'Price alert set at ₹{alert_price:.2f}'})
    
    except Exception as e:
        print(f"Error setting alert: {e}")
        return jsonify({'success': False, 'message': str(e)})
    
    finally:
        cursor.close()
        conn.close()


# ============================================================================
# TECHNICAL INDICATORS ROUTES
# ============================================================================

@app.route('/technical/<stock_symbol>')
def technical_analysis(stock_symbol):
    """Technical analysis page for a specific stock"""
    if 'user_id' not in session:
        flash('Please login first!', 'warning')
        return redirect(url_for('login'))
    
    try:
        # Fetch stock data
        stock_data = fetch_stock_data(stock_symbol, period='1y')
        
        if stock_data is None or stock_data.empty:
            flash(f'No data found for {stock_symbol}', 'danger')
            return redirect(url_for('dashboard'))
        
        # Calculate technical indicators
        ti = TechnicalIndicators(stock_data)
        analysis = ti.calculate_all_indicators()
        
        # Get data with indicators for charting
        data_with_indicators = ti.get_data_with_indicators()
        
        # Prepare chart data (last 90 days)
        chart_data = data_with_indicators.tail(90).to_dict('records')
        for record in chart_data:
            record['Date'] = record['Date'].strftime('%Y-%m-%d')
        
        return render_template('technical_analysis.html',
                             stock_symbol=stock_symbol,
                             analysis=analysis,
                             chart_data=json.dumps(chart_data))
    
    except Exception as e:
        print(f"Technical analysis error: {e}")
        import traceback
        traceback.print_exc()
        flash(f'Error analyzing {stock_symbol}', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/api/technical/<stock_symbol>')
def api_technical_indicators(stock_symbol):
    """API endpoint for technical indicators"""
    try:
        analysis = analyze_stock_technical(stock_symbol)
        
        if analysis is None:
            return jsonify({
                'success': False,
                'message': f'No data available for {stock_symbol}'
            })
        
        return jsonify({
            'success': True,
            'data': analysis,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })

@app.route('/api/technical/<stock_symbol>/indicators')
def api_specific_indicators(stock_symbol):
    """Get specific indicators with historical data"""
    try:
        # Get query parameters
        indicators = request.args.get('indicators', 'rsi,macd,bb').split(',')
        period = request.args.get('period', '3mo')
        
        # Fetch data
        stock_data = fetch_stock_data(stock_symbol, period=period)
        
        if stock_data is None or stock_data.empty:
            return jsonify({
                'success': False,
                'message': 'No data available'
            })
        
        # Calculate indicators
        ti = TechnicalIndicators(stock_data)
        
        result = {
            'success': True,
            'stock_symbol': stock_symbol,
            'data': {}
        }
        
        # Calculate requested indicators
        if 'rsi' in indicators:
            ti.calculate_rsi()
            result['data']['rsi'] = ti.data[['Date', 'Close', 'RSI', 'RSI_Signal']].tail(90).to_dict('records')
        
        if 'macd' in indicators:
            ti.calculate_macd()
            result['data']['macd'] = ti.data[['Date', 'Close', 'MACD', 'MACD_Signal', 'MACD_Histogram']].tail(90).to_dict('records')
        
        if 'bb' in indicators:
            ti.calculate_bollinger_bands()
            result['data']['bollinger_bands'] = ti.data[['Date', 'Close', 'BB_Upper', 'BB_Middle', 'BB_Lower']].tail(90).to_dict('records')
        
        if 'volume' in indicators:
            volume_analysis = ti.analyze_volume()
            result['data']['volume'] = volume_analysis
        
        # Format dates
        for indicator in result['data']:
            if isinstance(result['data'][indicator], list):
                for record in result['data'][indicator]:
                    if 'Date' in record:
                        record['Date'] = record['Date'].strftime('%Y-%m-%d')
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })

@app.route('/api/technical/<stock_symbol>/patterns')
def api_candlestick_patterns(stock_symbol):
    """Get candlestick patterns"""
    try:
        stock_data = fetch_stock_data(stock_symbol, period='3mo')
        
        if stock_data is None or stock_data.empty:
            return jsonify({
                'success': False,
                'message': 'No data available'
            })
        
        ti = TechnicalIndicators(stock_data)
        patterns = ti.detect_candlestick_patterns()
        
        # Format dates
        for pattern in patterns:
            pattern['date'] = pattern['date'].strftime('%Y-%m-%d')
        
        return jsonify({
            'success': True,
            'patterns': patterns
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })

@app.route('/api/technical/<stock_symbol>/support-resistance')
def api_support_resistance(stock_symbol):
    """Get support and resistance levels"""
    try:
        stock_data = fetch_stock_data(stock_symbol, period='6mo')
        
        if stock_data is None or stock_data.empty:
            return jsonify({
                'success': False,
                'message': 'No data available'
            })
        
        ti = TechnicalIndicators(stock_data)
        levels = ti.find_support_resistance()
        
        return jsonify({
            'success': True,
            'data': levels
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })

@app.route('/api/technical/<stock_symbol>/recommendation')
def api_trading_recommendation(stock_symbol):
    """Get trading recommendation based on technical analysis"""
    try:
        analysis = analyze_stock_technical(stock_symbol)
        
        if analysis is None:
            return jsonify({
                'success': False,
                'message': 'No data available'
            })
        
        return jsonify({
            'success': True,
            'stock_symbol': stock_symbol,
            'recommendation': analysis['recommendation'],
            'key_indicators': {
                'rsi': analysis['rsi'],
                'macd_signal': analysis['macd']['signal'],
                'trend': analysis['trend'],
                'bb_signal': analysis['bollinger_bands']['signal']
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })

@app.route('/technical-scanner')
def technical_scanner():
    """Technical scanner page for multiple stocks"""
    if 'user_id' not in session:
        flash('Please login first!', 'warning')
        return redirect(url_for('login'))
    
    # Popular stocks to scan
    default_stocks = ['RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDFCBANK.NS', 
                     'ICICIBANK.NS', 'HINDUNILVR.NS', 'SBIN.NS', 'BHARTIARTL.NS']
    
    scanner_results = []
    
    for symbol in default_stocks:
        try:
            analysis = analyze_stock_technical(symbol)
            if analysis:
                scanner_results.append({
                    'symbol': symbol,
                    'price': analysis['current_price'],
                    'trend': analysis['trend'],
                    'rsi': analysis['rsi']['value'],
                    'rsi_signal': analysis['rsi']['signal'],
                    'macd_signal': analysis['macd']['signal'],
                    'recommendation': analysis['recommendation']
                })
        except:
            continue
    
    return render_template('technical_scanner.html', results=scanner_results)


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors"""
    flash('An internal error occurred. Please try again.', 'danger')
    return redirect(url_for('index'))

# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    print("="*60)
    print("Stock Market Prediction System")
    print("="*60)
    print("\nStarting Flask application...")
    print("Access the application at: http://localhost:5000")
    print("\nAvailable routes:")
    print("  - Home: http://localhost:5000/")
    print("  - Dashboard: http://localhost:5000/dashboard")
    print("  - News: http://localhost:5000/news")
    print("  - Admin: http://localhost:5000/admin")
    print("\nPress Ctrl+C to stop the server")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)