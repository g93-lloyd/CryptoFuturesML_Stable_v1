# src/retraining_pipeline.py

from src.market_data_collector import fetch_ohlcv
from src.sentiment_pipeline import fetch_twitter_sentiment
from src.feature_engineering import add_technical_indicators, merge_sentiment
from src.model_trainer import prepare_data, train_lstm_model, save_model
from src.mlflow_logger import start_experiment_run, log_params_and_metrics, log_artifacts
from datetime import datetime
import os
import subprocess

def check_git_sync():
    try:
        fetch = subprocess.run(['git', 'fetch', 'origin'], check=True, capture_output=True)
        status = subprocess.run(['git', 'status', '-uno'], capture_output=True, text=True)

        log_entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {status.stdout.strip()}\n"
        os.makedirs("logs", exist_ok=True)
        with open("logs/git_sync_log.txt", "a") as log_file:
            log_file.write(log_entry)

        if "up to date" in status.stdout:
            print("✅ Git is up to date with origin/main.")
        else:
            print("⚠️ WARNING: Your branch is not synced with origin/main!")
    except Exception as e:
        print(f"❌ Git sync check failed: {e}")

def retrain_pipeline(versioned=False):
    check_git_sync()
    print("🚨 DEBUG: This is the correct retraining_pipeline.py being executed.")

    log_path = "logs/retrain_log.txt"
    os.makedirs("logs", exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        print("📅 Fetching fresh market data...")
        df = fetch_ohlcv("BTC/USDT", timeframe="5m", limit=1000)

        print("💬 Fetching latest sentiment data...")
        sentiment_scores = fetch_twitter_sentiment()

        print("🔪 Engineering features...")
        df = add_technical_indicators(df)
        df = merge_sentiment(df, sentiment_scores)

        print("🧠 Preparing data for training...")
        features = ['rsi_14', 'ema_21', 'macd', 'sentiment']
        target_col = 'close'
        window_size = 10
        X, y, scaler = prepare_data(df, feature_cols=features, target_col=target_col, window_size=window_size)

        print("🎯 Training LSTM model...")
        model, checkpoint_path = train_lstm_model(X, y)

        # ✅ Set save paths
        if versioned:
            model_time = datetime.now().strftime("%Y-%m-%d_%H-%M")
            model_path = f"models/lstm_model_{model_time}.keras"
            scaler_path = f"models/scaler_{model_time}.save"
        else:
            model_path = "models/lstm_model.keras"
            scaler_path = "models/scaler.save"

        # 🧹 Remove legacy .h5 model if it exists
        legacy_path = "models/lstm_model.h5"
        if os.path.exists(legacy_path):
            os.remove(legacy_path)
            print("🧹 Removed old HDF5 model: models/lstm_model.h5")

        # 🧹 Cleanup checkpoint
        if os.path.exists(checkpoint_path):
            os.remove(checkpoint_path)

        print(f"💾 Saving model and scaler to: {model_path}")
        save_model(model, scaler, model_path, scaler_path)

        with open("models/model_latest_path.txt", "w") as f:
            f.write(model_path)

        with start_experiment_run(run_name="LSTM_Retrain"):
            log_params_and_metrics(
                params={
                    "model_type": "LSTM",
                    "versioned": versioned,
                    "features": ",".join(features),
                    "rows": len(df),
                    "window_size": window_size
                },
                metrics={
                    "train_loss": model.history.history['loss'][-1],
                    "train_accuracy": model.history.history['accuracy'][-1]
                }
            )
            log_artifacts(model_path, scaler_path)

        success_msg = (f"[{timestamp}] ✅ Retraining complete | "
                       f"Rows: {len(df)} | Features: {features} | "
                       f"Saved: {model_path}\n")
        print(success_msg)
        with open(log_path, "a") as f:
            f.write(success_msg)

        return True

    except Exception as e:
        error_msg = f"[{timestamp}] ❌ Retraining failed: {str(e)}\n"
        print(error_msg)
        with open(log_path, "a") as f:
            f.write(error_msg)
        return False
