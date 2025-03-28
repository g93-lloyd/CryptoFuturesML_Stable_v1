# src/trade_analyzer.py

import pandas as pd
import os
from datetime import datetime

def analyze_trade_log(log_path="logs/trade_log.csv"):
    if not os.path.exists(log_path):
        return "❌ No trade log file found. Cannot analyze performance."

    try:
        df = pd.read_csv(log_path)

        if df.empty or len(df.columns) == 0:
            return "❌ Trade log is empty or invalid. No data to analyze."

        total_trades = len(df)
        total_pnl = df["PnL"].sum()
        profitable_trades = df[df["PnL"] > 0].shape[0]
        unprofitable_trades = df[df["PnL"] < 0].shape[0]
        accuracy = (profitable_trades / total_trades) * 100 if total_trades > 0 else 0

        max_gain = df["PnL"].max()
        max_loss = df["PnL"].min()
        avg_pnl = df["PnL"].mean()

        final_balance = df["Balance"].iloc[-1] if "Balance" in df.columns else "Unknown"

        last_trade_time = df["Time"].iloc[-1] if "Time" in df.columns else "Unknown"

        report = f"""
📊 Trade Performance Summary
────────────────────────────
🕒 Last Trade Time: {last_trade_time}
📈 Total Trades: {total_trades}
💰 Final Balance: ${final_balance:.2f}
📊 Total PnL: {total_pnl:.2f}
✅ Profitable Trades: {profitable_trades}
❌ Unprofitable Trades: {unprofitable_trades}
🎯 Accuracy: {accuracy:.2f}%
📉 Max Loss: {max_loss:.2f}
📈 Max Gain: {max_gain:.2f}
📐 Avg PnL per Trade: {avg_pnl:.2f}
"""
        return report

    except Exception as e:
        return f"❌ Error analyzing trade log: {str(e)}"

# Test Run
if __name__ == "__main__":
    print(analyze_trade_log())
