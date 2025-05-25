@echo off
color 0A
title 🚀 Enhanced Smart Money Bot - Direct Dashboard Start

echo.
echo ========================================================
echo        🚀 ENHANCED SMART MONEY BOT V2
echo        📊 Real-time Monitoring Dashboard  
echo        🚀 Direct Start - No Menu!
echo ========================================================
echo.

cd /d "%~dp0"

echo 📦 Checking dependencies...
python -c "import streamlit" 2>nul
if errorlevel 1 (
    echo ⚠️ Installing Streamlit...
    pip install streamlit plotly pandas numpy
    echo ✅ Installation complete!
)

echo.
echo 🚀 Starting dashboard directly...
echo 🌐 Dashboard will open at: http://localhost:8501
echo.
echo ⚡ Starting in 3 seconds...
timeout /t 3 /nobreak >nul

echo 🔥 LAUNCHING DASHBOARD NOW!
echo.

REM Direct Streamlit start without menu
streamlit run dashboard.py --server.port 8501

echo.
echo 🛑 Dashboard stopped.
pause
