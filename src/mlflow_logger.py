# src/mlflow_logger.py

import mlflow
import os
from datetime import datetime

def start_experiment_run(experiment_name="CryptoFuturesML", run_name=None):
    """
    Starts an MLflow run under the specified experiment.
    """
    mlflow.set_tracking_uri("file://" + os.path.abspath("mlruns"))
    mlflow.set_experiment(experiment_name)
    return mlflow.start_run(run_name=run_name or f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}")

def log_params_and_metrics(params: dict, metrics: dict):
    """
    Log training parameters and evaluation metrics to MLflow.
    """
    for key, val in params.items():
        mlflow.log_param(key, val)
    for key, val in metrics.items():
        mlflow.log_metric(key, val)

def log_artifacts(model_path: str, scaler_path: str = None):
    """
    Log saved model and scaler paths as artifacts.
    """
    if os.path.exists(model_path):
        mlflow.log_artifact(model_path, artifact_path="models")
    if scaler_path and os.path.exists(scaler_path):
        mlflow.log_artifact(scaler_path, artifact_path="scalers")
