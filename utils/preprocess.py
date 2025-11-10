import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

def preprocess_data(stock_data):
    """
    Preprocess stock data for machine learning
    
    Parameters:
    - stock_data: DataFrame with stock data
    
    Returns:
    - Dictionary with preprocessed data
    """
    # Make a copy to avoid modifying original data
    data = stock_data.copy()
    
    # 1. Handle missing values
    print(f"Missing values before cleaning: {data.isnull().sum().sum()}")
    
    # Forward fill missing values
    data.fillna(method='ffill', inplace=True)
    
    # Backward fill any remaining missing values
    data.fillna(method='bfill', inplace=True)
    
    print(f"Missing values after cleaning: {data.isnull().sum().sum()}")
    
    # 2. Create additional features
    # Moving averages
    data['MA_7'] = data['Close'].rolling(window=7).mean()
    data['MA_21'] = data['Close'].rolling(window=21).mean()
    
    # Daily returns
    data['Daily_Return'] = data['Close'].pct_change()
    
    # Volatility (standard deviation of returns)
    data['Volatility'] = data['Daily_Return'].rolling(window=7).std()
    
    # Price momentum
    data['Momentum'] = data['Close'] - data['Close'].shift(4)
    
    # Drop rows with NaN values created by rolling operations
    data.dropna(inplace=True)
    
    # 3. Normalize numerical features
    scaler = MinMaxScaler(feature_range=(0, 1))
    
    # Features to normalize
    features_to_scale = ['Open', 'High', 'Low', 'Close', 'Volume', 
                         'MA_7', 'MA_21', 'Volatility', 'Momentum']
    
    # Create scaled features
    scaled_data = data.copy()
    scaled_data[features_to_scale] = scaler.fit_transform(data[features_to_scale])
    
    # 4. Prepare data for models
    # Use previous 60 days to predict next day
    sequence_length = 60
    
    X = []
    y = []
    
    close_data = scaled_data['Close'].values
    
    for i in range(sequence_length, len(close_data)):
        X.append(close_data[i-sequence_length:i])
        y.append(close_data[i])
    
    X = np.array(X)
    y = np.array(y)
    
    # Split data into training and testing sets (80-20 split)
    split_idx = int(len(X) * 0.8)
    
    X_train = X[:split_idx]
    X_test = X[split_idx:]
    y_train = y[:split_idx]
    y_test = y[split_idx:]
    
    print(f"Training samples: {len(X_train)}, Testing samples: {len(X_test)}")
    
    return {
        'original_data': data,
        'scaled_data': scaled_data,
        'X_train': X_train,
        'X_test': X_test,
        'y_train': y_train,
        'y_test': y_test,
        'scaler': scaler,
        'feature_names': features_to_scale
    }

def inverse_transform_predictions(predictions, scaler, feature_names):
    """
    Convert normalized predictions back to original scale
    
    Parameters:
    - predictions: Normalized prediction values
    - scaler: Fitted MinMaxScaler object
    - feature_names: List of feature names
    
    Returns:
    - Denormalized predictions
    """
    # Get the index of 'Close' in feature names
    close_idx = feature_names.index('Close')
    
    # Create a dummy array with the same shape as training data
    dummy = np.zeros((len(predictions), len(feature_names)))
    dummy[:, close_idx] = predictions
    
    # Inverse transform
    denormalized = scaler.inverse_transform(dummy)
    
    return denormalized[:, close_idx]

if __name__ == "__main__":
    # Test preprocessing
    from data_fetch import fetch_stock_data
    
    stock_data = fetch_stock_data("AAPL")
    if stock_data is not None:
        processed = preprocess_data(stock_data)
        print("\nPreprocessed data shapes:")
        print(f"X_train: {processed['X_train'].shape}")
        print(f"X_test: {processed['X_test'].shape}")