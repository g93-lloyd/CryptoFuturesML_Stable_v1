# src/confidence_visualizer.py

import pandas as pd
import matplotlib.pyplot as plt
import os

CONFIDENCE_LOG_PATH = "logs/confidence_log.csv"

# === Plot Confidence Over Time ===
def plot_confidence_over_time():
    if not os.path.exists(CONFIDENCE_LOG_PATH):
        print("⚠️ Confidence log not found.")
        return

    try:
        df = pd.read_csv(CONFIDENCE_LOG_PATH, usecols=["timestamp", "confidence", "signal"])
        if df.empty:
            print("⚠️ Confidence log is empty.")
            return

        df['timestamp'] = pd.to_datetime(df['timestamp'])

        plt.figure(figsize=(10, 5))
        plt.plot(df['timestamp'], df['confidence'], label='Confidence')
        plt.axhline(0.6, color='green', linestyle='--', label='LONG Threshold')
        plt.axhline(0.4, color='red', linestyle='--', label='SHORT Threshold')
        plt.title('Confidence Over Time')
        plt.xlabel('Timestamp')
        plt.ylabel('Confidence')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()

        os.makedirs("logs/plots", exist_ok=True)
        path = "logs/plots/confidence_over_time.png"
        plt.savefig(path)
        print(f"📊 Saved: {path}")

    except Exception as e:
        print(f"❌ Plotting failed: {e}")


# === Plot Signal Frequency ===
def plot_signal_distribution():
    if not os.path.exists(CONFIDENCE_LOG_PATH):
        print("⚠️ Confidence log not found.")
        return

    try:
        df = pd.read_csv(CONFIDENCE_LOG_PATH, usecols=["signal"])
        if df.empty:
            print("⚠️ No signal data available.")
            return

        signal_counts = df["signal"].value_counts()

        plt.figure(figsize=(6, 4))
        signal_counts.plot(kind="bar", color=["green", "red", "gray"])
        plt.title("Signal Distribution")
        plt.ylabel("Frequency")
        plt.xticks(rotation=0)
        plt.tight_layout()
        plt.grid(axis="y")

        os.makedirs("logs/plots", exist_ok=True)
        path = "logs/plots/signal_distribution.png"
        plt.savefig(path)
        print(f"📊 Saved: {path}")

    except Exception as e:
        print(f"❌ Signal plot failed: {e}")

