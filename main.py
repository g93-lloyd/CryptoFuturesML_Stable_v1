# main.py — Unified Command + Live Automation Loop

import sys
import time
import subprocess
from datetime import datetime

# Core pipeline modules
from src.live_trading_engine import predict_and_trade
from src.retraining_pipeline import retrain_pipeline
from src.monitoring import analyze_performance
from src.market_data_collector import fetch_ohlcv
from src.position_manager import handle_signal
from src.cli_dashboard import display_dashboard
from src.confidence_visualizer import (
    plot_confidence_over_time,
    plot_signal_distribution
)
from src.utils import model_artifacts_exist, init_log_files  # ✅ Auto-log setup

# Interval between loop executions
INTERVAL_SECONDS = 300  # 5 minutes

# ✅ Git sync check
def check_git_sync():
    try:
        subprocess.run(["git", "fetch", "origin"], check=True)
        status = subprocess.check_output(["git", "status", "-uno"]).decode()
        if "behind" in status:
            print("⚠️ WARNING: Local branch is behind origin/main. Run `git-resync` to sync before retraining.")
        elif "diverged" in status:
            print("❌ ERROR: Local and remote have diverged. Run manual conflict resolution.")
        else:
            print("✅ Git is up to date with origin/main.")
    except Exception as e:
        print(f"❌ Git sync check failed: {e}")

# 🧠 Main CLI Menu
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

# 🔁 Continuous loop for automation
def run_live_loop():
    print("🚀 Starting automated live loop (CTRL+C to stop)\n")
    while True:
        try:
            print(f"\n⏳ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} — Running cycle...")

            signal, confidence = predict_and_trade(return_result=True)

            if signal in ["LONG", "SHORT"]:
                df = fetch_ohlcv(limit=1)
                current_price = df['close'].iloc[-1]
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
    init_log_files()  # ✅ Auto-create all needed logs if missing

    if not model_artifacts_exist():
        print("⚠️ Missing model or scaler. Run option 2 to retrain.")
    
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
            analyze_performance()
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

# Run program
if __name__ == "__main__":
    main()
