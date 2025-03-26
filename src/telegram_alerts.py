# src/telegram_alerts.py

from telegram import Bot
from src.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

def send_alert(message):
    try:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        print("📤 Telegram alert sent!")
    except Exception as e:
        print(f"❌ Failed to send Telegram alert: {e}")
