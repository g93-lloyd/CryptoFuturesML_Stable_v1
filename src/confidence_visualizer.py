# src/confidence_visualizer.py

import pandas as pd
import matplotlib.pyplot as plt
import os

CONFIDENCE_LOG_PATH = "logs/confidence_log.csv"

# ✅ Visualize Confidence Scores Over Time
def plot_confidence_over_time():
    if not os.path.exists(CONFIDENCE_LOG_PATH):
        print("⚠️ Confidence log not found.")
        return

    df = pd.read_csv(CONFIDENCE_LOG_PATH)
    if df.empty or 'timestamp' not in df.columns or 'confidence' not in df.columns:
        print("⚠️ Confidence log is empty or improperly formatted.")
        return

    df['timestamp'] = pd.to_datetime(df['timestamp'])

    plt.figure(figsize=(10, 5))
    plt.plot(df['timestamp'], df['confidence'], marker='o', label='Confidence')

    plt.axhline(0.6, color='green', linestyle='--', label='LONG Threshold')
    plt.axhline(0.4, color='red', linestyle='--', label='SHORT Threshold')

    plt.title('Confidence Over Time')
    plt.xlabel('Timestamp')
    plt.ylabel('Confidence')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# ✅ Visualize Signal Distribution
def plot_signal_distribution():
    if not os.path.exists(CONFIDENCE_LOG_PATH):
        print("⚠️ Confidence log not found.")
        return

    df = pd.read_csv(CONFIDENCE_LOG_PATH)
    if df.empty or 'signal' not in df.columns:
        print("⚠️ No signal data available.")
        return

    signal_counts = df['signal'].value_counts()

    plt.figure(figsize=(6, 4))
    color_map = {
        "LONG": "green",
        "SHORT": "red",
        "HOLD": "gray",
        "FILTERED": "orange",
        "ERROR": "black"
    }
    colors = [color_map.get(signal, "blue") for signal in signal_counts.index]

    signal_counts.plot(kind="bar", color=colors)
    plt.title("Signal Distribution")
    plt.ylabel("Frequency")
    plt.xticks(rotation=0)
    plt.grid(axis="y")
    plt.tight_layout()
    plt.show()
