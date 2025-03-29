# main.py

from colorama import Fore, Style, init
init(autoreset=True)

import os
import time
from src.live_trading_engine import predict_and_trade
from src.retraining_pipeline import retrain_pipeline
from src.trade_analyzer import analyze_performance
from src.cli_dashboard import display_dashboard
from src.confidence_visualizer import plot_confidence_over_time, plot_signal_distribution
from src.utils import (
    init_log_files,
    model_artifacts_exist,
    inject_virtual_trade_test_row,
    generate_daily_summary_log
)

# === Constants ===
INTERVAL_SECONDS = 900
LIVE_LOOP_CYCLES = 3  # Default for testing convenience

# === Init safety ===
init_log_files()
inject_virtual_trade_test_row()

def run_live_loop(cycles=LIVE_LOOP_CYCLES):
    print(f"{Fore.YELLOW}🔁 Starting Live Loop ({cycles} cycles)...")
    for i in range(cycles):
        print(f"{Fore.CYAN}🔄 Cycle {i+1} of {cycles} running...\n")
        predict_and_trade()
        display_dashboard()
        time.sleep(INTERVAL_SECONDS)
    print(f"{Fore.GREEN}✅ Live loop complete.\n")

def main():
    while True:
        print(f"""{Fore.CYAN}
🧠 Crypto Futures ML System
{Style.RESET_ALL}────────────────────────────
1️⃣  Run Live Prediction & Simulated Trade
2️⃣  Retrain Model on Latest Data
3️⃣  Analyze Trade Log Performance
4️⃣  Start Full Automated Live Loop
5️⃣  Exit
6️⃣  Visualize Confidence Over Time
7️⃣  Show Signal Distribution
8️⃣  Generate Daily Summary Log
────────────────────────────""")

        choice = input("Select an option (1-8): ").strip()

        if choice == "1":
            print(f"\n▶️ Running live prediction...\n")
            predict_and_trade()

        elif choice == "2":
            print(f"\n🔁 Retraining model...\n")
            run_retraining_pipeline()

        elif choice == "3":
            print(f"\n📊 Analyzing trade performance...\n")
            analyze_performance()

        elif choice == "4":
            run_live_loop()

        elif choice == "5":
            print(f"{Fore.YELLOW}👋 Exiting... Stay profitable!\n")
            break

        elif choice == "6":
            print(f"\n📈 Confidence Trend...\n")
            plot_confidence_over_time()

        elif choice == "7":
            print(f"\n📊 Signal Type Breakdown...\n")
            plot_signal_distribution()

        elif choice == "8":
            print(f"\n🧾 Generating Daily Summary Log...\n")
            generate_daily_summary_log()

        else:
            print(f"{Fore.RED}❌ Invalid choice. Try again.\n")

if __name__ == "__main__":
    if not model_artifacts_exist():
        print(f"{Fore.RED}❌ Required model/scaler artifacts not found. Please retrain first (Option 2).")
    else:
        main()
