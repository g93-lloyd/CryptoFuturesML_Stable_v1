# src/position_manager.py

from datetime import datetime, timedelta
import os
import pandas as pd
from src.binance_executor import place_order
from src.telegram_alerts import send_alert
from src.utils import write_daily_log

POSITION_LOG = "logs/virtual_positions.csv"
COOLDOWN_MINUTES = 10
TRADE_LIVE = True
TRADE_AMOUNT = 0.001

position_state = {
    "is_open": False,
    "type": None,
    "entry_price": 0.0,
    "entry_time": None,
    "cooldown_until": None,
    "balance": 10000.0
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

    if position_state["cooldown_until"] and timestamp < position_state["cooldown_until"]:
        print("⏳ In cooldown. Skipping trade.")
        return position_state

    if not position_state["is_open"]:
        if signal in ["LONG", "SHORT"]:
            position_state.update({
                "is_open": True,
                "type": signal,
                "entry_price": price,
                "entry_time": timestamp,
                "cooldown_until": None
            })
            if TRADE_LIVE:
                place_order("buy" if signal == "LONG" else "sell", amount=TRADE_AMOUNT)

            print(f"📥 Position OPENED: {signal} @ {price:.2f}")
            send_alert(f"📥 Position OPENED: {signal}\n@ ${price:.2f}")
        else:
            print("⚠️ HOLD signal. No open position.")
        return position_state

    if (position_state["type"] == "LONG" and signal == "SHORT") or \
       (position_state["type"] == "SHORT" and signal == "LONG"):

        entry_price = position_state["entry_price"]
        position_type = position_state["type"]

        pnl = ((price - entry_price) / entry_price) if position_type == "LONG" \
              else ((entry_price - price) / entry_price)
        pnl_percent = round(pnl * 100, 2)
        new_balance = position_state["balance"] * (1 + pnl)

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
        send_alert(f"📤 CLOSED {position_type} @ ${price:.2f}\nPnL: {pnl_percent:.2f}%")

        position_state.update({
            "is_open": False,
            "type": None,
            "entry_price": 0.0,
            "entry_time": None,
            "balance": new_balance,
            "cooldown_until": timestamp + timedelta(minutes=COOLDOWN_MINUTES)
        })

        write_daily_log()  # Optional: updates daily log after each closed trade

    else:
        print(f"🔁 Ignoring signal: {signal} | Position: {position_state['type']}")

    return position_state
