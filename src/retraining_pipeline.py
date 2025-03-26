# src/retraining_pipeline.py

# 🧪 Core modules for data fetching and feature engineering
from src.market_data_collector import fetch_ohlcv                      # Grabs latest OHLCV data
from src.sentiment_pipeline import fetch_twitter_sentiment            # Grabs latest Twitter sentiment
from src.feature_engineering import add_technical_indicators, merge_sentiment  # RSI, MACD, EMA + merge sentiment

# 🧠 Model training & saving logic
from src.model_trainer import prepare_data, train_lstm_model, save_model

# 📊 MLflow tracking
from src.mlflow_logger import start_experiment_run, log_params_and_metrics, log_artifacts

from datetime import datetime
import os

# 🔁 Full pipeline to retrain your LSTM model using fresh data
def retrain_pipeline(versioned=False):
    log_path = "logs/retrain_log.txt"
    os.makedirs("logs", exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        # Step 1: Fetch latest market data (5-minute candles, 1000 rows)
        print("📥 Fetching fresh market data...")
        df = fetch_ohlcv("BTC/USDT", timeframe="5m", limit=1000)

        # Step 2: Fetch fresh Twitter sentiment scores
        print("💬 Fetching latest sentiment data...")
        sentiment_scores = fetch_twitter_sentiment(limit=50)

        # Step 3: Add technical indicators and merge sentiment
        print("🧪 Engineering features...")
        df = add_technical_indicators(df)
        df = merge_sentiment(df, sentiment_scores)

        # Step 4: Convert data into supervised format for LSTM
        print("🧠 Preparing data for training...")
        features = ['rsi_14', 'ema_21', 'macd', 'sentiment']
        target_col = 'close'
        window_size = 10
        X, y, _ = prepare_data(df, feature_cols=features, target_col=target_col, window_size=window_size)

        # Step 5: Train the LSTM model on the processed features
        print("🎯 Training LSTM model...")
        model, scaler = train_lstm_model(X, y)

        # Step 6: Decide where to save the model (versioned or overwrite)
        if versioned:
            model_time = datetime.now().strftime("%Y-%m-%d_%H-%M")
            model_path = f"models/lstm_model_{model_time}.h5"
            scaler_path = f"models/scaler_{model_time}.save"
        else:
            model_path = "models/lstm_model.h5"
            scaler_path = "models/scaler.save"

        # Step 7: Save trained model and scaler
        print("💾 Saving model and scaler...")
        save_model(model, scaler, model_path, scaler_path)

        # Step 8: Update active model tracker
        with open("models/model_latest_path.txt", "w") as f:
            f.write(model_path)

        # Step 9: MLflow experiment tracking (optional but powerful)
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
                    "train_mae": model.history.history['mae'][-1]
                }
            )
            log_artifacts(model_path, scaler_path)

        # Step 10: Log success to retrain log
        success_msg = (f"[{timestamp}] ✅ Retraining complete | "
                       f"Rows: {len(df)} | Features: {features} | "
                       f"Saved: {model_path}\n")
        print(success_msg)
        with open(log_path, "a") as f:
            f.write(success_msg)

        return True

    except Exception as e:
        # Log errors to retrain log
        error_msg = f"[{timestamp}] ❌ Retraining failed: {str(e)}\n"
        print(error_msg)
        with open(log_path, "a") as f:
            f.write(error_msg)
        return False
