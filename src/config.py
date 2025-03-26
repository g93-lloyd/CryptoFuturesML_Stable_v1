# src/config.py

import os
from dotenv import load_dotenv
load_dotenv()

API_TOKEN = os.getenv("API_TOKEN", "secret-ml-token")

# ==== Binance Environment Selection ====
# Set BINANCE_ENV to either "testnet" or "mainnet" in your .env file
BINANCE_ENV = os.getenv("BINANCE_ENV", "testnet").lower()

# ==== Binance Keys ====
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

# ==== Twitter Sentiment ====
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
