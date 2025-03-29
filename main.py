# main.py — Unified Command + Live Automation Loop

# Built-in modules
import sys
import time
import subprocess
from datetime import datetime
from colorama import Fore, Style, init
init(autoreset=True)

# === System Imports ===
from src.live_trading_engine import predict_and_trade
from src.retraining_pipeline import retrain_pipeline
from src.monitoring import analyze_performance
from src.market_data_collector import fetch_ohlcv
from src.position_manager import handle_signal
from src.cli_dashboard import display_dashboard
from src.utils import model_artifacts_exist, init_log_files, inject_virtual_trade_test_row
from src.confidence_visualizer import plot_confidence_over_time, plot_signal_distribution
from src.telegram_alerts import send_alert

# === Loop Control ===
INTERVAL_SECONDS = 300  # 5 min
DEFAULT_CYCLES = 3      # Auto-run limit unless changed manually

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

# 📋 Main menu
def menu():
    print(Fore.CYAN + "\n🧠 Crypto Futures ML System")
    print(Fore.LIGHTBLACK_EX + "────────────────────────────")
    print(Fore.YELLOW + "1️⃣  Run Live Prediction & Simulated Trade")
    print("2️⃣  Retrain Model on Latest Data")
    print("3️⃣  Analyze Trade Log Performance")
    print("4️⃣  Start Full Automated Live Loop")
    print("5️⃣  Exit")
    print("6️⃣  Visualize Confidence Over Time")
    print("7️⃣  Show Signal Distribution")
    print(Fore.LIGHTBLACK_EX + "────────────────────────────")
    return input(Fore.CYAN + "Select an option (1-7): ")

# 🔄 Live Loop (Auto 3 cycles unless changed)
def run_live_loop(cycles=DEFAULT_CYCLES):
    print(Fore.CYAN + "🚀 Starting automated live loop (CTRL+C to stop)\n")
    for i in range(cycles):
        try:
            print(f"\n⏳ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} — Running cycle {i+1}/{cycles}")
            signal, confidence = predict_and_trade(return_result=True)

            if signal in ["LONG", "SHORT"]:
                df = fetch_ohlcv(limit=1)
                current_price = df['close'].iloc[-1]
                handle_signal(signal=signal, price=current_price)
            else:
                print(f"🔍 No actionable signal: {signal} (confidence: {confidence:.2%})")

            display_dashboard()
            if i < cycles - 1:
                time.sleep(INTERVAL_SECONDS)

        except KeyboardInterrupt:
            print("\n🛑 Live loop stopped by user.")
            break
        except Exception as e:
            print(f"❌ Loop error: {e}")
            time.sleep(INTERVAL_SECONDS)

# 🧠 App entrypoint
def main():
    init_log_files()

    if not model_artifacts_exist():
        print("🚨 Model or scaler not found! Please run option 2 (Retrain Model) first.")
        return

    inject_virtual_trade_test_row()

    while True:
        choice = menu()
        if choice == '1':
            print(Fore.GREEN + "\n▶️ Running live prediction...")
            predict_and_trade()
        elif choice == '2':
            print(Fore.MAGENTA + "\n🔁 Retraining model...")
            check_git_sync()
            retrain_pipeline()
        elif choice == '3':
            print(Fore.YELLOW + "\n📊 Analyzing trade performance...")
            analyze_performance()
        elif choice == '4':
            run_live_loop()
        elif choice == '5':
            print(Fore.CYAN + "\n👋 Exiting. Goodbye!")
            sys.exit()
        elif choice == '6':
            print(Fore.BLUE + "\n📈 Confidence Trend...")
            plot_confidence_over_time()
        elif choice == '7':
            print(Fore.BLUE + "\n📊 Signal Type Breakdown...")
            plot_signal_distribution()
        else:
            print(Fore.RED + "❌ Invalid choice. Try again.")

if __name__ == "__main__":
    main()
