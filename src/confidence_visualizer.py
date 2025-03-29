# src/confidence_visualizer.py

import pandas as pd
import matplotlib.pyplot as plt
import os

CONFIDENCE_LOG_PATH = "logs/confidence_log.csv"

def plot_confidence_chart():
    if not os.path.exists(CONFIDENCE_LOG_PATH):
        print("⚠️ Confidence log not found.")
        return

    df = pd.read_csv(CONFIDENCE_LOG_PATH)
    if df.empty or len(df) < 2:
        print("⚠️ Not enough data to plot confidence.")
        return

    df["timestamp"] = pd.to_datetime(df["timestamp"])

    plt.figure(figsize=(12, 6))
    plt.plot(df["timestamp"], df["confidence"], label="Confidence", linewidth=2)
    plt.axhline(0.6, color="green", linestyle="--", label="Buy Threshold (0.6)")
    plt.axhline(0.4, color="red", linestyle="--", label="Sell Threshold (0.4)")
    plt.title("🧠 Model Confidence Over Time")
    plt.xlabel("Time")
    plt.ylabel("Confidence")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()
