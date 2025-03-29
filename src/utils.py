# src/utils.py

import os
import pandas as pd
from datetime import datetime
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
