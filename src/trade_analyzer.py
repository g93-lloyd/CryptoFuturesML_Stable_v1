# src/trade_analyzer.py

import pandas as pd
import os

TRADE_LOG_PATH = "logs/trade_log.csv"
SUMMARY_LOG_PATH = "logs/performance_summary.txt"

def analyze_performance():
    if not os.path.exists(TRADE_LOG_PATH):
        print("⚠️ No trade log found.")
        return

    try:
        # ✅ Check if file is completely empty
        if os.path.getsize(TRADE_LOG_PATH) == 0:
            print("⚠️ Trade log file is empty.")
            return

        df = pd.read_csv(TRADE_LOG_PATH)

        # ✅ Check if there are too few trades to analyze
        if df.empty or len(df) < 2:
            print("⚠️ Not enough trade data to analyze.")
            return

        wins = df[df["PnL"] > 0]
        losses = df[df["PnL"] < 0]
        total_trades = len(df)
        total_pnl = df["PnL"].sum()
        win_rate = len(wins) / total_trades * 100
        avg_win = wins["PnL"].mean() if not wins.empty else 0
        avg_loss = losses["PnL"].mean() if not losses.empty else 0
        max_drawdown = df["PnL"].min()

        summary = f"""
📊 Trade Performance Summary
────────────────────────────
📈 Total Trades:       {total_trades}
💰 Total PnL:          {total_pnl:.2f} USDT
🏆 Win Rate:           {win_rate:.2f}%
📊 Avg Win:            {avg_win:.2f}
📉 Avg Loss:           {avg_loss:.2f}
🔻 Max Drawdown:       {max_drawdown:.2f}

📝 Summary also saved to: {SUMMARY_LOG_PATH}
"""

        print(summary)

        # ✅ Save summary to file
        os.makedirs("logs", exist_ok=True)
        with open(SUMMARY_LOG_PATH, "w") as f:
            f.write(summary)

    except pd.errors.EmptyDataError:
        print("⚠️ Trade log file is malformed or has no readable content.")
    except Exception as e:
        print(f"❌ Performance analysis failed: {str(e)}")
