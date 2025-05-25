@echo off
title 🚀 ADVANCED LIVE TRADING DASHBOARD - FULL FEATURED!
color 0B

echo.
echo ===============================================================
echo 🚀 ADVANCED LIVE TRADING DASHBOARD - MIT ALLEM DRUM UND DRAN!
echo ===============================================================
echo.
echo 📊 FEATURES:
echo    ✅ Live Candlestick Charts mit EMA-Lines
echo    ✅ Real-time Order Book (Bids/Asks)
echo    ✅ Live Portfolio Monitoring ($83.38 USDT)
echo    ✅ Trading Bot Controls (Start/Stop/Emergency)
echo    ✅ Manual Trading Buttons (BUY/SELL)
echo    ✅ Live Signal Detection (4-Filter System)
echo    ✅ Risk Management Controls
echo    ✅ Professional Trading Interface
echo.
echo ===============================================================
echo.

REM Kill any existing dashboard on port 8501
echo 🔄 Stopping old dashboard...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8501"') do taskkill /f /pid %%a 2>nul
timeout /t 2 /nobreak > nul

REM Activate conda environment
echo 🔧 Activating conda environment...
call conda activate crypto-bot_V2

if %errorlevel% neq 0 (
    echo ❌ Failed to activate conda environment!
    pause
    exit /b 1
)

echo ✅ Environment activated!
echo.

REM Change to monitoring directory
cd /d "J:\Meine Ablage\CodingStuff\crypto-bot_V2\monitoring"

REM Check for advanced dashboard
if not exist advanced_live_dashboard.py (
    echo ❌ Advanced dashboard not found!
    pause
    exit /b 1
)

echo ✅ Advanced Live Dashboard found!
echo.

echo 🚀 Starting ADVANCED LIVE TRADING DASHBOARD...
echo.
echo 💰 Deine echten $83.38 USDT werden live angezeigt!
echo 📊 Professionelle Trading Charts wie TradingView!
echo 🎮 Vollständige Bot-Kontrolle inklusive!
echo ⚡ Live Signale mit 4-Filter-System!
echo.
echo 🌐 Dashboard läuft auf: http://localhost:8501
echo.

timeout /t 3 /nobreak > nul

REM Start the ADVANCED dashboard
streamlit run advanced_live_dashboard.py --server.port 8501 --server.headless false --browser.gatherUsageStats false

echo.
echo 🏁 Advanced Dashboard beendet!
echo.
pause
