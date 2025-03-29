# test_telegram.py

from telegram import Bot
import os
from dotenv import load_dotenv

load_dotenv()

bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
chat_id = os.getenv("TELEGRAM_CHAT_ID")

try:
    bot.send_message(chat_id=chat_id, text="✅ Telegram test message from CryptoFuturesML!")
    print("✅ Telegram message sent successfully.")
except Exception as e:
    print(f"❌ Telegram test failed: {e}")

print("Bot Token:", bot.token)
print("Chat ID:", chat_id)
