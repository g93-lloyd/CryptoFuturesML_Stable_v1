# src/backtest_engine.py

import pandas as pd
import numpy as np
from datetime import timedelta
import joblib
from tensorflow.keras.models import load_model

from src.feature_engineering import add_technical_indicators, merge_sentiment
from src.market_data_collector import fetch_ohlcv
from src.sentiment_pipeline import fetch_twitter_sentiment
from src.backtest_analysis import compute_backtest_metrics, log_backtest_summary

def run_backtest(
    pair="BTC/USDT",
    model_path="models/lstm_model.h5",
    scaler_path="models/scaler.save",
    lookback=10,
    confidence_threshold=0.7,
    rsi_entry=30,
    rsi_exit=70,
    hold_minutes=30,
    limit=1500,
    save_to_file=True,
    strategy_name="LSTM_v1_5m_RSI30_70"
):
    print("📦 Running backtest with strategy + filters...")

    # Load historical OHLCV
    df = fetch_ohlcv(pair, timeframe="5m", limit=limit)
    df = add_technical_indicators(df)

    # Merge mock sentiment
    sentiment_scores = fetch_twitter_sentiment(limit=30)
    df = merge_sentiment(df, sentiment_scores)
    df = df.dropna().reset_index(drop=True)

    # Load model + scaler
    model = load_model(model_path)
    scaler = joblib.load(scaler_path)

    # Prepare features
    features = ['rsi_14', 'ema_21', 'macd', 'sentiment']
    scaled_features = scaler.transform(df[features].values)

    trades = []

    for i in range(lookback, len(df) - int(hold_minutes / 5)):
        window = scaled_features[i - lookback:i]
        input_data = np.expand_dims(window, axis=0)
        prediction = model.predict(input_data, verbose=0)
        confidence = float(prediction[0][0])
        rsi = df['rsi_14'].iloc[i]

        signal = "HOLD"
        if confidence > 0.6:
            signal = "LONG"
        elif confidence < 0.4:
            signal = "SHORT"

        # Apply filter
        allow_trade = False
        if signal == "LONG" and rsi < rsi_entry and confidence > confidence_threshold:
            allow_trade = True
        elif signal == "SHORT" and rsi > rsi_exit and confidence > confidence_threshold:
            allow_trade = True

        if not allow_trade:
            continue

        entry_price = df['close'].iloc[i]
        exit_index = i + int(hold_minutes / 5)
        if exit_index >= len(df):
            continue
        exit_price = df['close'].iloc[exit_index]

        pnl = ((exit_price - entry_price) / entry_price) if signal == "LONG" \
            else ((entry_price - exit_price) / entry_price)

        trades.append({
            "timestamp": df['timestamp'].iloc[i],
            "signal": signal,
            "rsi": rsi,
            "confidence": round(confidence, 4),
            "entry_price": round(entry_price, 2),
            "exit_price": round(exit_price, 2),
            "pnl_percent": round(pnl * 100, 2)
        })

    results = pd.DataFrame(trades)

    if save_to_file:
        results.to_csv("logs/backtest_trades.csv", index=False)
        print(f"✅ Backtest complete. {len(results)} trades saved to logs/backtest_trades.csv")

    # 🔍 Analyze & log strategy performance
    summary = compute_backtest_metrics(results, strategy_name=strategy_name)
    log_backtest_summary(summary)

    return results
