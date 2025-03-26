# src/paper_trader.py

import time
import ccxt
import pandas as pd
from datetime import datetime
import os
import logging

# ====== CONFIGURATION ======
VIRTUAL_BALANCE = 10000.0  # Starting simulated capital in USDT
TRADE_SYMBOL = "BTC/USDT"
TRADE_AMOUNT = 0.001       # Simulated size per trade
LOG_PATH = "logs/paper_trade_log.csv"
POLL_INTERVAL = 900        # Time between checks in seconds (e.g., 900 = 15 mins)
MIN_CONFIDENCE = 0.6       # Optional threshold if predict() returns confidence

# ====== SETUP ======
exchange = ccxt.binance()
balance = VIRTUAL_BALANCE
position = None
entry_price = 0.0
os.makedirs("logs", exist_ok=True)

# Setup logging
logging.basicConfig(
    filename="logs/paper_trader.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

# ====== IMPORT YOUR SIGNAL GENERATOR HERE ======
# from model.predictor import predict_and_trade

# Placeholder mock signal function (replace with yours)
def predict_and_trade():
    # Example: return ("buy", 0.72)
    import random
    return random.choice(["buy", "sell", "hold"]), random.uniform(0.5, 0.9)

# ====== GET REAL-TIME PRICE ======
def get_current_price(symbol):
    ticker = exchange.fetch_ticker(symbol)
    return ticker['last']

# ====== TRADE SIMULATION LOGIC ======
def simulate_trade():
    global balance, position, entry_price

    try:
        current_price = get_current_price(TRADE_SYMBOL)
        signal, confidence = predict_and_trade()
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

        action = "No Action"
        pnl = 0.0

        if confidence < MIN_CONFIDENCE:
            signal = "hold"

        if signal == "buy" and position is None:
            entry_price = current_price
            position = "long"
            action = f"Enter Long @ {entry_price:.2f}"

        elif signal == "sell" and position == "long":
            pnl = (current_price - entry_price) * (balance / entry_price)
            balance += pnl
            action = f"Exit Long @ {current_price:.2f} | PnL: {pnl:.2f}"
            position = None
            entry_price = 0.0

        log_trade(timestamp, signal, current_price, action, pnl, balance)

    except Exception as e:
        logging.error(f"Error in simulate_trade: {str(e)}")

# ====== LOGGING FUNCTION ======
def log_trade(timestamp, signal, price, action, pnl, balance):
    log_entry = {
        "Time": timestamp,
        "Signal": signal,
        "Price": price,
        "Action": action,
        "PnL": pnl,
        "Balance": balance
    }

    if not os.path.exists(LOG_PATH):
        pd.DataFrame([log_entry]).to_csv(LOG_PATH, index=False)
    else:
        pd.DataFrame([log_entry]).to_csv(LOG_PATH, mode='a', header=False, index=False)

    logging.info(f"{action} | Balance: {balance:.2f} | PnL: {pnl:.2f}")

# ====== LOOPING EXECUTION ======
if __name__ == "__main__":
    while True:
        simulate_trade()
        print(f"Trade checked at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
        time.sleep(POLL_INTERVAL)  # 15 min loop (adjust as needed)
