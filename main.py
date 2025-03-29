# main.py — Unified Command + Live Automation Loop

# Built-in modules
import sys
import time
import subprocess
from datetime import datetime
import os

# Core components from your trading system
from src.live_trading_engine import predict_and_trade         # Makes predictions & optionally logs simulated trades
from src.retraining_pipeline import retrain_pipeline          # Retrains your model using updated data
from src.trade_analyzer import analyze_trade_log              # 📊 Trade log analysis for Option 3
from src.market_data_collector import fetch_ohlcv             # Grabs latest OHLCV price data
from src.position_manager import handle_signal                # Manages simulated trade entry/exit
from src.cli_dashboard import display_dashboard               # Displays trading stats in terminal
from src.utils import ensure_trade_log_exists                 # Ensures trade log file is initialized

# Interval between live loop cycles (in seconds) — 5 minutes = 300s
INTERVAL_SECONDS = 300

# ✅ Safety check to ensure local repo is in sync with GitHub
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

# ✅ Startup file check before sensitive operations
def check_model_and_scaler():
    try:
        model_path_file = "models/model_latest_path.txt"
        if not os.path.exists(model_path_file):
            raise FileNotFoundError("❌ model_latest_path.txt not found.")
        with open(model_path_file, "r") as f:
            model_path = f.read().strip()
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"❌ Model file not found at: {model_path}")

        scalers = [f for f in os.listdir("models/") if f.endswith(".save")]
        if not scalers:
            raise FileNotFoundError("❌ No scaler file (.save) found in models directory.")

        print("✅ Model and scaler check passed.")
    except Exception as e:
        print(f"❌ Startup check failed: {e}")
        sys.exit()

# 📋 Menu displayed in terminal when script is run
def menu():
    print("\n🧠 Crypto Futures ML System")
    print("────────────────────────────")
    print("1️⃣  Run Live Prediction & Simulated Trade")
    print("2️⃣  Retrain Model on Latest Data")
    print("3️⃣  Analyze Trade Log Performance")
    print("4️⃣  Start Full Automated Live Loop")
    print("5️⃣  Exit")
    return input("Select an option (1-5): ")

# 🔄 Function to run in live loop mode (automated cycles)
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

# 🚀 Entry point: interactive command-line system menu
def main():
    ensure_trade_log_exists()   # ✅ Make sure trade_log.csv exists
    check_model_and_scaler()   # ✅ Sanity check for model/scaler

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
        else:
            print("❌ Invalid choice. Try again.")

if __name__ == "__main__":
    main()
