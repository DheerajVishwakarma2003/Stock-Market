"""
Indian Stock Market Helper Utilities
Provides validation and information for NSE/BSE stocks
"""

# Popular Indian stocks with their full names
POPULAR_NSE_STOCKS = {
    'RELIANCE.NS': 'Reliance Industries Limited',
    'TCS.NS': 'Tata Consultancy Services',
    'HDFCBANK.NS': 'HDFC Bank Limited',
    'INFY.NS': 'Infosys Limited',
    'ICICIBANK.NS': 'ICICI Bank Limited',
    'HINDUNILVR.NS': 'Hindustan Unilever Limited',
    'SBIN.NS': 'State Bank of India',
    'BHARTIARTL.NS': 'Bharti Airtel Limited',
    'ITC.NS': 'ITC Limited',
    'KOTAKBANK.NS': 'Kotak Mahindra Bank',
    'LT.NS': 'Larsen & Toubro Limited',
    'AXISBANK.NS': 'Axis Bank Limited',
    'ASIANPAINT.NS': 'Asian Paints Limited',
    'MARUTI.NS': 'Maruti Suzuki India Limited',
    'WIPRO.NS': 'Wipro Limited',
    'TATASTEEL.NS': 'Tata Steel Limited',
    'SUNPHARMA.NS': 'Sun Pharmaceutical Industries',
    'TITAN.NS': 'Titan Company Limited',
    'BAJFINANCE.NS': 'Bajaj Finance Limited',
    'TECHM.NS': 'Tech Mahindra Limited',
    'NESTLEIND.NS': 'Nestle India Limited',
    'ULTRACEMCO.NS': 'UltraTech Cement Limited',
    'ONGC.NS': 'Oil and Natural Gas Corporation',
    'NTPC.NS': 'NTPC Limited',
    'POWERGRID.NS': 'Power Grid Corporation',
    'M&M.NS': 'Mahindra & Mahindra Limited',
    'ADANIPORTS.NS': 'Adani Ports and SEZ',
    'COALINDIA.NS': 'Coal India Limited',
    'DRREDDY.NS': 'Dr. Reddy\'s Laboratories',
    'EICHERMOT.NS': 'Eicher Motors Limited',
}

# Sector classification
SECTORS = {
    'Banking & Finance': ['HDFCBANK.NS', 'ICICIBANK.NS', 'SBIN.NS', 'KOTAKBANK.NS', 
                          'AXISBANK.NS', 'BAJFINANCE.NS'],
    'IT & Technology': ['TCS.NS', 'INFY.NS', 'WIPRO.NS', 'TECHM.NS'],
    'Energy & Power': ['RELIANCE.NS', 'ONGC.NS', 'NTPC.NS', 'POWERGRID.NS', 'COALINDIA.NS'],
    'Automobile': ['MARUTI.NS', 'M&M.NS', 'EICHERMOT.NS'],
    'FMCG': ['HINDUNILVR.NS', 'ITC.NS', 'NESTLEIND.NS', 'ASIANPAINT.NS', 'TITAN.NS'],
    'Pharma': ['SUNPHARMA.NS', 'DRREDDY.NS'],
    'Infrastructure': ['LT.NS', 'ULTRACEMCO.NS', 'ADANIPORTS.NS', 'TATASTEEL.NS'],
    'Telecom': ['BHARTIARTL.NS'],
}

def validate_indian_stock_symbol(symbol):
    """
    Validate if the symbol is properly formatted for Indian stocks
    
    Parameters:
    - symbol: Stock symbol string
    
    Returns:
    - tuple: (is_valid, formatted_symbol, message)
    """
    symbol = symbol.strip().upper()
    
    # Check if it already has .NS or .BO suffix
    if symbol.endswith('.NS') or symbol.endswith('.BO'):
        return (True, symbol, 'Valid Indian stock symbol')
    
    # If no suffix, add .NS by default
    if '.' not in symbol:
        formatted = f"{symbol}.NS"
        return (True, formatted, f'Added NSE suffix: {formatted}')
    
    return (False, symbol, 'Invalid format. Use .NS for NSE or .BO for BSE')

def get_stock_info(symbol):
    """
    Get information about an Indian stock
    
    Parameters:
    - symbol: Stock symbol
    
    Returns:
    - dict: Stock information
    """
    symbol = symbol.upper()
    
    info = {
        'symbol': symbol,
        'name': POPULAR_NSE_STOCKS.get(symbol, 'Unknown'),
        'exchange': 'NSE' if '.NS' in symbol else 'BSE' if '.BO' in symbol else 'Unknown',
        'sector': get_sector(symbol),
        'is_popular': symbol in POPULAR_NSE_STOCKS
    }
    
    return info

def get_sector(symbol):
    """Get sector for a stock symbol"""
    for sector, stocks in SECTORS.items():
        if symbol in stocks:
            return sector
    return 'Other'

def get_popular_stocks_by_sector():
    """Get stocks organized by sector"""
    return SECTORS

def get_stock_suggestions(partial_symbol=''):
    """
    Get stock suggestions based on partial input
    
    Parameters:
    - partial_symbol: Partial stock symbol
    
    Returns:
    - list: Suggested stock symbols
    """
    partial = partial_symbol.upper()
    
    if not partial:
        # Return top 10 most popular stocks
        return list(POPULAR_NSE_STOCKS.keys())[:10]
    
    # Filter stocks that start with the partial symbol
    suggestions = [
        symbol for symbol in POPULAR_NSE_STOCKS.keys() 
        if symbol.startswith(partial) or symbol.replace('.NS', '').startswith(partial)
    ]
    
    return suggestions[:10]

def format_indian_currency(amount):
    """
    Format amount in Indian numbering system (Lakhs, Crores)
    
    Parameters:
    - amount: Numeric amount
    
    Returns:
    - str: Formatted string
    """
    if amount >= 10000000:  # 1 Crore
        return f"₹{amount/10000000:.2f} Cr"
    elif amount >= 100000:  # 1 Lakh
        return f"₹{amount/100000:.2f} L"
    elif amount >= 1000:  # 1 Thousand
        return f"₹{amount/1000:.2f} K"
    else:
        return f"₹{amount:.2f}"

def get_market_indices():
    """Get major Indian market indices"""
    return {
        'NIFTY 50': '^NSEI',
        'SENSEX': '^BSESN',
        'NIFTY Bank': '^NSEBANK',
        'NIFTY IT': '^CNXIT',
        'NIFTY Auto': '^CNXAUTO',
        'NIFTY Pharma': '^CNXPHARMA',
        'NIFTY FMCG': '^CNXFMCG',
    }

def is_trading_day(date=None):
    """
    Check if a given date is a trading day in India
    (Excludes weekends - Saturday and Sunday)
    
    Parameters:
    - date: datetime object (default: today)
    
    Returns:
    - bool: True if trading day
    """
    from datetime import datetime
    
    if date is None:
        date = datetime.now()
    
    # Weekend check
    if date.weekday() >= 5:  # 5=Saturday, 6=Sunday
        return False
    
    # Note: Indian market holidays not checked here
    # For production, integrate with NSE holiday calendar
    return True

def get_market_timings():
    """Get Indian stock market timings"""
    return {
        'pre_open': '09:00 - 09:15 IST',
        'regular': '09:15 - 15:30 IST',
        'post_close': '15:40 - 16:00 IST',
        'timezone': 'Asia/Kolkata (IST)'
    }

# Quick reference guide
INDIAN_STOCK_GUIDE = """
Indian Stock Market Quick Reference:

NSE (National Stock Exchange):
- Add .NS suffix to stock symbols
- Examples: RELIANCE.NS, TCS.NS, INFY.NS

BSE (Bombay Stock Exchange):
- Add .BO suffix to stock symbols  
- Examples: RELIANCE.BO, TCS.BO

Popular Stocks by Sector:
1. Banking: HDFCBANK.NS, ICICIBANK.NS, SBIN.NS
2. IT: TCS.NS, INFY.NS, WIPRO.NS
3. Energy: RELIANCE.NS, ONGC.NS
4. Auto: MARUTI.NS, M&M.NS
5. FMCG: HINDUNILVR.NS, ITC.NS

Market Timings:
- Pre-open: 09:00 - 09:15 IST
- Regular: 09:15 - 15:30 IST
- Trading Days: Monday to Friday (excluding holidays)
"""

if __name__ == "__main__":
    # Test the functions
    print("="*60)
    print("Indian Stock Market Helper - Test")
    print("="*60)
    
    # Test validation
    test_symbols = ['RELIANCE', 'TCS.NS', 'INFY.BO', 'INVALID.XY']
    for symbol in test_symbols:
        is_valid, formatted, msg = validate_indian_stock_symbol(symbol)
        print(f"\n{symbol} -> {formatted}")
        print(f"Valid: {is_valid}, Message: {msg}")
    
    # Test stock info
    print("\n" + "="*60)
    print("Popular Stocks Information:")
    print("="*60)
    for symbol in list(POPULAR_NSE_STOCKS.keys())[:5]:
        info = get_stock_info(symbol)
        print(f"\n{info['symbol']}: {info['name']}")
        print(f"Exchange: {info['exchange']}, Sector: {info['sector']}")
    
    # Print guide
    print("\n" + "="*60)
    print(INDIAN_STOCK_GUIDE)