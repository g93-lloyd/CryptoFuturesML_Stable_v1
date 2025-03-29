# main.py — Unified Command + Live Automation Loop

import sys
import time
import subprocess
from datetime import datetime
import os
import pandas as pd

# Core components
from src.live_trading_engine import predict_and_trade
from src.retraining_pipeline import retrain_pipeline
from src.trade_analyzer import analyze_trade_log
from src.market_data_collector import fetch_ohlcv
from src.position_manager import handle_signal, log_position
from src.cli_dashboard import display_dashboard
from src.confidence_visualizer import (
    plot_confidence_over_time,
    plot_signal_distribution
)
from src.utils import model_artifacts_exist, init_log_files

INTERVAL_SECONDS = 300  # 5 minutes

# ✅ Git Sync Checker
def check_git_sync():
    try:
        subprocess.run(["git", "fetch", "origin"], check=True)
        status = subprocess.check_output(["git", "status", "-uno"]).decode()
        if "behind" in status:
            print("⚠️ WARNING: Local branch is behind origin/main.")
        elif "diverged" in status:
            print("❌ ERROR: Local and remote have diverged.")
        else:
            print("✅ Git is up to date.")
    except Exception as e:
        print(f"❌ Git sync check failed: {e}")

# ✅ Optional: Inject test row only if needed
def inject_test_virtual_trade_if_empty():
    log_path = "logs/virtual_positions.csv"
    if os.path.exists(log_path):
        df = pd.read_csv(log_path)
        if df.empty:
            now = datetime.utcnow()
            test_rows = [
                {
                    "timestamp": now,
                    "entry_time": now - timedelta(minutes=15),
                    "signal": "LONG",
                    "entry_price": 65000.0,
                    "exit_price": 65200.0,
                    "pnl_percent": 0.31,
                    "balance_after": 10310.0
                },
                {
                    "timestamp": now,
                    "entry_time": now - timedelta(minutes=45),
                    "signal": "SHORT",
                    "entry_price": 65200.0,
                    "exit_price": 64800.0,
                    "pnl_percent": 0.61,
                    "balance_after": 10938.0
                }
            ]
            df = pd.DataFrame(test_rows)
            df.to_csv(log_path, index=False)
            print("🧪 2 test trades injected to logs/virtual_positions.csv.")
    else:
        print("⚠️ Trade log file missing — unable to inject test trades.")


# CLI Menu
def menu():
    print("\n🧠 Crypto Futures ML System")
    print("────────────────────────────")
    print("1️⃣  Run Live Prediction & Simulated Trade")
    print("2️⃣  Retrain Model on Latest Data")
    print("3️⃣  Analyze Trade Log Performance")
    print("4️⃣  Start Full Automated Live Loop")
    print("5️⃣  Exit")
    print("6️⃣  Visualize Confidence Over Time")
    print("7️⃣  Show Signal Distribution")
    return input("Select an option (1-7): ")

# 🔁 Live Loop Mode
def run_live_loop():
    print("🚀 Starting live loop (CTRL+C to stop)\n")
    while True:
        try:
            print(f"\n⏳ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} — Running cycle...")
            signal, confidence = predict_and_trade(return_result=True)

            if signal in ["LONG", "SHORT"]:
                df = fetch_ohlcv(limit=1)
                current_price = df["close"].iloc[-1]
                handle_signal(signal=signal, price=current_price)
            else:
                print(f"🔍 No actionable signal: {signal} (confidence: {confidence:.2%})")

            display_dashboard()
            time.sleep(INTERVAL_SECONDS)

        except KeyboardInterrupt:
            print("\n🛑 Live loop stopped by user.")
            break
        except Exception as e:
            print(f"❌ Loop error: {e}")
            time.sleep(INTERVAL_SECONDS)

# 🚀 Entry point
def main():
    # ✅ Check logs exist
    init_log_files()

    # ✅ Check model/scaler exists
    if not model_artifacts_exist():
        print("❌ Missing model or scaler. Run Option 2 to retrain first.")
        return

    # ✅ Optional: inject fake trade row if needed
    inject_test_virtual_trade_if_empty()

    while True:
        choice = menu()
        if choice == '1':
            print("\n▶️ Running live prediction...")
            predict_and_trade()
        elif choice == '2':
            print("\n🔁 Retraining model...")
            check_git_sync()
            retrain_pipeline()
        elif choice == '3':
            print("\n📊 Analyzing trade performance...")
            analyze_trade_log()
        elif choice == '4':
            run_live_loop()
        elif choice == '5':
            print("\n👋 Exiting. Goodbye!")
            sys.exit()
        elif choice == '6':
            print("\n📈 Confidence Trend...")
            plot_confidence_over_time()
        elif choice == '7':
            print("\n📊 Signal Type Breakdown...")
            plot_signal_distribution()
        else:
            print("❌ Invalid choice. Try again.")

if __name__ == "__main__":
    main()
