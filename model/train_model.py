import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
import pickle
import os

def train_linear_regression(X_train, y_train, X_test, y_test):
    """Train and evaluate Linear Regression model"""
    print("Training Linear Regression...")
    
    # Reshape data for Linear Regression (needs 2D input)
    X_train_lr = X_train.reshape(X_train.shape[0], -1)
    X_test_lr = X_test.reshape(X_test.shape[0], -1)
    
    # Train model
    model = LinearRegression()
    model.fit(X_train_lr, y_train)
    
    # Predictions
    train_pred = model.predict(X_train_lr)
    test_pred = model.predict(X_test_lr)
    
    # Metrics
    metrics = {
        'train_rmse': np.sqrt(mean_squared_error(y_train, train_pred)),
        'test_rmse': np.sqrt(mean_squared_error(y_test, test_pred)),
        'train_mae': mean_absolute_error(y_train, train_pred),
        'test_mae': mean_absolute_error(y_test, test_pred),
        'train_r2': r2_score(y_train, train_pred),
        'test_r2': r2_score(y_test, test_pred)
    }
    
    return model, test_pred, metrics

def train_random_forest(X_train, y_train, X_test, y_test):
    """Train and evaluate Random Forest model"""
    print("Training Random Forest...")
    
    # Reshape data for Random Forest
    X_train_rf = X_train.reshape(X_train.shape[0], -1)
    X_test_rf = X_test.reshape(X_test.shape[0], -1)
    
    # Train model
    model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X_train_rf, y_train)
    
    # Predictions
    train_pred = model.predict(X_train_rf)
    test_pred = model.predict(X_test_rf)
    
    # Metrics
    metrics = {
        'train_rmse': np.sqrt(mean_squared_error(y_train, train_pred)),
        'test_rmse': np.sqrt(mean_squared_error(y_test, test_pred)),
        'train_mae': mean_absolute_error(y_train, train_pred),
        'test_mae': mean_absolute_error(y_test, test_pred),
        'train_r2': r2_score(y_train, train_pred),
        'test_r2': r2_score(y_test, test_pred)
    }
    
    return model, test_pred, metrics

def train_lstm(X_train, y_train, X_test, y_test):
    """Train and evaluate LSTM model"""
    print("Training LSTM...")
    
    # Reshape data for LSTM (samples, timesteps, features)
    X_train_lstm = X_train.reshape((X_train.shape[0], X_train.shape[1], 1))
    X_test_lstm = X_test.reshape((X_test.shape[0], X_test.shape[1], 1))
    
    # Build LSTM model
    model = Sequential([
        LSTM(50, return_sequences=True, input_shape=(X_train.shape[1], 1)),
        Dropout(0.2),
        LSTM(50, return_sequences=False),
        Dropout(0.2),
        Dense(25),
        Dense(1)
    ])
    
    # Compile model
    model.compile(optimizer=Adam(learning_rate=0.001), loss='mean_squared_error')
    
    # Train model
    history = model.fit(
        X_train_lstm, y_train,
        batch_size=32,
        epochs=50,
        validation_split=0.1,
        verbose=0
    )
    
    # Predictions
    train_pred = model.predict(X_train_lstm, verbose=0).flatten()
    test_pred = model.predict(X_test_lstm, verbose=0).flatten()
    
    # Metrics
    metrics = {
        'train_rmse': np.sqrt(mean_squared_error(y_train, train_pred)),
        'test_rmse': np.sqrt(mean_squared_error(y_test, test_pred)),
        'train_mae': mean_absolute_error(y_train, train_pred),
        'test_mae': mean_absolute_error(y_test, test_pred),
        'train_r2': r2_score(y_train, train_pred),
        'test_r2': r2_score(y_test, test_pred)
    }
    
    return model, test_pred, metrics

def plot_predictions(y_test, predictions_dict, stock_symbol):
    """Create visualization comparing actual vs predicted prices"""
    plt.figure(figsize=(14, 8))
    
    # Plot actual prices
    plt.plot(y_test, label='Actual Price', color='black', linewidth=2)
    
    # Plot predictions from each model
    colors = ['blue', 'green', 'red']
    for (model_name, pred), color in zip(predictions_dict.items(), colors):
        plt.plot(pred, label=f'{model_name} Prediction', color=color, alpha=0.7)
    
    plt.title(f'{stock_symbol} - Stock Price Prediction Comparison', fontsize=16)
    plt.xlabel('Time Steps', fontsize=12)
    plt.ylabel('Normalized Price', fontsize=12)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    # Save plot
    plot_path = f'static/plots/{stock_symbol}_prediction.png'
    plt.savefig(plot_path, dpi=100, bbox_inches='tight')
    plt.close()
    
    return plot_path

def predict_next_7_days(model, model_name, last_sequence, scaler, feature_names):
    """
    Predict next 7 days of stock prices
    
    Parameters:
    - model: Trained model object
    - model_name: Name of the model
    - last_sequence: Last sequence from test data
    - scaler: Fitted scaler
    - feature_names: List of feature names
    
    Returns:
    - array: 7-day predictions in original scale
    """
    # Get the last 60 days of data
    current_sequence = last_sequence[-1].copy()
    predictions = []
    
    for _ in range(7):
        if model_name == 'LSTM':
            # LSTM prediction
            sequence_reshaped = current_sequence.reshape(1, len(current_sequence), 1)
            next_pred = model.predict(sequence_reshaped, verbose=0)[0][0]
        else:
            # Linear Regression or Random Forest
            sequence_reshaped = current_sequence.reshape(1, -1)
            next_pred = model.predict(sequence_reshaped)[0]
        
        predictions.append(next_pred)
        
        # Update sequence for next prediction
        current_sequence = np.roll(current_sequence, -1)
        current_sequence[-1] = next_pred
    
    # Convert to original scale
    close_idx = feature_names.index('Close')
    dummy = np.zeros((len(predictions), len(feature_names)))
    dummy[:, close_idx] = predictions
    denormalized = scaler.inverse_transform(dummy)
    
    return denormalized[:, close_idx]

def plot_future_predictions(future_predictions, stock_symbol):
    """
    Create a chart showing 7-day future predictions with dates and prices
    
    Parameters:
    - future_predictions: Array of 7 predicted values
    - stock_symbol: Stock ticker symbol
    """
    from datetime import datetime, timedelta
    import matplotlib.dates as mdates
    
    plt.figure(figsize=(14, 7))
    
    # Create dates for next 7 days (excluding weekends for trading days)
    today = datetime.now()
    future_dates = []
    current_date = today
    
    while len(future_dates) < 7:
        current_date += timedelta(days=1)
        # Skip weekends (5=Saturday, 6=Sunday)
        if current_date.weekday() < 5:
            future_dates.append(current_date)
    
    # Format dates for display
    date_labels = [d.strftime('%Y-%m-%d') for d in future_dates]
    
    # Create the plot with dates on x-axis
    fig, ax = plt.subplots(figsize=(14, 7))
    
    # Plot with dotted line style
    ax.plot(future_dates, future_predictions, 'o--', color='#667eea', linewidth=2.5, 
             markersize=12, label=f'Predicted Price (₹)', markerfacecolor='#667eea', 
             markeredgewidth=2, markeredgecolor='#667eea', linestyle='--', dashes=(5, 3))
    
    # Fill area under curve with gradient effect
    ax.fill_between(future_dates, future_predictions, alpha=0.15, color='#667eea')
    
    # Add price labels on points with better formatting
    for i, (date, value) in enumerate(zip(future_dates, future_predictions)):
        # Add price label above each point
        ax.text(date, value, f'₹{value:.2f}', 
               ha='center', va='bottom', fontsize=10, fontweight='bold',
               bbox=dict(boxstyle='round,pad=0.5', facecolor='white', 
                        edgecolor='#667eea', alpha=0.8))
    
    # Format x-axis to show dates nicely
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.set_major_locator(mdates.DayLocator())
    plt.xticks(rotation=45, ha='right')
    
    # Add grid with light styling
    ax.grid(True, alpha=0.2, linestyle='--', linewidth=0.5, color='gray')
    ax.set_axisbelow(True)
    
    # Styling
    ax.set_title(f'{stock_symbol} - AI Price Predictions (Next 7 Days)', 
                fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Date', fontsize=12, fontweight='bold')
    ax.set_ylabel('Predicted Price (₹)', fontsize=12, fontweight='bold')
    
    # Add legend with better styling
    legend = ax.legend(loc='upper left', fontsize=11, framealpha=0.9)
    legend.get_frame().set_facecolor('white')
    legend.get_frame().set_edgecolor('#667eea')
    
    # Set background color
    ax.set_facecolor('#f8f9ff')
    fig.patch.set_facecolor('white')
    
    # Add price range info
    min_price = min(future_predictions)
    max_price = max(future_predictions)
    price_range = max_price - min_price
    
    # Add text box with prediction summary
    textstr = f'Range: ₹{min_price:.2f} - ₹{max_price:.2f}\nVariation: ₹{price_range:.2f}'
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
    ax.text(0.98, 0.02, textstr, transform=ax.transAxes, fontsize=10,
            verticalalignment='bottom', horizontalalignment='right', bbox=props)
    
    # Adjust layout to prevent label cutoff
    plt.tight_layout()
    
    # Save plot
    plot_path = f'static/plots/{stock_symbol}_future_7days.png'
    plt.savefig(plot_path, dpi=120, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f"Future 7-day prediction chart saved: {plot_path}")
    print(f"Predicted prices: {[f'₹{p:.2f}' for p in future_predictions]}")
    return plot_path

def train_and_predict(processed_data, stock_symbol):
    """
    Train all models, compare performance, and return best predictions
    
    Parameters:
    - processed_data: Dictionary from preprocess_data()
    - stock_symbol: Stock ticker symbol
    
    Returns:
    - Dictionary with results
    """
    X_train = processed_data['X_train']
    X_test = processed_data['X_test']
    y_train = processed_data['y_train']
    y_test = processed_data['y_test']
    
    # Train all models
    lr_model, lr_pred, lr_metrics = train_linear_regression(X_train, y_train, X_test, y_test)
    rf_model, rf_pred, rf_metrics = train_random_forest(X_train, y_train, X_test, y_test)
    lstm_model, lstm_pred, lstm_metrics = train_lstm(X_train, y_train, X_test, y_test)
    
    # Compare models based on test RMSE
    models_performance = {
        'Linear Regression': lr_metrics['test_rmse'],
        'Random Forest': rf_metrics['test_rmse'],
        'LSTM': lstm_metrics['test_rmse']
    }
    
    best_model = min(models_performance, key=models_performance.get)
    
    # Select best predictions
    predictions_map = {
        'Linear Regression': lr_pred,
        'Random Forest': rf_pred,
        'LSTM': lstm_pred
    }
    
    best_predictions = predictions_map[best_model]
    
    # Select best model object for future predictions
    best_model_obj = {
        'Linear Regression': lr_model,
        'Random Forest': rf_model,
        'LSTM': lstm_model
    }[best_model]
    
    # Generate future 7-day predictions
    future_predictions = predict_next_7_days(
        best_model_obj, 
        best_model, 
        X_test, 
        processed_data['scaler'],
        processed_data['feature_names']
    )
    
    # Generate future dates (skip weekends)
    from datetime import datetime, timedelta
    today = datetime.now()
    future_dates = []
    current_date = today
    
    while len(future_dates) < 7:
        current_date += timedelta(days=1)
        if current_date.weekday() < 5:  # Skip weekends
            future_dates.append(current_date.strftime('%Y-%m-%d'))
    
    # Create visualization
    plot_path = plot_predictions(
        y_test,
        {
            'Linear Regression': lr_pred,
            'Random Forest': rf_pred,
            'LSTM': lstm_pred
        },
        stock_symbol
    )
    
    # Create 7-day future prediction chart
    plot_future_predictions(future_predictions, stock_symbol)
    
    # Save best model
    model_path = f'model/saved_model_{stock_symbol}.pkl'
    if best_model == 'LSTM':
        lstm_model.save(f'model/saved_model_{stock_symbol}.h5')
    else:
        with open(model_path, 'wb') as f:
            pickle.dump(best_model_obj, f)
    
    print(f"\nBest Model: {best_model}")
    print(f"Test RMSE: {models_performance[best_model]:.6f}")
    
    return {
        'best_model': best_model,
        'predictions': best_predictions,
        'actual': y_test,
        'future_predictions': future_predictions,
        'future_dates': future_dates,
        'metrics': {
            'Linear Regression': lr_metrics,
            'Random Forest': rf_metrics,
            'LSTM': lstm_metrics
        },
        'plot_path': plot_path,
        'scaler': processed_data['scaler'],
        'feature_names': processed_data['feature_names']
    }

if __name__ == "__main__":
    # Test the training pipeline
    from utils.data_fetch import fetch_stock_data
    from utils.preprocess import preprocess_data
    
    stock_data = fetch_stock_data("AAPL")
    if stock_data is not None:
        processed = preprocess_data(stock_data)
        result = train_and_predict(processed, "AAPL")
        print("\nTraining completed successfully!")