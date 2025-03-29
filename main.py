# main.py — Unified Command + Live Automation Loop

# Built-in modules
import sys
import time
import subprocess
from datetime import datetime, timedelta

# Core components from your trading system
from src.live_trading_engine import predict_and_trade         # Makes predictions & optionally logs simulated trades
from src.retraining_pipeline import retrain_pipeline          # Retrains your model using updated data
from src.monitoring import analyze_performance                # Analyzes trade logs (PnL, win rate, etc.)
from src.market_data_collector import fetch_ohlcv             # Grabs latest OHLCV price data
from src.position_manager import handle_signal                # Manages simulated trade entry/exit
from src.cli_dashboard import display_dashboard               # Displays trading stats in terminal
from src.trade_analyzer import analyze_performance              # 📊 Trade log analysis for Option 3
from src.confidence_visualizer import (
    plot_confidence_over_time,
    plot_signal_distribution
)
from src.utils import model_artifacts_exist, init_log_files   # ✅ Model safety + log initialization
from src.utils import inject_virtual_trade_test_row

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

# 📋 Menu displayed in terminal when script is run
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

# 🔄 Function to run in live loop mode (automated cycles)
def run_live_loop(max_cycles=3):
    print(f"🚀 Starting automated live loop for {max_cycles} cycles\n")
    cycle = 0
    while True:
        try:
            print(f"\n⏳ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} — Running cycle {cycle + 1}...")

            signal, confidence = predict_and_trade(return_result=True)

            if signal in ["LONG", "SHORT"]:
                df = fetch_ohlcv(limit=1)
                current_price = df['close'].iloc[-1]
                handle_signal(signal=signal, price=current_price)
            else:
                print(f"🔍 No actionable signal: {signal} (confidence: {confidence:.2%})")

            display_dashboard()
            cycle += 1

            if cycle >= max_cycles:
                print("✅ Reached max cycles. Returning to menu.")
                break

            time.sleep(INTERVAL_SECONDS)

        except KeyboardInterrupt:
            print("\n🛑 Live loop stopped by user.")
            break
        except Exception as e:
            print(f"❌ Loop error: {e}")
            time.sleep(INTERVAL_SECONDS)

# Inject test trade rows if logs are empty
def inject_test_virtual_trade_if_empty():
    inject_virtual_trade_test_row()

# 🚀 Entry point: interactive command-line system menu
def main():
    # ✅ Ensure model and scaler files are ready
    model_artifacts_exist()
    init_log_files()
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
            analyze_performance
        elif choice == '4':
            try:
                loops = int(input("🔁 How many cycles to run? (Default = 3): ") or 3)
                run_live_loop(max_cycles=loops)
            except ValueError:
                print("❌ Invalid input. Running 3 cycles by default.")
                run_live_loop(max_cycles=3)
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
