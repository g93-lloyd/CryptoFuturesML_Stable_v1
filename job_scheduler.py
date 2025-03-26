# job_schedular.py — Scheduled retraining, drift monitoring, summaries

import schedule
import time
from datetime import datetime
import os
from src.retraining_pipeline import retrain_pipeline
from src.trade_simulator import simulate_trade_pnl
from src.daily_summary import send_daily_summary
from src.monitoring import drift_detected
from src.report_generator import generate_daily_report
from src.alert_manager import check_critical_alerts

# Ensure logs directory exists
os.makedirs("logs", exist_ok=True)
log_file = "logs/retrain_log.txt"

def retrain_job_if_drift():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        if drift_detected():
            retrain_pipeline(versioned=True)
            msg = f"[{timestamp}] 🔁 Drift detected → Retraining triggered.\n"
        else:
            msg = f"[{timestamp}] ✅ No significant drift. No retraining.\n"
    except Exception as e:
        msg = f"[{timestamp}] ❌ Drift check/retraining failed: {str(e)}\n"

    with open(log_file, "a") as f:
        f.write(msg)
    print(msg.strip())

# Scheduled Tasks
schedule.every().monday.at("07:00").do(retrain_job_if_drift)       # Weekly check
schedule.every().day.at("19:50").do(simulate_trade_pnl)            # Daily PnL
schedule.every().day.at("20:00").do(send_daily_summary)            # Telegram
schedule.every().day.at("20:10").do(generate_daily_report)         # Report Generator
schedule.every().day.at("20:15").do(check_critical_alerts)         # Critical alerts

print("📅 Scheduler started. Waiting for scheduled jobs...")

while True:
    schedule.run_pending()
    time.sleep(60)
