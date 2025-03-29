# src/utils.py

import os
import pandas as pd
from datetime import datetime
import time
import functools
import random

def log_prediction(signal, confidence, rsi, price, source="live"):
    if signal not in ["LONG", "SHORT", "HOLD", "FILTERED"]:
        print(f"⚠️ Invalid signal: {signal}. Not logging.")
        return

    os.makedirs("logs", exist_ok=True)
    log_path = "logs/confidence_log.csv"

    try:
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

    except Exception as e:
        print(f"❌ Failed to log prediction: {e}")


# ✅ Retry wrapper for fault-tolerant ops
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

# ✅ Model & Scaler Safety Check
def model_artifacts_exist():
    try:
        model_path_file = "models/model_latest_path.txt"
        if not os.path.exists(model_path_file):
            print("❌ model_latest_path.txt not found.")
            return False
        with open(model_path_file, "r") as f:
            model_path = f.read().strip()
        if not os.path.exists(model_path):
            print(f"❌ Model file not found at {model_path}")
            return False
        scalers = [f for f in os.listdir("models") if f.endswith(".save")]
        if not scalers:
            print("❌ No scaler file found.")
            return False
        return True
    except Exception as e:
        print(f"❌ Model artifact check failed: {e}")
        return False
