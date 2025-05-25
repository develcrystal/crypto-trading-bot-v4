@echo off
color 0A
title 🚀 Enhanced Smart Money Bot - Simple Conda Start

echo.
echo ========================================================
echo        🚀 ENHANCED SMART MONEY BOT V2
echo        📊 Real-time Monitoring Dashboard  
echo        🐍 Using EXISTING crypto-bot_V2 environment
echo ========================================================
echo.

cd /d "%~dp0"

echo 🐍 Activating existing crypto-bot_V2 environment...
call conda activate crypto-bot_V2

if errorlevel 1 (
    echo ❌ Failed to activate crypto-bot_V2 environment!
    echo 💡 Make sure you're in the right conda environment
    pause
    exit /b 1
)

echo ✅ Environment activated: crypto-bot_V2
echo 🚀 Starting dashboard with existing packages...
echo 🌐 Dashboard URL: http://localhost:8501
echo.
echo 💡 Press CTRL+C to stop dashboard
echo.

REM Start dashboard directly - NO INSTALLATION
streamlit run dashboard.py --server.port 8501

echo.
echo 🛑 Dashboard stopped.
call conda deactivate
pause
