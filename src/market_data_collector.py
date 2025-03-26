# src/market_data_collector.py

import ccxt                      # Crypto exchange API wrapper
import pandas as pd              # Dataframe management
import os
import time
import random

# Configurable constants from your config.py
from config import BINANCE_SYMBOL, BINANCE_TIMEFRAME, OHLCV_LIMIT

# Retry decorator (auto-retries if ccxt fails due to rate limit/network)
from src.utils import retry

# Set to True if routing through VPS/ngrok proxy (to bypass Binance UK block)
USE_PROXY = True

# Proxy endpoint — should match your VPS tunnel (e.g., TinyProxy on port 8888)
PROXY_URL = "http://localhost:8888"

# 📈 Fetch OHLCV data from Binance using ccxt
@retry(max_attempts=4, delay=1, backoff=2)
def fetch_ohlcv(symbol=BINANCE_SYMBOL, timeframe=BINANCE_TIMEFRAME, limit=OHLCV_LIMIT):
    # Light random delay to reduce API spam / prevent IP bans
    time.sleep(random.uniform(0.5, 1.5))

    # Basic exchange configuration
    exchange_config = {
        'enableRateLimit': True,                          # Prevents hitting Binance limits
        'options': {'defaultType': 'future'}              # Use Binance Futures market
    }

    # If proxy usage is enabled, route HTTP requests through the specified proxy
    if USE_PROXY:
        exchange_config['proxies'] = {
            'http': PROXY_URL,
            'https': PROXY_URL,
        }

    # Initialize the ccxt Binance instance with or without proxy
    exchange = ccxt.binance(exchange_config)

    # Fetch OHLCV candles (default = latest N candles)
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)

    # Convert to Pandas DataFrame
    df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

    return df  # Ready for feature_engineering
