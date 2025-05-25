@echo off
title 🚀 COMPLETE LIVE TRADING SYSTEM - Bot + Dashboard
color 0B

echo.
echo =================================================================
echo 🚀 COMPLETE LIVE TRADING SYSTEM - BOT + DASHBOARD + AUDIO!
echo =================================================================
echo.
echo 🤖 Bot: Enhanced Smart Money Strategy mit Audio Alerts
echo 📊 Dashboard: Real-time Monitoring auf Port 8501  
echo 🔊 Audio: Windows Sound System für alle Trading Events
echo 💰 Trading: Live Bybit API Integration
echo.
echo =================================================================
echo.

REM Activate conda environment
echo 🔧 Activating conda environment...
call conda activate crypto-bot_V2

if %errorlevel% neq 0 (
    echo ❌ Conda environment not found!
    echo Creating new environment...
    call conda create -n crypto-bot_V2 python=3.10 -y
    call conda activate crypto-bot_V2
    echo Installing requirements...
    pip install -r requirements.txt
)

echo ✅ Environment ready!
echo.

REM Start Dashboard in background
echo 📊 Starting Dashboard auf http://localhost:8501...
start "Trading Dashboard" cmd /c "conda activate crypto-bot_V2 && cd /d "%CD%" && streamlit run monitoring\dashboard.py --server.port 8501"

echo ⏳ Warte 5 Sekunden für Dashboard-Start...
timeout /t 5 /nobreak > nul

REM Open browser to dashboard
echo 🌐 Öffne Dashboard im Browser...
start http://localhost:8501

echo.
echo 🚀 SYSTEM BEREIT!
echo.
echo 📊 Dashboard: http://localhost:8501 (läuft im Hintergrund)
echo 🤖 Bot: Startet jetzt mit Audio Alerts...
echo.
echo 🔊 AUDIO LEGEND:
echo    🎵 Startup = Aufsteigende Töne (Bot startet)
echo    🎯 BUY Signal = 2x Hohe Töne + Erfolgs-Melodie  
echo    🎯 SELL Signal = 2x Tiefe Töne + Alert-Sound
echo    ✅ Trade Success = System-Erfolg + Celebration
echo    ❌ Trade Failed = System-Fehler + Loss-Alert
echo    😐 No Signal = Kurzer tiefer Ton
echo    🛑 Shutdown = Absteigende Töne (Bot stoppt)
echo.

timeout /t 3 /nobreak > nul

REM Start the trading bot with audio
echo 🚀 Starting Enhanced Live Trading Bot...
python live_trading_bot_clean.py

echo.
echo 🏁 Trading Session beendet!
echo 📊 Dashboard läuft weiter auf: http://localhost:8501
echo 💾 Trading-Logs wurden gespeichert
echo.
echo Drücke eine Taste zum Beenden...
pause > nul
