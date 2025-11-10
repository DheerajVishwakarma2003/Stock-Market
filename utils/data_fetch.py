import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def fetch_stock_data(stock_symbol, period='2y'):
    """
    Fetch historical stock data from Yahoo Finance
    Automatically formats Indian stock symbols with .NS suffix if needed
    
    Parameters:
    - stock_symbol: Stock ticker symbol (e.g., 'AAPL', 'RELIANCE', 'RELIANCE.NS')
    - period: Time period for historical data (default: 2 years)
    
    Returns:
    - DataFrame with stock data or None if error
    """
    try:
        # Auto-format Indian stock symbols
        original_symbol = stock_symbol
        stock_symbol = stock_symbol.strip().upper()
        
        # If no suffix and looks like Indian stock, add .NS
        if '.' not in stock_symbol:
            # List of common Indian stock prefixes (you can expand this)
            indian_stocks = ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK', 
                           'SBIN', 'BHARTIARTL', 'ITC', 'HINDUNILVR', 'KOTAKBANK',
                           'LT', 'AXISBANK', 'ASIANPAINT', 'MARUTI', 'WIPRO',
                           'TATASTEEL', 'SUNPHARMA', 'TITAN', 'BAJFINANCE', 'TECHM',
                           'NESTLEIND', 'ULTRACEMCO', 'ONGC', 'NTPC', 'POWERGRID',
                           'M&M', 'ADANIPORTS', 'COALINDIA', 'DRREDDY', 'EICHERMOT']
            
            if any(stock_symbol.startswith(prefix) for prefix in indian_stocks):
                stock_symbol = f"{stock_symbol}.NS"
                print(f"Auto-formatted to Indian NSE symbol: {stock_symbol}")
        
        # Create ticker object
        ticker = yf.Ticker(stock_symbol)
        
        # Fetch historical data
        stock_data = ticker.history(period=period)
        
        if stock_data.empty:
            print(f"No data found for {stock_symbol}")
            
            # If .NS didn't work, try .BO
            if stock_symbol.endswith('.NS'):
                bo_symbol = stock_symbol.replace('.NS', '.BO')
                print(f"Trying BSE symbol: {bo_symbol}")
                ticker = yf.Ticker(bo_symbol)
                stock_data = ticker.history(period=period)
                
                if not stock_data.empty:
                    stock_symbol = bo_symbol
                    print(f"Found data with BSE symbol: {bo_symbol}")
            
            if stock_data.empty:
                return None
        
        # Reset index to make Date a column
        stock_data.reset_index(inplace=True)
        
        # Select relevant columns
        stock_data = stock_data[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
        
        print(f"Successfully fetched {len(stock_data)} records for {stock_symbol}")
        return stock_data
    
    except Exception as e:
        print(f"Error fetching data for {stock_symbol}: {e}")
        return None

def get_stock_info(stock_symbol):
    """
    Get additional stock information
    
    Parameters:
    - stock_symbol: Stock ticker symbol
    
    Returns:
    - Dictionary with stock info
    """
    try:
        ticker = yf.Ticker(stock_symbol)
        info = ticker.info
        
        return {
            'name': info.get('longName', stock_symbol),
            'sector': info.get('sector', 'N/A'),
            'industry': info.get('industry', 'N/A'),
            'market_cap': info.get('marketCap', 'N/A'),
            'current_price': info.get('currentPrice', 'N/A')
        }
    
    except Exception as e:
        print(f"Error fetching stock info: {e}")
        return None

if __name__ == "__main__":
    # Test the function
    test_symbol = "AAPL"
    data = fetch_stock_data(test_symbol)
    
    if data is not None:
        print(f"\nFirst 5 rows of {test_symbol} data:")
        print(data.head())
        
        info = get_stock_info(test_symbol)
        print(f"\nStock Information:")
        print(info)