# src/utils.py

import os
import pandas as pd
from datetime import datetime
import time
import functools
import random

def log_prediction(signal, confidence, rsi, price, source="live"):
    os.makedirs("logs", exist_ok=True)

    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    # Unified log row
    log_row = {
        "timestamp": timestamp,
        "signal": signal,
        "confidence": round(confidence, 4),
        "rsi": round(rsi, 2),
        "price": round(price, 2),
        "source": source
    }

    # ✅ Log to full prediction log
    prediction_log_path = "logs/prediction_log.csv"
    pd.DataFrame([log_row]).to_csv(
        prediction_log_path,
        mode="a" if os.path.exists(prediction_log_path) else "w",
        header=not os.path.exists(prediction_log_path),
        index=False
    )

    # ✅ Log subset for confidence visualization
    confidence_log_path = "logs/confidence_log.csv"
    confidence_entry = {
        "timestamp": timestamp,
        "signal": signal,
        "confidence": round(confidence, 4),
        "rsi": round(rsi, 2),
        "price": round(price, 2)
    }
    pd.DataFrame([confidence_entry]).to_csv(
        confidence_log_path,
        mode="a" if os.path.exists(confidence_log_path) else "w",
        header=not os.path.exists(confidence_log_path),
        index=False
    )

# Retry wrapper used elsewhere
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
