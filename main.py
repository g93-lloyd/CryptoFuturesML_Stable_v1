# main.py — Unified Command + Live Automation Loop

# Built-in modules
import sys
import time
from datetime import datetime

# Core components from your trading system
from src.live_trading_engine import predict_and_trade         # Makes predictions & optionally logs simulated trades
from src.retraining_pipeline import retrain_pipeline          # Retrains your model using updated data
from src.monitoring import analyze_performance                # Analyzes trade logs (PnL, win rate, etc.)
from src.market_data_collector import fetch_ohlcv             # Grabs latest OHLCV price data
from src.position_manager import handle_signal                # Manages simulated trade entry/exit
from src.cli_dashboard import display_dashboard               # Displays trading stats in terminal

# Interval between live loop cycles (in seconds) — 5 minutes = 300s
INTERVAL_SECONDS = 300

# Menu displayed in terminal when script is run
def menu():
    print("\n🧠 Crypto Futures ML System")
    print("────────────────────────────")
    print("1️⃣  Run Live Prediction & Simulated Trade")
    print("2️⃣  Retrain Model on Latest Data")
    print("3️⃣  Analyze Trade Log Performance")
    print("4️⃣  Start Full Automated Live Loop")
    print("5️⃣  Exit")
    return input("Select an option (1-5): ")

# Function to run in live loop mode (automated cycles)
def run_live_loop():
    print("🚀 Starting automated live loop (CTRL+C to stop)\n")
    while True:
        try:
            # Show timestamp of current loop
            print(f"\n⏳ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} — Running cycle...")

            # Make prediction + trade (return signal and confidence)
            signal, confidence = predict_and_trade(return_result=True)

            # If signal is LONG or SHORT, simulate a trade
            if signal in ["LONG", "SHORT"]:
                df = fetch_ohlcv(limit=1)  # Get latest candle
                current_price = df['close'].iloc[-1]  # Use close price
                handle_signal(signal=signal, price=current_price)  # Execute virtual trade
            else:
                print(f"🔍 No actionable signal: {signal} (confidence: {confidence:.2%})")

            # Show summary in CLI after each loop
            display_dashboard()

            # Wait until next interval
            time.sleep(INTERVAL_SECONDS)

        except KeyboardInterrupt:
            print("\n🛑 Live loop stopped by user.")  # Graceful exit
            break
        except Exception as e:
            print(f"❌ Loop error: {e}")  # Handle unexpected errors
            time.sleep(INTERVAL_SECONDS)

# Entry point: command menu to interact with the system
def main():
    while True:
        choice = menu()
        if choice == '1':
            print("\n▶️ Running live prediction...")
            predict_and_trade()
        elif choice == '2':
            print("\n🔁 Retraining model...")
            retrain_pipeline()
        elif choice == '3':
            print("\n📊 Analyzing trade performance...")
            analyze_performance()
        elif choice == '4':
            run_live_loop()
        elif choice == '5':
            print("\n👋 Exiting. Goodbye!")
            sys.exit()
        else:
            print("❌ Invalid choice. Try again.")

# Only runs if this file is called directly
if __name__ == "__main__":
    main()
