# src/cli_dashboard.py

import pandas as pd
from datetime import datetime
import os

POSITION_LOG = "logs/virtual_positions.csv"

def display_dashboard():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\033[96m\U0001F9E0 CryptoFuturesML — CLI Dashboard\033[0m")
    print("\033[90m─" * 50 + "\033[0m")

    if not os.path.exists(POSITION_LOG):
        print("📭 No trades logged yet.")
        return

    try:
        df = pd.read_csv(POSITION_LOG)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['entry_time'] = pd.to_datetime(df['entry_time'])

        if df.empty:
            print("📭 No trades yet.")
            return

        last = df.iloc[-1]
        print(f"📅 Last Trade: {last['signal']} | {last['entry_time']} → {last['timestamp']}")
        print(f"⚡ PnL: {last['pnl_percent']:.2f}% | \U0001F4B0 Balance: ${last['balance_after']:.2f}")
        print("\033[90m─" * 50 + "\033[0m")

        today = datetime.now().date()
        today_trades = df[df['timestamp'].dt.date == today]
        if not today_trades.empty:
            avg_pnl = today_trades['pnl_percent'].mean()
            win_rate = (today_trades['pnl_percent'] > 0).mean() * 100
            print("📊 \033[94mToday's Stats:\033[0m")
            print(f"   Trades: {len(today_trades)}")
            print(f"   Avg PnL: {avg_pnl:.2f}%")
            print(f"   Win Rate: {win_rate:.1f}%")
        else:
            print("📭 No trades today.")

        print("\033[90m─" * 50 + "\033[0m")

    except Exception as e:
        print(f"❌ Dashboard error: {e}")

if __name__ == "__main__":
    display_dashboard()
