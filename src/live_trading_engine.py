# src/live_trading_engine.py

# Core libraries
import numpy as np
import os
import joblib
from tensorflow.keras.models import load_model
from datetime import datetime

# Project modules
from src.feature_engineering import add_technical_indicators, merge_sentiment  # Adds RSI, MACD, and merges sentiment
from src.market_data_collector import fetch_ohlcv                             # Gets historical OHLCV data
from src.sentiment_pipeline import fetch_twitter_sentiment                   # Collects and scores Twitter sentiment
from src.monitoring import log_trade                                         # Logs trade to trade log
from src.telegram_alerts import send_alert                                   # Sends alerts to Telegram bot
from src.utils import log_prediction                                         # Logs predictions to file

# If set to True, disables Telegram alerts
SILENT_MODE = False

# Utility: Get the latest model file from the models directory
def get_latest_model_path():
    model_dir = "models/"
    models = [f for f in os.listdir(model_dir) if f.endswith(".h5")]
    if not models:
        raise FileNotFoundError("❌ No model found in /models.")
    models.sort(reverse=True)  # Assumes versioning via timestamp
    return os.path.join(model_dir, models[0])

# Utility: Get the latest scaler (used to normalize input features)
def get_latest_scaler_path():
    scaler_dir = "models/"
    scalers = [f for f in os.listdir(scaler_dir) if f.endswith(".save")]
    if not scalers:
        raise FileNotFoundError("❌ No scaler found in /models.")
    scalers.sort(reverse=True)
    return os.path.join(scaler_dir, scalers[0])

# 🔮 Core function: fetch data → preprocess → predict → filter → log/alert
def predict_and_trade(return_result=False):
    try:
        # Load model and scaler
        model_path = get_latest_model_path()
        scaler_path = get_latest_scaler_path()
        model = load_model(model_path)
        scaler = joblib.load(scaler_path)

        # Fetch market data and compute features
        df = fetch_ohlcv("BTC/USDT", limit=100)
        df = add_technical_indicators(df)  # Adds RSI, EMA, MACD, etc.
        sentiment = fetch_twitter_sentiment()  # Get sentiment scores
        df = merge_sentiment(df, sentiment)  # Add sentiment to feature set

        df = df.dropna().reset_index(drop=True)

        # Select features used in model
        features = ['rsi_14', 'ema_21', 'macd', 'sentiment']
        X = df[features].values
        X_scaled = scaler.transform(X)  # Normalize inputs

        # Create a 3D input window (batch_size=1, window_size, features)
        window_size = 10
        latest_window = X_scaled[-window_size:]
        input_data = np.expand_dims(latest_window, axis=0)  # Shape: (1, 10, 4)

        # Get prediction from model (binary classifier: 0 = short, 1 = long)
        prediction = model.predict(input_data, verbose=0)
        confidence = float(prediction[0][0])  # Extract confidence score

        # Get latest indicators
        latest_rsi = df['rsi_14'].iloc[-1]
        current_price = df['close'].iloc[-1]

        # Map confidence to signal
        if confidence > 0.6:
            signal = "LONG"
        elif confidence < 0.4:
            signal = "SHORT"
        else:
            signal = "HOLD"

        # ✅ Smart filter: Only trade on high-confidence + RSI-confirmed signals
        allow_trade = False
        if signal == "LONG" and latest_rsi < 30 and confidence > 0.7:
            allow_trade = True
        elif signal == "SHORT" and latest_rsi > 70 and confidence > 0.7:
            allow_trade = True

        # Log prediction to CSV (whether filtered or not)
        log_prediction(
            signal if allow_trade else "FILTERED",
            confidence,
            latest_rsi,
            current_price,
            source="live"
        )

        # Proceed with "simulated trade" if filter passes
        if allow_trade:
            log_trade(signal, confidence)
            if not SILENT_MODE:
                send_alert(
                    f"🚨 Filtered Signal: {signal}\n📊 RSI: {latest_rsi:.2f}\n⚡ Confidence: {confidence:.2%}"
                )
            print(f"📢 FINAL Signal: {signal} | RSI: {latest_rsi:.2f} | Confidence: {confidence:.2%}")
            if return_result:
                return signal, confidence
        else:
            # Show filtered signal but don't trade
            print(f"⚠️ Signal filtered: {signal} | RSI: {latest_rsi:.2f} | Confidence: {confidence:.2%}")
            if return_result:
                return "FILTERED", confidence

    except Exception as e:
        print(f"❌ Prediction failed: {e}")
        if return_result:
            return "ERROR", 0.0
