# src/utils.py

import os
import pandas as pd
from datetime import datetime, timedelta
import time
import functools
import random

# === Log predictions to CSV ===
def log_prediction(signal, confidence, rsi, price, source="live"):
    os.makedirs("logs", exist_ok=True)
    log_path = "logs/confidence_log.csv"

    new_row = pd.DataFrame([{
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "signal": signal,
        "confidence": round(confidence, 4),
        "rsi": round(rsi, 2),
        "price": round(price, 2),
        "source": source
    }])

    if not os.path.exists(log_path):
        new_row.to_csv(log_path, index=False)
    else:
        new_row.to_csv(log_path, mode="a", header=False, index=False)

# === Retry Decorator for Robustness ===
def retry(max_attempts=3, delay=2, backoff=2, jitter=True, logger=None):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            current_delay = delay
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    msg = f"⚠️ Attempt {attempts} failed: {e}"
                    print(msg) if not logger else logger(msg)
                    if attempts == max_attempts:
                        raise
                    sleep_time = current_delay + (random.uniform(0, 1) if jitter else 0)
                    time.sleep(sleep_time)
                    current_delay *= backoff
        return wrapper
    return decorator

# === Safety check for critical files ===
def model_artifacts_exist():
    model_path = "models/model_latest_path.txt"
    if not os.path.exists(model_path):
        return False
    with open(model_path, "r") as f:
        model_file = f.read().strip()
    if not os.path.exists(model_file):
        return False
    scaler_found = any(f.endswith(".save") for f in os.listdir("models/"))
    return scaler_found

# === Log File Initialization ===
def init_log_files():
    os.makedirs("logs", exist_ok=True)

    # Confidence Log
    confidence_path = "logs/confidence_log.csv"
    if not os.path.exists(confidence_path) or os.path.getsize(confidence_path) == 0:
        with open(confidence_path, "w") as f:
            f.write("timestamp,signal,confidence,rsi,price,source\n")

    # Trade Log
    trade_log_path = "logs/trade_log.csv"
    if not os.path.exists(trade_log_path) or os.path.getsize(trade_log_path) == 0:
        with open(trade_log_path, "w") as f:
            f.write("Time,Signal,Price,Action,PnL,Balance\n")

    # Virtual Position Log
    position_log_path = "logs/virtual_positions.csv"
    if not os.path.exists(position_log_path) or os.path.getsize(position_log_path) == 0:
        with open(position_log_path, "w") as f:
            f.write("timestamp,entry_time,signal,entry_price,exit_price,pnl_percent,balance_after\n")

# === Inject Virtual Test Row ===
def inject_virtual_trade_test_row():
    path = "logs/virtual_positions.csv"
    if not os.path.exists(path):
        return
    try:
        df = pd.read_csv(path)
        if df.shape[0] == 0:
            now = datetime.utcnow()
            test_row = pd.DataFrame([{
                "timestamp": now,
                "entry_time": now - timedelta(minutes=15),
                "signal": "LONG",
                "entry_price": 26000,
                "exit_price": 26300,
                "pnl_percent": 1.15,
                "balance_after": 10115.0
            }])
            test_row.to_csv(path, mode="a", header=False, index=False)
            print("✅ Inserted test row into virtual_positions.csv.")
    except Exception as e:
        print(f"⚠️ Could not insert test row: {e}")

# === Daily Summary Log ===
def generate_daily_summary_log():
    try:
        df = pd.read_csv("logs/virtual_positions.csv")
        if df.empty:
            print("📭 No virtual position data found.")
            return

        df['timestamp'] = pd.to_datetime(df['timestamp'])
        today = datetime.utcnow().date()
        today_trades = df[df['timestamp'].dt.date == today]

        if today_trades.empty:
            print("📭 No trades today to summarize.")
            return

        avg_pnl = today_trades['pnl_percent'].mean()
        win_rate = (today_trades['pnl_percent'] > 0).mean() * 100
        trades = len(today_trades)
        balance_end = today_trades['balance_after'].iloc[-1]

        summary = f"""
📘 Daily Summary Log ({today})
──────────────────────────────
📊 Trades: {trades}
📈 Avg PnL: {avg_pnl:.2f}%
🏆 Win Rate: {win_rate:.2f}%
💰 Final Balance: ${balance_end:.2f}
"""
        log_path = "logs/daily_log.txt"
        with open(log_path, "a") as f:
            f.write(summary + "\n")

        print(summary)
        print("✅ Daily summary saved to logs/daily_log.txt")

        # v1.5+ queue: send this summary to Telegram via send_alert()

    except Exception as e:
        print(f"❌ Failed to generate daily log: {e}")
