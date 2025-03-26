# src/alert_manager.py

import os
import pandas as pd
from datetime import datetime, timedelta
import requests
from src.telegram_alerts import send_alert
from src.config import API_TOKEN

# Thresholds and Endpoints
CRITICAL_BALANCE_THRESHOLD = 500           # 🚨 Minimum allowed balance
INACTIVITY_HOURS = 12                      # ⏰ Alert if no trades in this time
PREDICT_ENDPOINT = "http://localhost:8000/predict"  # FastAPI health check
MODEL_PATH_FILE = "models/model_latest_path.txt"    # Verifies model path


def check_critical_alerts():
    alerts_triggered = []

    # 🔁 Retraining failures
    retrain_log = "logs/retrain_log.txt"
    if os.path.exists(retrain_log):
        with open(retrain_log, "r") as f:
            lines = f.readlines()
            if lines and "❌" in lines[-1]:
                alerts_triggered.append("❗ Retraining failed:\n" + lines[-1].strip())

    # 💰 Balance check
    position_log = "logs/virtual_positions.csv"
    if os.path.exists(position_log):
        df = pd.read_csv(position_log)
        if not df.empty:
            last_balance = df["balance_after"].iloc[-1]
            if last_balance < CRITICAL_BALANCE_THRESHOLD:
                alerts_triggered.append(f"⚠️ Balance critically low: ${last_balance:.2f}")

            # ⏳ Inactivity alert
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            latest_trade_time = df["timestamp"].max()
            hours_since_last = (datetime.utcnow() - latest_trade_time).total_seconds() / 3600
            if hours_since_last > INACTIVITY_HOURS:
                alerts_triggered.append(f"⏳ No trades in the last {hours_since_last:.1f} hours.")

    # 🧠 Model version mismatch
    if os.path.exists(MODEL_PATH_FILE):
        with open(MODEL_PATH_FILE) as f:
            expected_path = f.read().strip()
        if not os.path.exists(expected_path):
            alerts_triggered.append(f"🔁 Live model missing or version mismatch:\n{expected_path}")

    # 🔌 API Uptime Check
    try:
        res = requests.get(PREDICT_ENDPOINT, headers={"Authorization": f"Bearer {API_TOKEN}"}, timeout=5)
        if res.status_code != 200:
            alerts_triggered.append(f"❌ API /predict endpoint returned status {res.status_code}")
    except Exception as e:
        alerts_triggered.append(f"❌ API /predict unreachable: {str(e)}")

    # Send alert if any triggered
    if alerts_triggered:
        alert_msg = "🚨 CryptoFuturesML — Critical Alert(s):\n\n" + "\n\n".join(alerts_triggered)
        send_alert(alert_msg)
        print("📤 Critical alert sent.")
    else:
        print("✅ All system checks passed.")
