@echo off
echo ======================================================
echo 🚀 MAINNET DEPLOYMENT - 50 EUR TRADING
echo ======================================================
echo WARNUNG: Dieser Script bereitet ECHTES Trading vor!
echo Startkapital: 50 EUR ^| Risk: 2%% per Trade
echo Emergency Stop: 7.50 EUR (-15%%)
echo ======================================================
echo.

pause

echo Aktiviere Conda Environment...
call conda activate crypto-bot_V2

echo Starte Mainnet Deployment Script...
python deploy_mainnet_50eur.py

echo.
echo ======================================================
echo 🎯 NÄCHSTE SCHRITTE:
echo 1. python enhanced_live_bot.py
echo 2. streamlit run monitoring/bybit_focused_dashboard.py
echo ======================================================
pause
