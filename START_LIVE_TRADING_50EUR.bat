@echo off
title 🚀 LIVE TRADING - Enhanced Smart Money Bot - 50 EUR
color 0A

echo ======================================================
echo 🚀 LIVE TRADING SESSION - ENHANCED SMART MONEY BOT
echo ======================================================
echo 💰 Kapital: 50 EUR USDT
echo 🎯 Strategy: Enhanced Smart Money mit Market Regime Detection
echo 🛡️ Risk: 2%% per Trade (1 EUR max)
echo ⚠️  Emergency Stop: 7.50 EUR (-15%%)
echo ======================================================
echo.

echo ⚠️  ACHTUNG: ECHTES TRADING MIT ECHTEM GELD!
echo.
set /p confirm="Bereit für Live Trading? (ja/NEIN): "
if /i not "%confirm%"=="ja" (
    echo ❌ Live Trading abgebrochen.
    pause
    exit
)

echo.
echo 🔧 Aktiviere Conda Environment...
call conda activate crypto-bot_V2

echo.
echo 🚀 Starte Enhanced Live Trading Bot...
echo Dashboard wird automatisch auf Port 8505 gestartet...
echo.

start "📊 Dashboard" cmd /c "streamlit run monitoring/bybit_focused_dashboard.py --server.port 8505"

timeout /t 5 /nobreak > nul

echo 🤖 Starte Trading Bot...
python enhanced_live_bot.py

echo.
echo ✅ Trading Session beendet.
pause
