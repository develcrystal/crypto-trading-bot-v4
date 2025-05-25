@echo off
title 🚀 LIVE TRADING BOT - Enhanced Smart Money Strategy
color 0A

echo.
echo ===============================================================
echo 🚀 ENHANCED SMART MONEY LIVE TRADING BOT - MIT AUDIO ALERTS!
echo ===============================================================
echo.
echo 🔊 Audio System: AKTIVIERT
echo 🎯 Enhanced Strategy: BEREIT  
echo 💰 Bybit Integration: LIVE
echo 📊 Dashboard: http://localhost:8501
echo.
echo ===============================================================
echo.

REM Activate conda environment
echo 🔧 Activating conda environment...
call conda activate crypto-bot_V2

REM Check if activation was successful
if %errorlevel% neq 0 (
    echo ❌ Failed to activate conda environment!
    echo Please run: conda create -n crypto-bot_V2 python=3.10
    pause
    exit /b 1
)

echo ✅ Conda environment activated!
echo.

REM Check .env file
if not exist .env (
    echo ❌ .env file nicht gefunden!
    echo Bitte .env.example zu .env kopieren und API Keys eintragen!
    pause
    exit /b 1
)

echo ✅ .env file found!
echo.

REM Show current directory
echo 📁 Current Directory: %CD%
echo.

REM Start the live trading bot with audio alerts
echo 🚀 Starting Enhanced Live Trading Bot with Audio Alerts...
echo.
echo ⚠️  ACHTUNG: Bot wird jetzt mit ECHTEN API Credentials starten!
echo 💰 Bei TESTNET=false werden ECHTE Trades ausgeführt!
echo.
echo 🔊 Höre auf Audio-Signale:
echo    🎵 Startup: Aufsteigende Töne
echo    🎯 Signal: Hohe Töne = BUY, Tiefe Töne = SELL  
echo    ✅ Success: Erfolgs-Melodie
echo    ❌ Error: Fehler-Sounds
echo    🛑 Shutdown: Absteigende Töne
echo.

timeout /t 3 /nobreak > nul

python live_trading_bot_clean.py

echo.
echo 🏁 Trading Bot Session beendet!
echo 📊 Check dein Dashboard für Details: http://localhost:8501
echo.
pause
