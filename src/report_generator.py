# src/report_generator.py

from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta

def generate_daily_report():
    logs_path = Path("logs")
    reports_path = Path("reports")
    reports_path.mkdir(parents=True, exist_ok=True)

    trades_file = logs_path / "virtual_positions.csv"
    retrain_file = logs_path / "retrain_log.txt"

    df_trades = pd.read_csv(trades_file) if trades_file.exists() else pd.DataFrame()
    model_version = "N/A"

    if retrain_file.exists():
        with open(retrain_file, "r") as f:
            lines = f.readlines()
            for line in reversed(lines):
                if "Saved:" in line:
                    model_version = line.split("Saved:")[-1].strip()
                    break

    df_trades["timestamp"] = pd.to_datetime(df_trades["timestamp"])
    today = datetime.utcnow().date()
    this_week = today - timedelta(days=7)
    today_trades = df_trades[df_trades["timestamp"].dt.date == today]
    week_trades = df_trades[df_trades["timestamp"].dt.date >= this_week]

    def summarize(df):
        return {
            "count": len(df),
            "avg_pnl": round(df["pnl_percent"].mean(), 2) if not df.empty else 0,
            "win_rate": round((df["pnl_percent"] > 0).mean() * 100, 2) if not df.empty else 0,
        }

    today_stats = summarize(today_trades)
    week_stats = summarize(week_trades)
    last_balance = df_trades["balance_after"].iloc[-1] if not df_trades.empty else 10000

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Daily Report - CryptoFuturesML</title>
        <style>
            body {{ font-family: Arial; background: #111; color: #eee; padding: 20px; }}
            h1 {{ color: #1db954; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th, td {{ padding: 10px; border: 1px solid #444; text-align: center; }}
            th {{ background-color: #222; }}
            .highlight {{ color: #1ed760; font-weight: bold; }}
        </style>
    </head>
    <body>
        <h1>📊 CryptoFuturesML — Daily Summary ({today})</h1>
        <p>🧠 Model Version: <span class="highlight">{model_version}</span></p>
        <p>💰 Portfolio Balance: <span class="highlight">${last_balance:.2f}</span></p>

        <h2>📅 Today</h2>
        <table>
            <tr><th>Trades</th><th>Avg PnL (%)</th><th>Win Rate (%)</th></tr>
            <tr><td>{today_stats['count']}</td><td>{today_stats['avg_pnl']}</td><td>{today_stats['win_rate']}</td></tr>
        </table>

        <h2>📆 Last 7 Days</h2>
        <table>
            <tr><th>Trades</th><th>Avg PnL (%)</th><th>Win Rate (%)</th></tr>
            <tr><td>{week_stats['count']}</td><td>{week_stats['avg_pnl']}</td><td>{week_stats['win_rate']}</td></tr>
        </table>

        <p style="margin-top:40px; color:#777;">Generated on {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")}</p>
    </body>
    </html>
    """

    report_file = reports_path / f"daily_report_{today}.html"
    report_file.write_text(html_content)
    print(f"✅ Report generated: {report_file}")
    return report_file
