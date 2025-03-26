# api/main.py — Crypto ML API (Secure)

from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from src.live_trading_engine import predict_and_trade
from src.position_manager import position_state
from src.config import API_TOKEN
import pandas as pd
import os

app = FastAPI(title="Crypto ML API")

class PredictResponse(BaseModel):
    signal: str
    confidence: float

def verify_token(request: Request):
    token = request.headers.get("Authorization")
    if token != f"Bearer {API_TOKEN}":
        raise HTTPException(status_code=401, detail="Unauthorized")

@app.get("/")
def root():
    return {"status": "Crypto ML API is live!"}

@app.get("/predict", response_model=PredictResponse)
def predict(request: Request):
    verify_token(request)
    signal, confidence = predict_and_trade(return_result=True)
    return {"signal": signal, "confidence": confidence}

@app.get("/dashboard-data")
def dashboard_data(request: Request):
    verify_token(request)

    data = {
        "last_signal": position_state["type"] or "None",
        "is_open": position_state["is_open"],
        "entry_price": position_state["entry_price"],
        "balance": round(position_state["balance"], 2),
        "cooldown_until": str(position_state["cooldown_until"]) if position_state["cooldown_until"] else "None",
    }

    if os.path.exists("logs/virtual_positions.csv"):
        df = pd.read_csv("logs/virtual_positions.csv")
        if not df.empty:
            last_pnl = df['pnl_percent'].iloc[-1]
            data["last_pnl"] = round(last_pnl, 2)

    return data
