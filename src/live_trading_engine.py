# src/live_trading_engine.py

# Core libraries
import numpy as np
import os
import joblib
from tensorflow.keras.models import load_model
from datetime import datetime

# Project modules
from src.feature_engineering import add_technical_indicators, merge_sentiment
from src.market_data_collector import fetch_ohlcv
from src.sentiment_pipeline import fetch_twitter_sentiment
from src.monitoring import log_trade
from src.telegram_alerts import send_alert
from src.utils import log_prediction

# If set to True, disables Telegram alerts
SILENT_MODE = False

# ✅ Utility: Get the latest .keras model file from the models directory
def get_latest_model_path():
    model_dir = "models/"
    models = [f for f in os.listdir(model_dir) if f.endswith(".keras")]
    if not models:
        raise FileNotFoundError("❌ No .keras model found in /models.")
    models.sort(reverse=True)  # Assumes versioning via timestamp
    return os.path.join(model_dir, models[0])

# ✅ Utility: Get the latest scaler (used to normalize input features)
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
        # ✅ Load model and scaler
        model_path = get_latest_model_path()
        scaler_path = get_latest_scaler_path()
        model = load_model(model_path)
        scaler = joblib.load(scaler_path)

        # 🧠 Fetch market data and compute features
        df = fetch_ohlcv("BTC/USDT", limit=100)
        df = add_technical_indicators(df)
        sentiment = fetch_twitter_sentiment()
        df = merge_sentiment(df, sentiment)

        df = df.dropna().reset_index(drop=True)

        # 🔢 Select features used in model
        features = ['rsi_14', 'ema_21', 'macd', 'sentiment']
        X = df[features].values
        X_scaled = scaler.transform(X)

        # 🪟 Create a 3D input window (batch_size=1, window_size, features)
        window_size = 10
        latest_window = X_scaled[-window_size:]
        input_data = np.expand_dims(latest_window, axis=0)

        # 🤖 Get prediction from model
        prediction = model.predict(input_data, verbose=0)
        confidence = float(prediction[0][0])

        # 🧾 Get latest indicators
        latest_rsi = df['rsi_14'].iloc[-1]
        current_price = df['close'].iloc[-1]

        # 🔁 Map confidence to signal
        if confidence > 0.6:
            signal = "LONG"
        elif confidence < 0.4:
            signal = "SHORT"
        else:
            signal = "HOLD"

        # ✅ Smart filter logic
        allow_trade = False
        if signal == "LONG" and latest_rsi < 30 and confidence > 0.7:
            allow_trade = True
        elif signal == "SHORT" and latest_rsi > 70 and confidence > 0.7:
            allow_trade = True

        # 🪵 Log prediction regardless of trade decision
        log_prediction(
            signal if allow_trade else "FILTERED",
            confidence,
            latest_rsi,
            current_price,
            source="live"
        )

        # 💸 Simulate trade if passed filter
        if allow_trade:
            log_trade(signal, confidence)
            if not SILENT_MODE:
                send_alert(
                    f"\U0001F6A8 Filtered Signal: {signal}\n\U0001F4CA RSI: {latest_rsi:.2f}\n⚡ Confidence: {confidence:.2%}"
                )
            print(f"\U0001F4E2 FINAL Signal: {signal} | RSI: {latest_rsi:.2f} | Confidence: {confidence:.2%}")
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
