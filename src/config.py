# src/config.py

import os
from dotenv import load_dotenv
load_dotenv()

TWITTER_BEARER_TOKEN = os.getenv("AAAAAAAAAAAAAAAAAAAAACyE0AEAAAAAtXjgWXsuiHJ6lZQ8MUGefo3FlUI%3DLOqNpsgjvvXeJcJp733Wf1U0Ntz3nyR0tGDLv0s3brdIBUTVyE")

API_TOKEN = os.getenv("API_TOKEN", "secret-ml-token")

# ==== Binance Environment Selection ====
# Set BINANCE_ENV to either "testnet" or "mainnet" in your .env file
BINANCE_ENV = os.getenv("BINANCE_ENV", "testnet").lower()

# ==== Binance Keys ====
if BINANCE_ENV == "testnet":
    BINANCE_API_KEY = os.getenv("919673c06d9565fa8e566d1def5bda7a934e39f7bc098b92a815367653104bca")
    BINANCE_SECRET = os.getenv("2a77872bcb122f7ab5af66459631469f6280e049c29782574144ec640e61e130")
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

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "7436804274:AAE-3XuFTvSuOSjJ3yOd3xpHOKAlsRUkMqw")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "1237159493")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "7436804274:AAE-3XuFTvSuOSjJ3yOd3xpHOKAlsRUkMqw")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "1237159493")

