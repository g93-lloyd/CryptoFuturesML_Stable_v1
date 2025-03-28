# src/live_trading_engine.py

import numpy as np
import os
import joblib
from keras.models import load_model
from datetime import datetime
import pandas as pd

from src.feature_engineering import add_technical_indicators, merge_sentiment
from src.market_data_collector import fetch_ohlcv
from src.sentiment_pipeline import fetch_twitter_sentiment
from src.monitoring import log_trade
from src.telegram_alerts import send_alert
from src.utils import log_prediction

SILENT_MODE = False
CONFIDENCE_LOG_PATH = "logs/confidence_log.csv"

# Load latest model path from tracker
def get_latest_model_path():
    with open("models/model_latest_path.txt", "r") as f:
        path = f.read().strip()
    if not os.path.exists(path):
        raise FileNotFoundError(f"❌ Model file not found: {path}")
    return path

def get_latest_scaler_path():
    scaler_dir = "models/"
    scalers = [f for f in os.listdir(scaler_dir) if f.endswith(".save")]
    if not scalers:
        raise FileNotFoundError("❌ No scaler found in /models.")
    scalers.sort(reverse=True)
    return os.path.join(scaler_dir, scalers[0])

# Logs confidence data to CSV
def log_confidence(signal, confidence, rsi, price):
    entry = {
        "Time": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
        "Signal": signal,
        "Confidence": confidence,
        "RSI": rsi,
        "Price": price
    }
    os.makedirs("logs", exist_ok=True)
    df = pd.DataFrame([entry])
    if not os.path.exists(CONFIDENCE_LOG_PATH):
        df.to_csv(CONFIDENCE_LOG_PATH, index=False)
    else:
        df.to_csv(CONFIDENCE_LOG_PATH, mode="a", header=False, index=False)

# 🔮 Prediction and optional trade execution
def predict_and_trade(return_result=False):
    try:
        model = load_model(get_latest_model_path())
        scaler = joblib.load(get_latest_scaler_path())

        df = fetch_ohlcv("BTC/USDT", limit=100)
        df = add_technical_indicators(df)
        sentiment = fetch_twitter_sentiment()
        df = merge_sentiment(df, sentiment)
        df = df.dropna().reset_index(drop=True)

        features = ['rsi_14', 'ema_21', 'macd', 'sentiment']
        X = df[features].values
        X_scaled = scaler.transform(X)

        window_size = 10
        latest_window = X_scaled[-window_size:]
        input_data = np.expand_dims(latest_window, axis=0)

        prediction = model.predict(input_data, verbose=0)
        confidence = float(prediction[0][0])
        latest_rsi = df['rsi_14'].iloc[-1]
        current_price = df['close'].iloc[-1]

        if confidence > 0.6:
            signal = "LONG"
        elif confidence < 0.4:
            signal = "SHORT"
        else:
            signal = "HOLD"

        # Filter weak signals
        allow_trade = False
        if signal == "LONG" and latest_rsi < 30 and confidence > 0.7:
            allow_trade = True
        elif signal == "SHORT" and latest_rsi > 70 and confidence > 0.7:
            allow_trade = True

        # 🔍 Log confidence snapshot
        log_confidence(signal, confidence, latest_rsi, current_price)

        # 🧠 Prediction logging
        log_prediction(
            signal if allow_trade else "FILTERED",
            confidence,
            latest_rsi,
            current_price,
            source="live"
        )

        if allow_trade:
            log_trade(signal, confidence)
            if not SILENT_MODE:
                send_alert(
                    f"🚨 Signal: {signal}\n📊 RSI: {latest_rsi:.2f}\n⚡ Confidence: {confidence:.2%}"
                )
            print(f"📢 FINAL Signal: {signal} | RSI: {latest_rsi:.2f} | Confidence: {confidence:.2%}")
            if return_result:
                return signal, confidence
        else:
            print(f"⚠️ Signal filtered: {signal} | RSI: {latest_rsi:.2f} | Confidence: {confidence:.2%}")
            if return_result:
                return "FILTERED", confidence

    except Exception as e:
        print(f"❌ Prediction failed: {e}")
        if return_result:
            return "ERROR", 0.0
