# src/trade_analyzer.py

import pandas as pd
import os

TRADE_LOG_PATH = "logs/virtual_positions.csv"
SUMMARY_LOG_PATH = "logs/performance_summary.txt"

def analyze_performance():
    if not os.path.exists(TRADE_LOG_PATH):
        print("⚠️ No trade log file found.")
        return

    try:
        df = pd.read_csv(TRADE_LOG_PATH)

        if df.empty or len(df) < 2:
            print("⚠️ Not enough trade data to analyze.")
            return

        # Ensure timestamp column is datetime
        if "timestamp" not in df.columns or "entry_time" not in df.columns:
            print("⚠️ Required columns missing from trade log.")
            return

        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["entry_time"] = pd.to_datetime(df["entry_time"])

        wins = df[df["pnl_percent"] > 0]
        losses = df[df["pnl_percent"] < 0]
        total_trades = len(df)
        total_pnl = df["pnl_percent"].sum()
        win_rate = len(wins) / total_trades * 100
        avg_win = wins["pnl_percent"].mean() if not wins.empty else 0
        avg_loss = losses["pnl_percent"].mean() if not losses.empty else 0
        max_drawdown = df["pnl_percent"].min()

        summary = f"""
📊 Trade Performance Summary
────────────────────────────
📈 Total Trades:       {total_trades}
💰 Total PnL (%):      {total_pnl:.2f}%
🏆 Win Rate:           {win_rate:.2f}%
📊 Avg Win:            {avg_win:.2f}%
📉 Avg Loss:           {avg_loss:.2f}%
🔻 Max Drawdown:       {max_drawdown:.2f}%

📝 Summary also saved to: {SUMMARY_LOG_PATH}
"""

        print(summary)

        # Save to summary log
        os.makedirs("logs", exist_ok=True)
        with open(SUMMARY_LOG_PATH, "w") as f:
            f.write(summary)

    except Exception as e:
        print(f"❌ Performance analysis failed: {e}")
