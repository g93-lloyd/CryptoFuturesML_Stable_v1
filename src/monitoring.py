# src/monitoring.py — Logs, PnL analysis, Drift Detection

import os
from datetime import datetime
import pandas as pd
from scipy.stats import wasserstein_distance

# ========= TRADE LOGGING =========
def log_trade(signal, confidence):
    os.makedirs("logs", exist_ok=True)
    log_file = "logs/trade_log.csv"

    new_entry = pd.DataFrame([{
        "timestamp": datetime.now(),
        "signal": signal,
        "confidence": round(confidence, 4),
        "entry_price": None,     # Placeholder for future upgrade
        "exit_price": None,
        "pnl_percent": None
    }])

    # Append or create log file
    if os.path.exists(log_file):
        new_entry.to_csv(log_file, mode='a', header=False, index=False)
    else:
        new_entry.to_csv(log_file, index=False)

    print("📝 Trade logged.")


# ========= PNL SUMMARY =========
def analyze_performance():
    try:
        log_file = "logs/trade_log.csv"
        if not os.path.exists(log_file):
            print("📭 No trade log found.")
            return

        df = pd.read_csv(log_file)
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        total = len(df)
        longs = (df['signal'] == "LONG").sum()
        shorts = (df['signal'] == "SHORT").sum()
        holds = (df['signal'] == "HOLD").sum()
        avg_conf = df['confidence'].mean()

        print("📊 Trade Performance Summary")
        print("────────────────────────────")
        print(f"🕒 Total Trades: {total}")
        print(f"🟩 LONG: {longs} | 🔻 SHORT: {shorts} | ⚪ HOLD: {holds}")
        print(f"⚡ Avg Confidence: {avg_conf:.2%}")

        # Optional — only show PnL if column exists and not empty
        if 'pnl_percent' in df.columns:
            realized = df[df['pnl_percent'].notna()]
            avg_pnl = realized['pnl_percent'].mean()
            print(f"💰 Avg PnL: {avg_pnl:.2f}% (on {len(realized)} closed trades)")

    except Exception as e:
        print(f"❌ Performance analysis failed: {e}")


# ========= DRIFT DETECTION =========
def drift_detected(threshold=0.15):
    """
    Compare recent vs historical distributions for drift using Wasserstein Distance.
    Features checked: sentiment_score, price_volatility, volume
    """

    try:
        file_path = "data/datasets/combined_features.csv"
        if not os.path.exists(file_path):
            print("🚫 Feature dataset not found.")
            return False

        df = pd.read_csv(file_path)
        if len(df) < 100:
            print("⚠️ Not enough data to evaluate drift.")
            return False

        # Split into historical and recent windows
        historical = df.iloc[:-20]
        recent = df.iloc[-20:]

        drift_metrics = {}
        drift_detected = False

        for feature in ['sentiment_score', 'price_volatility', 'volume']:
            if feature not in df.columns:
                continue
            hist_values = historical[feature].dropna()
            recent_values = recent[feature].dropna()
            if len(hist_values) < 10 or len(recent_values) < 10:
                continue
            wd = wasserstein_distance(hist_values, recent_values)
            drift_metrics[feature] = wd
            if wd > threshold:
                drift_detected = True

        # Save to drift log
        drift_log = pd.DataFrame([{
            "timestamp": datetime.now(),
            **drift_metrics,
            "drift_triggered": drift_detected
        }])

        os.makedirs("logs", exist_ok=True)
        drift_log_path = "logs/drift_log.csv"
        if os.path.exists(drift_log_path):
            drift_log.to_csv(drift_log_path, mode='a', header=False, index=False)
        else:
            drift_log.to_csv(drift_log_path, index=False)

        return drift_detected

    except Exception as e:
        print(f"❌ Drift detection failed: {e}")
        return False
