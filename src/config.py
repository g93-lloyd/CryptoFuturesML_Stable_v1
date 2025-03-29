# src/config.py

import os
from dotenv import load_dotenv
load_dotenv()

# ==== API and Secrets from .env ====
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
API_TOKEN = os.getenv("API_TOKEN", "secret-ml-token")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# ==== Binance Environment Selection ====
BINANCE_ENV = os.getenv("BINANCE_ENV", "testnet").lower()

if BINANCE_ENV == "testnet":
    BINANCE_API_KEY = os.getenv("BINANCE_TEST_API_KEY")
    BINANCE_SECRET = os.getenv("BINANCE_TEST_API_SECRET")
    BINANCE_API_URL = "https://testnet.binancefuture.com"
else:
    BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
    BINANCE_SECRET = os.getenv("BINANCE_SECRET")
    BINANCE_API_URL = "https://fapi.binance.com"

# ==== Trading Settings ====
BINANCE_SYMBOL = "BTC/USDT"
BINANCE_TIMEFRAME = "5m"
OHLCV_LIMIT = 500
