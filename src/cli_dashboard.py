# src/cli_dashboard.py

import pandas as pd
from datetime import datetime
import os

POSITION_LOG = "logs/virtual_positions.csv"

def display_dashboard():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("🧠 CryptoFuturesML — CLI Dashboard")
    print("────────────────────────────────────────────")

    if not os.path.exists(POSITION_LOG):
        print("📭 No trades logged yet.")
        return

    df = pd.read_csv(POSITION_LOG)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['entry_time'] = pd.to_datetime(df['entry_time'])

    # Display last trade
    last = df.iloc[-1]
    print(f"📅 Last Trade: {last['signal']} | {last['entry_time']} → {last['timestamp']}")
    print(f"⚡ PnL: {last['pnl_percent']:.2f}% | 💰 Balance: ${last['balance_after']:.2f}")
    print("────────────────────────────────────────────")

    # Daily summary
    today = datetime.now().date()
    today_trades = df[df['timestamp'].dt.date == today]
    if not today_trades.empty:
        avg_pnl = today_trades['pnl_percent'].mean()
        win_rate = (today_trades['pnl_percent'] > 0).mean() * 100
        print(f"📊 Today's Stats:")
        print(f"   Trades: {len(today_trades)}")
        print(f"   Avg PnL: {avg_pnl:.2f}%")
        print(f"   Win Rate: {win_rate:.1f}%")
    else:
        print("📭 No trades today.")

    print("────────────────────────────────────────────")

if __name__ == "__main__":
    display_dashboard()
