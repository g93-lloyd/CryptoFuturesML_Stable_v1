# src/daily_summary.py

import pandas as pd
from datetime import datetime
from src.telegram_alerts import send_alert

def send_daily_summary():
    try:
        df = pd.read_csv("logs/trade_log.csv")
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        today = datetime.now().date()
        today_trades = df[df['timestamp'].dt.date == today]

        if today_trades.empty:
            send_alert("📭 No trades recorded today.")
            return

        total = len(today_trades)
        longs = (today_trades['signal'] == "LONG").sum()
        shorts = (today_trades['signal'] == "SHORT").sum()
        holds = (today_trades['signal'] == "HOLD").sum()
        avg_conf = today_trades['confidence'].mean()

        # PnL metrics
        closed_trades = today_trades[today_trades['pnl_percent'].notna()]
        avg_pnl = closed_trades['pnl_percent'].mean() if not closed_trades.empty else 0.0
        win_rate = (closed_trades['pnl_percent'] > 0).mean() * 100 if not closed_trades.empty else 0.0

        summary = (
            f"📊 Daily Summary ({today}):\n"
            f"───────────────────────\n"
            f"📈 Trades: {total}\n"
            f"🟩 LONG: {longs} | 🔻 SHORT: {shorts} | ⚪ HOLD: {holds}\n"
            f"⚡ Avg Confidence: {avg_conf:.2%}\n"
            f"💰 Avg PnL: {avg_pnl:.2f}%\n"
            f"🥇 Win Rate: {win_rate:.1f}% ({len(closed_trades)} closed)\n"
            f"🕒 Sent at: {datetime.now().strftime('%H:%M:%S')}"
        )

        send_alert(summary)

    except Exception as e:
        send_alert(f"❌ Summary failed: {e}")
