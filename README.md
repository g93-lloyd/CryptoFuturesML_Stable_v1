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