@echo off
title 💰 LIVE MAINNET DASHBOARD - ECHTE $83.38 USDT!
color 0C

echo.
echo ===============================================================
echo 💰 LIVE BYBIT MAINNET DASHBOARD - KEINE SIMULATION! 💰
echo ===============================================================
echo.
echo 🔴 ACHTUNG: Dieses Dashboard zeigt ECHTE MAINNET DATEN!
echo 💰 Balance: $83.38 USDT (REAL)
echo 🚀 API: Bybit Mainnet (LIVE)
echo 📊 Preise: 100%% LIVE von Bybit
echo.
echo ===============================================================
echo.

REM Kill any existing dashboard on port 8501
echo 🔄 Stopping old dashboard on port 8501...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8501"') do taskkill /f /pid %%a 2>nul
timeout /t 2 /nobreak > nul

REM Activate conda environment
echo 🔧 Activating conda environment...
call conda activate crypto-bot_V2

if %errorlevel% neq 0 (
    echo ❌ Failed to activate conda environment!
    echo Please run: conda create -n crypto-bot_V2 python=3.10
    pause
    exit /b 1
)

echo ✅ Environment activated!
echo.

REM Check if .env exists
if not exist .env (
    echo ❌ .env file not found!
    echo Please create .env with your Bybit Mainnet API credentials!
    pause
    exit /b 1
)

echo ✅ .env file found!
echo.

REM Change to monitoring directory
cd /d "J:\Meine Ablage\CodingStuff\crypto-bot_V2\monitoring"

REM Verify the new dashboard file exists
if not exist LIVE_MAINNET_DASHBOARD.py (
    echo ❌ LIVE_MAINNET_DASHBOARD.py not found!
    echo Please ensure the file exists in the monitoring directory.
    pause
    exit /b 1
)

echo ✅ Live Mainnet Dashboard found!
echo.

echo 🚀 Starting LIVE MAINNET DASHBOARD...
echo.
echo 💰 Das Dashboard wird deine ECHTEN $83.38 USDT anzeigen!
echo 📊 Alle Daten kommen LIVE von deinem Bybit Mainnet Account!
echo 🔴 KEINE SIMULATION - NUR ECHTE DATEN!
echo.
echo 🌐 Dashboard öffnet auf: http://localhost:8501
echo.

timeout /t 3 /nobreak > nul

REM Start the LIVE MAINNET dashboard
streamlit run LIVE_MAINNET_DASHBOARD.py --server.port 8501 --server.headless false --browser.gatherUsageStats false

echo.
echo 🏁 Live Mainnet Dashboard beendet!
echo.
pause
