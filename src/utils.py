# src/utils.py

import os
import pandas as pd
from datetime import datetime
import time
import functools
import random

# ✅ Log prediction to confidence log (and optionally to prediction log)
def log_prediction(signal, confidence, rsi, price, source="live"):
    os.makedirs("logs", exist_ok=True)

    row = {
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "signal": signal,
        "confidence": round(confidence, 4),
        "rsi": round(rsi, 2),
        "price": round(price, 2),
        "source": source
    }

    # ✅ Confidence log (used for visualization)
    conf_path = "logs/confidence_log.csv"
    if os.path.exists(conf_path):
        pd.DataFrame([row]).to_csv(conf_path, mode="a", header=False, index=False)
    else:
        pd.DataFrame([row]).to_csv(conf_path, index=False)

    # ✅ Prediction log (optional extended logging)
    pred_path = "logs/prediction_log.csv"
    if os.path.exists(pred_path):
        pd.DataFrame([row]).to_csv(pred_path, mode="a", header=False, index=False)
    else:
        pd.DataFrame([row]).to_csv(pred_path, index=False)

# ✅ Retry wrapper for unstable functions (e.g., APIs)
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

# ✅ Safety check: verify model + scaler exist
def model_artifacts_exist():
    try:
        # Check latest path tracker
        model_tracker = "models/model_latest_path.txt"
        if not os.path.exists(model_tracker):
            print("❌ model_latest_path.txt not found.")
            return False

        with open(model_tracker, "r") as f:
            model_path = f.read().strip()
        if not os.path.exists(model_path):
            print(f"❌ Model file not found: {model_path}")
            return False

        # Check at least one .save file exists for scaler
        scaler_exists = any(fname.endswith(".save") for fname in os.listdir("models"))
        if not scaler_exists:
            print("❌ No scaler file found in models/")
            return False

        return True

    except Exception as e:
        print(f"❌ model_artifacts_exist check failed: {e}")
        return False
