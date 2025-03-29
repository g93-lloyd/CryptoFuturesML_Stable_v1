# src/live_trading_engine.py

import numpy as np
import os
import joblib
import pandas as pd
from keras.models import load_model
from datetime import datetime

from src.feature_engineering import add_technical_indicators, merge_sentiment
from src.market_data_collector import fetch_ohlcv
from src.sentiment_pipeline import fetch_twitter_sentiment
from src.monitoring import log_trade
from src.telegram_alerts import send_alert
from src.utils import log_prediction

SILENT_MODE = False
CONFIDENCE_LOG = "logs/confidence_log.csv"

# ✅ Initialize log file if it doesn't exist
def init_confidence_log():
    os.makedirs("logs", exist_ok=True)
    if not os.path.exists(CONFIDENCE_LOG):
        with open(CONFIDENCE_LOG, "w") as f:
            f.write("timestamp,signal,confidence,rsi,price\n")

# 🔍 Log confidence data
def log_confidence(signal, confidence, rsi, price):
    init_confidence_log()
    row = {
        "timestamp": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
        "signal": signal,
        "confidence": round(confidence, 4),
        "rsi": round(rsi, 2),
        "price": round(price, 2)
    }
    df = pd.DataFrame([row])
    df.to_csv(CONFIDENCE_LOG, mode='a', header=False, index=False)

# ✅ Load latest model path from tracker
def get_latest_model_path():
    with open("models/model_latest_path.txt", "r") as f:
        path = f.read().strip()
    if not os.path.exists(path):
        raise FileNotFoundError(f"❌ Model file not found: {path}")
    return path

# ✅ Load latest scaler path from tracker
def get_latest_scaler_path():
    scaler_dir = "models/"
    scalers = [f for f in os.listdir(scaler_dir) if f.endswith(".save")]
    if not scalers:
        raise FileNotFoundError("❌ No scaler found in /models.")
    scalers.sort(reverse=True)
    return os.path.join(scaler_dir, scalers[0])

# 🔮 Prediction Logic
def predict_and_trade(return_result=False):
    try:
        model_path = get_latest_model_path()
        scaler_path = get_latest_scaler_path()
        model = load_model(model_path)
        scaler = joblib.load(scaler_path)

        df = fetch_ohlcv("BTC/USDT", limit=100)
        df = add_technical_indicators(df)
        sentiment = fetch_twitter_sentiment()
        df = merge_sentiment(df, sentiment)
        df = df.dropna().reset_index(drop=True)

        features = ['rsi_14', 'ema_21', 'macd', 'sentiment']
        X = df[features].values
        X_scaled = scaler.transform(X)

        window_size = 10
        input_data = np.expand_dims(X_scaled[-window_size:], axis=0)
        prediction = model.predict(input_data, verbose=0)
        confidence = float(prediction[0][0])

        latest_rsi = df['rsi_14'].iloc[-1]
        current_price = df['close'].iloc[-1]

        # Map confidence to signal
        if confidence > 0.6:
            signal = "LONG"
        elif confidence < 0.4:
            signal = "SHORT"
        else:
            signal = "HOLD"

        # ✅ Log confidence always
        log_confidence(signal, confidence, latest_rsi, current_price)

        # Trade filtering
        allow_trade = False
        if signal == "LONG" and latest_rsi < 30 and confidence > 0.7:
            allow_trade = True
        elif signal == "SHORT" and latest_rsi > 70 and confidence > 0.7:
            allow_trade = True

        # Log prediction
        log_prediction(
            signal if allow_trade else "FILTERED",
            confidence,
            latest_rsi,
            current_price,
            source="live"
        )

        # Execute if approved
        if allow_trade:
            log_trade(signal, confidence)
            if not SILENT_MODE:
                send_alert(f"🚨 Signal: {signal}\n📊 RSI: {latest_rsi:.2f}\n⚡ Confidence: {confidence:.2%}")
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
