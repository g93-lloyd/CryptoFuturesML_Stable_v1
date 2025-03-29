# main.py

from src.live_trading_engine import predict_and_trade
from src.retraining_pipeline import retrain_pipeline
from src.trade_analyzer import analyze_performance
from src.cli_dashboard import display_dashboard
from src.utils import (
    init_log_files,
    inject_virtual_trade_test_row,
    model_artifacts_exist,
    generate_daily_summary_log
)
from src.confidence_visualizer import (
    plot_confidence_over_time,
    plot_signal_distribution
)
from colorama import Fore, Style, init as colorama_init
import time

colorama_init(autoreset=True)

# === INIT ON STARTUP ===
init_log_files()
inject_virtual_trade_test_row()

# === MENU ===
def print_menu():
    print(Fore.CYAN + Style.BRIGHT + "\n🧠 Crypto Futures ML System")
    print("────────────────────────────")
    print("1️⃣  Run Live Prediction & Simulated Trade")
    print("2️⃣  Retrain Model on Latest Data")
    print("3️⃣  Analyze Trade Log Performance")
    print("4️⃣  Start Full Automated Live Loop")
    print("5️⃣  Exit")
    print("6️⃣  Visualize Confidence Over Time")
    print("7️⃣  Show Signal Distribution")
    print("8️⃣  Generate Daily Summary Log")
    print("────────────────────────────")

def run_live_loop(cycles=3):
    for i in range(cycles):
        print(f"\n🔁 Live loop cycle {i+1}/{cycles}")
        predict_and_trade()
        display_dashboard()
        time.sleep(5)
    print(Fore.YELLOW + "\n🛑 Live loop completed. Returning to menu...")

def main():
    if not model_artifacts_exist():
        print(Fore.RED + "❌ Model or scaler artifacts not found. Please run Option 2 first to retrain.")
        return

    while True:
        print_menu()
        choice = input(Fore.GREEN + "Select an option (1-8): ")

        if choice == "1":
            print("\n▶️ Running live prediction...")
            predict_and_trade()

        elif choice == "2":
            print("\n🔁 Retraining model...\n")
            retrain_pipeline()

        elif choice == "3":
            print("\n📊 Analyzing trade performance...")
            analyze_performance()

        elif choice == "4":
            run_live_loop()

        elif choice == "5":
            print(Fore.MAGENTA + "\n👋 Exiting. Stay profitable!")
            break

        elif choice == "6":
            print("\n📈 Confidence Trend...")
            plot_confidence_over_time()

        elif choice == "7":
            print("\n📊 Signal Type Breakdown...")
            plot_signal_distribution()

        elif choice == "8":
            print("\n📝 Generating Daily Summary Log...")
            generate_daily_summary_log()

        else:
            print(Fore.RED + "❌ Invalid option. Please choose between 1 and 8.")

if __name__ == "__main__":
    main()
