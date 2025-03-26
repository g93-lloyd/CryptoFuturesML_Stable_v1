# src/binance_executor.py

import ccxt
from src.config import (
    BINANCE_API_KEY,
    BINANCE_SECRET,
    BINANCE_API_URL,
    BINANCE_SYMBOL,
    BINANCE_ENV
)

# 🔐 Initialize Binance Futures client (Testnet or Mainnet)
def get_binance_client():
    return ccxt.binance({
        'apiKey': BINANCE_API_KEY,
        'secret': BINANCE_SECRET,
        'enableRateLimit': True,
        'options': {
            'defaultType': 'future'
        },
        'urls': {
            'api': {
                'public': BINANCE_API_URL,
                'private': BINANCE_API_URL
            }
        }
    })

# 🟢 Place a market order (buy or sell)
def place_order(side="buy", amount=0.001, symbol=BINANCE_SYMBOL):
    try:
        client = get_binance_client()
        order = client.create_market_order(symbol=symbol, side=side, amount=amount)
        print(f"✅ Order executed: {side.upper()} {amount} {symbol}")
        return order
    except Exception as e:
        print(f"❌ Failed to place order: {e}")
        return None

# 🧹 Cancel all open orders for a symbol
def cancel_all_orders(symbol=BINANCE_SYMBOL):
    try:
        client = get_binance_client()
        orders = client.fetch_open_orders(symbol)

        if not orders:
            print(f"✅ No open orders to cancel for {symbol}")
            return

        for order in orders:
            client.cancel_order(order['id'], symbol)
            print(f"🚫 Canceled order ID: {order['id']}")

        print(f"🧹 Total {len(orders)} open orders cancelled for {symbol}")

    except Exception as e:
        print(f"❌ Failed to cancel orders: {e}")

# 💰 Fetch account balance (default USDT)
def get_balance(asset="USDT"):
    try:
        client = get_binance_client()
        balance = client.fetch_balance()
        free = balance['total'].get(asset, 0)
        print(f"💰 Available {asset}: {free}")
        return free
    except Exception as e:
        print(f"❌ Failed to fetch balance: {e}")
        return 0
