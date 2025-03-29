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
                    msg = f"\u26a0\ufe0f Attempt {attempts} failed: {e}"
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

    log_specs = {
        "logs/confidence_log.csv": "timestamp,signal,confidence,rsi,price,source\n",
        "logs/trade_log.csv": "Time,Signal,Price,Action,PnL,Balance\n",
        "logs/virtual_positions.csv": "timestamp,entry_time,signal,entry_price,exit_price,pnl_percent,balance_after\n",
        "logs/daily_log.txt": "# Daily Trade Summary Log\n\n"
    }

    for path, header in log_specs.items():
        if not os.path.exists(path) or os.path.getsize(path) == 0:
            with open(path, "w") as f:
                f.write(header)

# === Inject Test Row into Virtual Positions (for dashboard init) ===
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

# === Write a Daily Log Summary to File ===
def write_daily_log():
    path = "logs/virtual_positions.csv"
    if not os.path.exists(path):
        return

    try:
        df = pd.read_csv(path, parse_dates=['timestamp'])
        today = datetime.utcnow().date()
        today_trades = df[df['timestamp'].dt.date == today]

        if today_trades.empty:
            return

        summary = f"\n[{datetime.utcnow().strftime('%Y-%m-%d')}]\n"
        summary += f"Total Trades: {len(today_trades)}\n"
        summary += f"Avg PnL: {today_trades['pnl_percent'].mean():.2f}%\n"
        summary += f"Win Rate: {(today_trades['pnl_percent'] > 0).mean() * 100:.1f}%\n"

        with open("logs/daily_log.txt", "a") as f:
            f.write(summary)

    except Exception as e:
        print(f"❌ Failed to write daily log: {e}")

def generate_daily_summary_log():
    try:
        df = pd.read_csv("logs/virtual_positions.csv", parse_dates=["timestamp"])
        if df.empty:
            print("📭 No trades to summarize.")
            return

        df['date'] = df['timestamp'].dt.date
        summary = df.groupby('date').agg({
            'pnl_percent': ['count', 'mean', lambda x: (x > 0).mean() * 100]
        })
        summary.columns = ['Trades', 'Avg_PnL(%)', 'Win_Rate(%)']
        summary.reset_index(inplace=True)

        log_path = "logs/daily_log.txt"
        with open(log_path, "w") as f:
            f.write("📅 Daily Trading Summary\n")
            f.write("──────────────────────────────\n")
            for _, row in summary.iterrows():
                f.write(
                    f"{row['date']} | Trades: {int(row['Trades'])} | "
                    f"Avg PnL: {row['Avg_PnL(%)']:.2f}% | "
                    f"Win Rate: {row['Win_Rate(%)']:.2f}%\n"
                )
        print("✅ Daily summary written to logs/daily_log.txt")
    except Exception as e:
        print(f"❌ Failed to generate daily log: {e}")
