# src/backtest_analysis.py

import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
from datetime import datetime

def compute_backtest_metrics(df, strategy_name="DefaultStrategy"):
    if df.empty:
        return None

    df = df.sort_values("timestamp").reset_index(drop=True)
    df['cumulative_return'] = (1 + df['pnl_percent'] / 100).cumprod()

    returns = df['pnl_percent'] / 100
    win_rate = (returns > 0).sum() / len(returns)
    avg_pnl = returns.mean()
    std_pnl = returns.std()
    sharpe = (avg_pnl / std_pnl) * np.sqrt(12) if std_pnl > 0 else 0

    peak = df['cumulative_return'].cummax()
    drawdown = (df['cumulative_return'] - peak) / peak
    max_dd = drawdown.min()

    summary = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "strategy": strategy_name,
        "num_trades": len(df),
        "win_rate": round(win_rate * 100, 2),
        "avg_pnl": round(avg_pnl * 100, 2),
        "sharpe_ratio": round(sharpe, 2),
        "max_drawdown": round(max_dd * 100, 2),
    }

    return summary

def log_backtest_summary(summary_dict, path="logs/backtest_summary.csv"):
    if summary_dict is None:
        print("❌ No trades to summarize.")
        return

    os.makedirs("logs", exist_ok=True)
    df = pd.DataFrame([summary_dict])
    if os.path.exists(path):
        df.to_csv(path, mode='a', header=False, index=False)
    else:
        df.to_csv(path, index=False)

    print(f"✅ Backtest metrics logged to {path}")


def plot_backtest_results(log_path="logs/backtest_trades.csv"):
    if not os.path.exists(log_path):
        print("❌ Backtest log not found.")
        return

    df = pd.read_csv(log_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    if df.empty:
        print("⚠️ No trades to plot.")
        return

    df = df.sort_values("timestamp").reset_index(drop=True)
    df['cumulative_return'] = (1 + df['pnl_percent'] / 100).cumprod()

    fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

    axes[0].plot(df['timestamp'], df['cumulative_return'], color='green', linewidth=2)
    axes[0].set_title("📈 Cumulative Equity Curve")
    axes[0].set_ylabel("Equity (x initial capital)")
    axes[0].grid(True)

    axes[1].hist(df['pnl_percent'], bins=30, color='skyblue', edgecolor='black')
    axes[1].set_title("📊 Trade PnL Distribution")
    axes[1].set_xlabel("PnL (%)")
    axes[1].set_ylabel("Frequency")
    axes[1].grid(True)

    plt.tight_layout()
    plt.show()
