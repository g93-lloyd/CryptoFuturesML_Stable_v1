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
LOG_PATH = "logs/trade_log.csv"  # Fixed name for compatibility with analyzer
POLL_INTERVAL = 900        # 15 minutes
MIN_CONFIDENCE = 0.6       # Threshold for action

# ====== SETUP ======
exchange = ccxt.binance()
balance = VIRTUAL_BALANCE
position = None
entry_price = 0.0
os.makedirs("logs", exist_ok=True)

# Logging config
logging.basicConfig(
    filename="logs/paper_trader.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

# ====== IMPORT YOUR MODEL PREDICTION FUNCTION HERE ======
# from model.predictor import predict_and_trade

# Mocked placeholder (for now)
def predict_and_trade():
    import random
    return random.choice(["buy", "sell", "hold"]), random.uniform(0.5, 0.9)

# ====== GET PRICE ======
def get_current_price(symbol):
    return exchange.fetch_ticker(symbol)['last']

# ====== SIMULATION LOGIC ======
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

        log_trade(timestamp, signal, current_price, action, pnl, balance) # ✅ Only triggered when a trade is exited

    except Exception as e:
        logging.error(f"❌ simulate_trade error: {str(e)}")

# ====== LOG TRADES ======
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
        time.sleep(POLL_INTERVAL)
