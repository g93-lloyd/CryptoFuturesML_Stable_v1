# 🤖 CryptoFuturesML v1.0

A production-grade crypto futures trading system built with LSTM + sentiment analysis.  
Optimized for transparency, modularity, and personal deployment on a VPS.

---

## 📦 Features (v1.0)
- ✅ Real-time BTC/USDT signal generation
- ✅ LSTM model (.keras) with confidence scoring
- ✅ RSI + EMA + MACD technical indicators
- ✅ Twitter sentiment (with fallback)
- ✅ Smart filtering logic before entry
- ✅ Paper trading engine + Testnet integration
- ✅ Virtual position tracker (`logs/virtual_positions.csv`)
- ✅ PnL & win rate dashboard (`Option 4`)
- ✅ Full CLI interface
- ✅ Telegram Alerts (entry/exit/confidence)
- ✅ Confidence logging and plotting (Options 6 & 7)
- ✅ Daily summary log (`daily_log.txt`)

---

## 🚀 Quickstart

```bash
cd CryptoFuturesML_Stable_v1
python main.py
```

## 🧠 System Overview

| Component               | Description                                     |
|------------------------|-------------------------------------------------|
| `main.py`              | Entry point CLI for all actions                 |
| `src/`                 | Core modules: prediction, trading, logging      |
| `logs/`                | Trade, confidence, and virtual position logs    |
| `models/`              | Saved LSTM model and scaler                     |
| `.env`                 | Stores Binance, Twitter, Telegram credentials   |

---

## 🛠️ Requirements

- Python 3.10+
- `tensorflow`, `pandas`, `matplotlib`, `python-telegram-bot`, `ccxt`
- `.env` file with these:
  ```
  TELEGRAM_BOT_TOKEN=xxx
  TELEGRAM_CHAT_ID=yyy
  BINANCE_TEST_API_KEY=zzz
  BINANCE_TEST_API_SECRET=zzz
  TWITTER_BEARER_TOKEN=zzz
  ```

---

## ✅ How to Deploy

```bash
# Pull latest repo or push from VS Code
git pull

# Activate environment (if needed)
source venv/bin/activate

# Launch system
python main.py
```

---

## 🔐 License

MIT License  
Generated on 2025-03-29 by CryptoFuturesML

# CryptoFuturesML 🚀

A professional-grade, home-deployable crypto futures machine learning trading system.

## ✅ Core Features
- Live prediction using LSTM model
- Real-time Binance Futures Testnet order execution
- Paper trading and portfolio simulation
- RSI and sentiment-based signal filtering
- Drift detection + auto retraining pipeline
- Telegram alerts (trades, critical errors)
- FastAPI endpoints for signal and dashboard
- HTML daily report generation
- CLI dashboard for quick monitoring
- Secure token-based API access
- Retry logic and health monitoring

## 🗂️ Key Files
| File | Purpose |
|------|---------|
| `main.py` | Command interface + live loop |
| `job_schedular.py` | Background task runner |
| `src/retraining_pipeline.py` | Auto model retrain logic |
| `src/live_trading_engine.py` | Model loading + signal filtering |
| `src/position_manager.py` | Position tracking and cooldown |
| `src/binance_executor.py` | Binance Testnet trade execution |
| `src/monitoring.py` | PnL & drift tracking |
| `src/alert_manager.py` | System health alerts |
| `src/utils.py` | Retry + prediction logging |
| `web/index.html` | Web UI for signal & stats |
| `logs/` | Trade, PnL, prediction logs |
| `reports/` | Daily HTML reports |

## 🚦 How to Use
1. Set up `.env` file with Binance Testnet + Telegram tokens
2. Run `main.py` for manual control or option 4 for live loop
3. Use FastAPI (`localhost:8000`) for integration
4. Deploy with `systemd` or `Docker` (Dockerfile included)
5. Monitor via CLI, browser, or Telegram

## 🔐 Security
- API access secured via bearer token
- `.env` keys ignored in `.gitignore`
- Proxy-enabled support for region-blocked access

---

### Final Checklist
- ✅ Core bot infra + live loop
- ✅ Retry logic
- ✅ Alerts + logging
- ✅ Model tracking
- ✅ Backtesting
- ✅ Security
- ✅ Reporting



🚀 VPS Migration & Recovery Guide (For CryptoFuturesML)
If you ever switch to a new VPS or change IP addresses, follow this step-by-step guide to reconfigure your environment without losing project automation or sync:

✅ Step 1: Clone the GitHub Repository
bash
Copy
Edit
git clone https://github.com/<your-username>/CryptoFuturesML_Stable_v1.git
cd CryptoFuturesML_Stable_v1
✅ Step 2: Recreate the Virtual Environment
bash
Copy
Edit
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
✅ Step 3: Restore Git Automation
Append the following to your ~/.bashrc:

bash
Copy
Edit
# Auto-sync with GitHub on terminal login
alias git-resync='git fetch origin && git reset --hard origin/main && git clean -fd && echo "✅ Project resynced to match GitHub (origin/main)"'
git-resync  # Auto-run on login
Then activate:

bash
Copy
Edit
source ~/.bashrc
✅ Step 4: Check Git Connection
Ensure your VPS has the correct SSH key or access to GitHub:

bash
Copy
Edit
git status
✅ Step 5: Reconnect ngrok (Optional for Remote Access)
If using ngrok for VPS access:

Install ngrok

Re-authenticate (ngrok config add-authtoken <your_token>)

Launch your tunnels again

📁 Additional Notes
Don’t use nano to manually change code unless you git add + commit + push to sync with GitHub.

Always edit code via VS Code, commit, and push from there to keep it clean.

Weekly auto-cleanup is scheduled for logs/git_sync_log.txt.