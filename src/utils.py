# src/utils.py

import os
import pandas as pd
from datetime import datetime
import time
import functools
import random

# 🔍 Logs model prediction decisions for auditing or later analysis
def log_prediction(signal, confidence, rsi, price, source="live"):
    os.makedirs("logs", exist_ok=True)
    log_path = "logs/prediction_log.csv"

    new_row = pd.DataFrame([{
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "signal": signal,
        "confidence": round(confidence, 4),
        "rsi": round(rsi, 2),
        "price": round(price, 2),
        "source": source
    }])

    if os.path.exists(log_path):
        new_row.to_csv(log_path, mode="a", header=False, index=False)
    else:
        new_row.to_csv(log_path, index=False)

# 🛡️ Retry wrapper for resilient external calls (e.g., API or data fetches)
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

# ✅ Ensures trade_log.csv exists with correct headers to prevent dashboard/analyzer crashes
def ensure_trade_log_exists():
    log_path = "logs/trade_log.csv"
    if not os.path.exists(log_path):
        os.makedirs("logs", exist_ok=True)
        with open(log_path, "w") as f:
            f.write("Time,Signal,Price,Action,PnL,Balance\n")
