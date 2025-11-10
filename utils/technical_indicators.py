"""
Technical Indicators Calculator
Advanced technical analysis tools for stock market predictions
"""

import numpy as np
import pandas as pd
from scipy.signal import argrelextrema

class TechnicalIndicators:
    """
    Calculate various technical indicators for stock analysis
    """
    
    def __init__(self, data):
        """
        Initialize with stock data
        
        Parameters:
        - data: DataFrame with columns ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
        """
        self.data = data.copy()
        self.data['Date'] = pd.to_datetime(self.data['Date'])
        self.data = self.data.sort_values('Date').reset_index(drop=True)
    
    def calculate_rsi(self, period=14):
        """
        Calculate Relative Strength Index (RSI)
        
        RSI = 100 - (100 / (1 + RS))
        where RS = Average Gain / Average Loss
        
        Values:
        - Above 70: Overbought (potential sell signal)
        - Below 30: Oversold (potential buy signal)
        """
        delta = self.data['Close'].diff()
        
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        self.data['RSI'] = rsi
        
        # Determine signal
        self.data['RSI_Signal'] = 'Neutral'
        self.data.loc[rsi > 70, 'RSI_Signal'] = 'Overbought'
        self.data.loc[rsi < 30, 'RSI_Signal'] = 'Oversold'
        
        return rsi
    
    def calculate_macd(self, fast=12, slow=26, signal=9):
        """
        Calculate MACD (Moving Average Convergence Divergence)
        
        MACD Line = EMA(12) - EMA(26)
        Signal Line = EMA(9) of MACD Line
        Histogram = MACD Line - Signal Line
        
        Signals:
        - MACD crosses above Signal: Bullish (buy)
        - MACD crosses below Signal: Bearish (sell)
        """
        ema_fast = self.data['Close'].ewm(span=fast, adjust=False).mean()
        ema_slow = self.data['Close'].ewm(span=slow, adjust=False).mean()
        
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        
        self.data['MACD'] = macd_line
        self.data['MACD_Signal'] = signal_line
        self.data['MACD_Histogram'] = histogram
        
        # Determine crossover signals
        self.data['MACD_Cross'] = 'Hold'
        for i in range(1, len(self.data)):
            if (macd_line.iloc[i] > signal_line.iloc[i] and 
                macd_line.iloc[i-1] <= signal_line.iloc[i-1]):
                self.data.loc[i, 'MACD_Cross'] = 'Buy'
            elif (macd_line.iloc[i] < signal_line.iloc[i] and 
                  macd_line.iloc[i-1] >= signal_line.iloc[i-1]):
                self.data.loc[i, 'MACD_Cross'] = 'Sell'
        
        return macd_line, signal_line, histogram
    
    def calculate_bollinger_bands(self, period=20, std_dev=2):
        """
        Calculate Bollinger Bands
        
        Middle Band = SMA(20)
        Upper Band = SMA(20) + (2 × Standard Deviation)
        Lower Band = SMA(20) - (2 × Standard Deviation)
        
        Signals:
        - Price touching upper band: Overbought
        - Price touching lower band: Oversold
        - Bands narrow: Low volatility (potential breakout)
        - Bands wide: High volatility
        """
        sma = self.data['Close'].rolling(window=period).mean()
        std = self.data['Close'].rolling(window=period).std()
        
        upper_band = sma + (std_dev * std)
        lower_band = sma - (std_dev * std)
        
        self.data['BB_Middle'] = sma
        self.data['BB_Upper'] = upper_band
        self.data['BB_Lower'] = lower_band
        self.data['BB_Width'] = upper_band - lower_band
        
        # Determine position relative to bands
        self.data['BB_Signal'] = 'Neutral'
        self.data.loc[self.data['Close'] >= upper_band, 'BB_Signal'] = 'Overbought'
        self.data.loc[self.data['Close'] <= lower_band, 'BB_Signal'] = 'Oversold'
        
        return upper_band, sma, lower_band
    
    def find_support_resistance(self, order=5):
        """
        Identify Support and Resistance Levels
        
        Support: Price level where buying pressure overcomes selling pressure
        Resistance: Price level where selling pressure overcomes buying pressure
        
        Uses local minima for support and local maxima for resistance
        """
        # Find local minima (support levels)
        support_indices = argrelextrema(self.data['Low'].values, np.less_equal, order=order)[0]
        support_levels = self.data.iloc[support_indices]['Low'].values
        
        # Find local maxima (resistance levels)
        resistance_indices = argrelextrema(self.data['High'].values, np.greater_equal, order=order)[0]
        resistance_levels = self.data.iloc[resistance_indices]['High'].values
        
        # Cluster similar levels
        def cluster_levels(levels, tolerance=0.02):
            if len(levels) == 0:
                return []
            
            levels = sorted(levels)
            clusters = []
            current_cluster = [levels[0]]
            
            for level in levels[1:]:
                if abs(level - np.mean(current_cluster)) / np.mean(current_cluster) < tolerance:
                    current_cluster.append(level)
                else:
                    clusters.append(np.mean(current_cluster))
                    current_cluster = [level]
            
            clusters.append(np.mean(current_cluster))
            return clusters
        
        support_levels = cluster_levels(support_levels)
        resistance_levels = cluster_levels(resistance_levels)
        
        # Get current price
        current_price = self.data['Close'].iloc[-1]
        
        # Find nearest support and resistance
        support_below = [s for s in support_levels if s < current_price]
        resistance_above = [r for r in resistance_levels if r > current_price]
        
        nearest_support = max(support_below) if support_below else None
        nearest_resistance = min(resistance_above) if resistance_above else None
        
        return {
            'support_levels': support_levels[-5:],  # Last 5 support levels
            'resistance_levels': resistance_levels[-5:],  # Last 5 resistance levels
            'nearest_support': nearest_support,
            'nearest_resistance': nearest_resistance,
            'current_price': current_price
        }
    
    def analyze_volume(self):
        """
        Volume Analysis
        
        - Volume trends
        - Volume moving average
        - Volume spike detection
        - On-Balance Volume (OBV)
        """
        # Volume moving average
        self.data['Volume_MA'] = self.data['Volume'].rolling(window=20).mean()
        
        # Volume spike (above 2x average)
        self.data['Volume_Spike'] = self.data['Volume'] > (2 * self.data['Volume_MA'])
        
        # On-Balance Volume (OBV)
        obv = [0]
        for i in range(1, len(self.data)):
            if self.data['Close'].iloc[i] > self.data['Close'].iloc[i-1]:
                obv.append(obv[-1] + self.data['Volume'].iloc[i])
            elif self.data['Close'].iloc[i] < self.data['Close'].iloc[i-1]:
                obv.append(obv[-1] - self.data['Volume'].iloc[i])
            else:
                obv.append(obv[-1])
        
        self.data['OBV'] = obv
        
        # Volume trend
        recent_volume = self.data['Volume'].iloc[-20:].mean()
        older_volume = self.data['Volume'].iloc[-40:-20].mean()
        
        volume_trend = 'Increasing' if recent_volume > older_volume else 'Decreasing'
        
        return {
            'current_volume': self.data['Volume'].iloc[-1],
            'avg_volume': self.data['Volume_MA'].iloc[-1],
            'volume_trend': volume_trend,
            'obv': self.data['OBV'].iloc[-1],
            'recent_spikes': self.data['Volume_Spike'].iloc[-10:].sum()
        }
    
    def detect_candlestick_patterns(self):
        """
        Detect Candlestick Patterns
        
        Patterns detected:
        - Doji (indecision)
        - Hammer (bullish reversal)
        - Shooting Star (bearish reversal)
        - Engulfing (bullish/bearish)
        - Morning Star (bullish reversal)
        - Evening Star (bearish reversal)
        """
        patterns = []
        
        for i in range(2, len(self.data)):
            open_price = self.data['Open'].iloc[i]
            close = self.data['Close'].iloc[i]
            high = self.data['High'].iloc[i]
            low = self.data['Low'].iloc[i]
            
            prev_open = self.data['Open'].iloc[i-1]
            prev_close = self.data['Close'].iloc[i-1]
            
            body = abs(close - open_price)
            total_range = high - low
            upper_shadow = high - max(open_price, close)
            lower_shadow = min(open_price, close) - low
            
            # Doji: Very small body
            if total_range > 0 and body / total_range < 0.1:
                patterns.append({
                    'date': self.data['Date'].iloc[i],
                    'pattern': 'Doji',
                    'type': 'Neutral',
                    'description': 'Indecision in the market'
                })
            
            # Hammer: Small body, long lower shadow, little/no upper shadow
            if (body > 0 and lower_shadow > 2 * body and 
                upper_shadow < body and close > open_price):
                patterns.append({
                    'date': self.data['Date'].iloc[i],
                    'pattern': 'Hammer',
                    'type': 'Bullish',
                    'description': 'Potential bullish reversal'
                })
            
            # Shooting Star: Small body, long upper shadow, little/no lower shadow
            if (body > 0 and upper_shadow > 2 * body and 
                lower_shadow < body and close < open_price):
                patterns.append({
                    'date': self.data['Date'].iloc[i],
                    'pattern': 'Shooting Star',
                    'type': 'Bearish',
                    'description': 'Potential bearish reversal'
                })
            
            # Bullish Engulfing
            if (close > open_price and prev_close < prev_open and
                close > prev_open and open_price < prev_close):
                patterns.append({
                    'date': self.data['Date'].iloc[i],
                    'pattern': 'Bullish Engulfing',
                    'type': 'Bullish',
                    'description': 'Strong bullish reversal signal'
                })
            
            # Bearish Engulfing
            if (close < open_price and prev_close > prev_open and
                close < prev_open and open_price > prev_close):
                patterns.append({
                    'date': self.data['Date'].iloc[i],
                    'pattern': 'Bearish Engulfing',
                    'type': 'Bearish',
                    'description': 'Strong bearish reversal signal'
                })
        
        return patterns[-10:]  # Return last 10 patterns
    
    def calculate_all_indicators(self):
        """
        Calculate all technical indicators at once
        
        Returns comprehensive analysis dictionary
        """
        # Calculate all indicators
        rsi = self.calculate_rsi()
        macd, signal, histogram = self.calculate_macd()
        bb_upper, bb_middle, bb_lower = self.calculate_bollinger_bands()
        support_resistance = self.find_support_resistance()
        volume_analysis = self.analyze_volume()
        patterns = self.detect_candlestick_patterns()
        
        # Get latest values
        latest_idx = -1
        
        # Overall trend analysis
        sma_20 = self.data['Close'].rolling(window=20).mean().iloc[latest_idx]
        sma_50 = self.data['Close'].rolling(window=50).mean().iloc[latest_idx]
        current_price = self.data['Close'].iloc[latest_idx]
        
        if current_price > sma_20 > sma_50:
            trend = 'Strong Uptrend'
        elif current_price > sma_20:
            trend = 'Uptrend'
        elif current_price < sma_20 < sma_50:
            trend = 'Strong Downtrend'
        elif current_price < sma_20:
            trend = 'Downtrend'
        else:
            trend = 'Sideways'
        
        # Compile results
        results = {
            'current_price': float(current_price),
            'trend': trend,
            'rsi': {
                'value': float(rsi.iloc[latest_idx]) if not pd.isna(rsi.iloc[latest_idx]) else 0,
                'signal': self.data['RSI_Signal'].iloc[latest_idx],
                'interpretation': self._interpret_rsi(rsi.iloc[latest_idx])
            },
            'macd': {
                'macd_line': float(macd.iloc[latest_idx]),
                'signal_line': float(signal.iloc[latest_idx]),
                'histogram': float(histogram.iloc[latest_idx]),
                'signal': self.data['MACD_Cross'].iloc[latest_idx],
                'interpretation': self._interpret_macd(histogram.iloc[latest_idx])
            },
            'bollinger_bands': {
                'upper': float(bb_upper.iloc[latest_idx]),
                'middle': float(bb_middle.iloc[latest_idx]),
                'lower': float(bb_lower.iloc[latest_idx]),
                'width': float(self.data['BB_Width'].iloc[latest_idx]),
                'signal': self.data['BB_Signal'].iloc[latest_idx],
                'interpretation': self._interpret_bb(current_price, bb_upper.iloc[latest_idx], bb_lower.iloc[latest_idx])
            },
            'support_resistance': support_resistance,
            'volume': volume_analysis,
            'patterns': patterns,
            'sma_20': float(sma_20),
            'sma_50': float(sma_50)
        }
        
        # Generate overall recommendation
        results['recommendation'] = self._generate_recommendation(results)
        
        return results
    
    def _interpret_rsi(self, rsi_value):
        """Interpret RSI value"""
        if pd.isna(rsi_value):
            return "Insufficient data"
        if rsi_value > 70:
            return "Overbought - Consider selling"
        elif rsi_value < 30:
            return "Oversold - Consider buying"
        elif rsi_value > 50:
            return "Bullish momentum"
        else:
            return "Bearish momentum"
    
    def _interpret_macd(self, histogram):
        """Interpret MACD histogram"""
        if histogram > 0:
            return "Bullish momentum - MACD above signal"
        elif histogram < 0:
            return "Bearish momentum - MACD below signal"
        else:
            return "Neutral"
    
    def _interpret_bb(self, price, upper, lower):
        """Interpret Bollinger Bands position"""
        if price >= upper:
            return "Price at upper band - Overbought condition"
        elif price <= lower:
            return "Price at lower band - Oversold condition"
        else:
            pct = (price - lower) / (upper - lower) * 100
            return f"Price at {pct:.0f}% of band range"
    
    def _generate_recommendation(self, results):
        """
        Generate overall trading recommendation based on all indicators
        """
        buy_signals = 0
        sell_signals = 0
        
        # RSI signals
        if results['rsi']['signal'] == 'Oversold':
            buy_signals += 2
        elif results['rsi']['signal'] == 'Overbought':
            sell_signals += 2
        
        # MACD signals
        if results['macd']['signal'] == 'Buy':
            buy_signals += 2
        elif results['macd']['signal'] == 'Sell':
            sell_signals += 2
        
        # Bollinger Bands
        if results['bollinger_bands']['signal'] == 'Oversold':
            buy_signals += 1
        elif results['bollinger_bands']['signal'] == 'Overbought':
            sell_signals += 1
        
        # Trend
        if 'Uptrend' in results['trend']:
            buy_signals += 1
        elif 'Downtrend' in results['trend']:
            sell_signals += 1
        
        # Volume
        if results['volume']['volume_trend'] == 'Increasing' and buy_signals > sell_signals:
            buy_signals += 1
        
        # Generate recommendation
        if buy_signals > sell_signals + 2:
            return {
                'action': 'Strong Buy',
                'confidence': min(95, buy_signals * 15),
                'reason': f'Multiple bullish signals detected ({buy_signals} buy vs {sell_signals} sell signals)'
            }
        elif buy_signals > sell_signals:
            return {
                'action': 'Buy',
                'confidence': min(80, buy_signals * 12),
                'reason': f'Bullish indicators outweigh bearish ({buy_signals} buy vs {sell_signals} sell signals)'
            }
        elif sell_signals > buy_signals + 2:
            return {
                'action': 'Strong Sell',
                'confidence': min(95, sell_signals * 15),
                'reason': f'Multiple bearish signals detected ({sell_signals} sell vs {buy_signals} buy signals)'
            }
        elif sell_signals > buy_signals:
            return {
                'action': 'Sell',
                'confidence': min(80, sell_signals * 12),
                'reason': f'Bearish indicators outweigh bullish ({sell_signals} sell vs {buy_signals} buy signals)'
            }
        else:
            return {
                'action': 'Hold',
                'confidence': 50,
                'reason': 'Mixed signals - Wait for clearer trend'
            }

    def get_data_with_indicators(self):
        """Return dataframe with all calculated indicators"""
        return self.data


# Helper function to use with existing prediction system
def analyze_stock_technical(stock_symbol):
    """
    Convenience function to analyze stock with technical indicators
    
    Parameters:
    - stock_symbol: Stock ticker symbol
    
    Returns:
    - Dictionary with all technical analysis
    """
    from utils.data_fetch import fetch_stock_data
    
    # Fetch data
    stock_data = fetch_stock_data(stock_symbol, period='1y')
    
    if stock_data is None or stock_data.empty:
        return None
    
    # Calculate indicators
    ti = TechnicalIndicators(stock_data)
    results = ti.calculate_all_indicators()
    
    return results


if __name__ == '__main__':
    # Test the indicators
    from utils.data_fetch import fetch_stock_data
    
    print("Testing Technical Indicators...")
    print("=" * 60)
    
    # Test with a stock
    stock = "RELIANCE.NS"
    print(f"\nAnalyzing {stock}...")
    
    data = fetch_stock_data(stock, period='1y')
    if data is not None:
        ti = TechnicalIndicators(data)
        results = ti.calculate_all_indicators()
        
        print(f"\nCurrent Price: ₹{results['current_price']:.2f}")
        print(f"Trend: {results['trend']}")
        print(f"\nRSI: {results['rsi']['value']:.2f} - {results['rsi']['signal']}")
        print(f"MACD Signal: {results['macd']['signal']}")
        print(f"Bollinger Bands: {results['bollinger_bands']['signal']}")
        print(f"\nRecommendation: {results['recommendation']['action']}")
        print(f"Confidence: {results['recommendation']['confidence']}%")
        print(f"Reason: {results['recommendation']['reason']}")
        
        if results['patterns']:
            print(f"\nRecent Patterns:")
            for pattern in results['patterns'][-3:]:
                print(f"  - {pattern['pattern']} ({pattern['type']})")
    
    print("\n" + "=" * 60)
    print("Technical Indicators Module Ready!")