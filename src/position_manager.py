# src/position_manager.py

from datetime import datetime, timedelta
import os
import pandas as pd
from src.binance_executor import place_order  # Binance testnet order handler

POSITION_LOG = "logs/virtual_positions.csv"
COOLDOWN_MINUTES = 10  # Prevents rapid back-to-back trades

TRADE_LIVE = True       # ✅ Toggle to False to run in full simulation mode
TRADE_AMOUNT = 0.001    # Amount used per trade (in BTC or asset units)

# ⏳ State manager for current open trade
position_state = {
    "is_open": False,
    "type": None,             # 'LONG' or 'SHORT'
    "entry_price": 0.0,
    "entry_time": None,
    "cooldown_until": None,
    "balance": 10000.0        # Starting paper balance
}

def log_position(entry):
    os.makedirs("logs", exist_ok=True)
    df = pd.DataFrame([entry])
    if os.path.exists(POSITION_LOG):
        df.to_csv(POSITION_LOG, mode='a', header=False, index=False)
    else:
        df.to_csv(POSITION_LOG, index=False)

def handle_signal(signal, price, timestamp=None):
    global position_state
    timestamp = timestamp or datetime.utcnow()

    # 🚫 Respect cooldown to prevent overtrading
    if position_state["cooldown_until"] and timestamp < position_state["cooldown_until"]:
        print("⏳ In cooldown. Skipping trade.")
        return position_state

    # ==== Entry logic ====
    if not position_state["is_open"]:
        if signal in ["LONG", "SHORT"]:
            # Update state with new open position
            position_state.update({
                "is_open": True,
                "type": signal,
                "entry_price": price,
                "entry_time": timestamp,
                "cooldown_until": None
            })

            # 🧪 Place order on Binance Testnet (or skip if TRADE_LIVE = False)
            if TRADE_LIVE:
                place_order("buy" if signal == "LONG" else "sell", amount=TRADE_AMOUNT)

            print(f"📥 Position OPENED: {signal} @ {price:.2f}")
        else:
            print("⚠️ HOLD signal. No open position.")
        return position_state

    # ==== Exit logic ====
    if (position_state["type"] == "LONG" and signal == "SHORT") or \
       (position_state["type"] == "SHORT" and signal == "LONG"):

        entry_price = position_state["entry_price"]
        position_type = position_state["type"]

        # 📊 Calculate profit/loss
        pnl = ((price - entry_price) / entry_price) if position_type == "LONG" \
              else ((entry_price - price) / entry_price)
        pnl_percent = round(pnl * 100, 2)
        new_balance = position_state["balance"] * (1 + pnl)

        # 📝 Log trade outcome
        log_position({
            "timestamp": timestamp,
            "entry_time": position_state["entry_time"],
            "signal": position_type,
            "entry_price": round(entry_price, 2),
            "exit_price": round(price, 2),
            "pnl_percent": pnl_percent,
            "balance_after": round(new_balance, 2)
        })

        print(f"📤 Position CLOSED: {position_type} | PnL: {pnl_percent:.2f}%")

        # Reset state & apply cooldown
        position_state.update({
            "is_open": False,
            "type": None,
            "entry_price": 0.0,
            "entry_time": None,
            "balance": new_balance,
            "cooldown_until": timestamp + timedelta(minutes=COOLDOWN_MINUTES)
        })

    else:
        print(f"🔁 Ignoring signal: {signal} | Position: {position_state['type']}")

    return position_state
