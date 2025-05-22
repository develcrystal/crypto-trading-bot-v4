@echo off
color 0A
title 🚀 Enhanced Smart Money Bot - Conda Dashboard Start

echo.
echo ========================================================
echo        🚀 ENHANCED SMART MONEY BOT V2
echo        📊 Real-time Monitoring Dashboard  
echo        🐍 Conda Environment: crypto-bot_V2
echo ========================================================
echo.

cd /d "%~dp0"

echo 🔍 Checking Conda environment...

REM Check if crypto-bot_V2 environment exists
conda env list | findstr "crypto-bot_V2" >nul
if errorlevel 1 (
    echo ❌ Conda environment 'crypto-bot_V2' not found!
    echo 📦 Creating environment...
    conda create -n crypto-bot_V2 python=3.10 -y
    if errorlevel 1 (
        echo ❌ Failed to create conda environment!
        pause
        exit /b 1
    )
)

echo ✅ Conda environment found: crypto-bot_V2
echo 🐍 Activating environment...

REM Activate conda environment and install dependencies
call conda activate crypto-bot_V2

echo 📦 Installing/updating packages in crypto-bot_V2...
call conda install -n crypto-bot_V2 pandas numpy -y
call pip install streamlit plotly

echo.
echo 🚀 Starting dashboard in conda environment...
echo 🌐 Dashboard URL: http://localhost:8501
echo 💡 Press CTRL+C to stop
echo.

REM Start dashboard in the activated environment
streamlit run dashboard.py --server.port 8501

echo.
echo 🛑 Dashboard stopped.
call conda deactivate
pause
