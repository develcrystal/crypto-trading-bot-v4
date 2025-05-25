@echo off
color 0A
title 🚀 Enhanced Smart Money Bot - Monitoring Dashboard

echo.
echo ========================================================
echo        🚀 ENHANCED SMART MONEY BOT V2
echo        📊 Real-time Monitoring Dashboard  
echo        🚀 Quick Version - Ready to Launch!
echo ========================================================
echo.
echo 🎯 Features:
echo • Real-time Portfolio Monitoring
echo • Market Regime Detection  
echo • Live Trading Signals
echo • Performance Analytics
echo • Risk Management
echo • Trade History
echo.
echo ⚡ Auto-launching dashboard...
echo 🌐 URL: http://localhost:8501
echo.
echo 💡 Press CTRL+C to stop the dashboard
echo.

cd /d "%~dp0"

echo 📦 Checking dependencies...
python -c "import streamlit" 2>nul
if errorlevel 1 (
    echo ⚠️  Installing Streamlit...
    pip install streamlit plotly
)

echo 🚀 Starting dashboard...
echo.
python dashboard_launcher.py

echo.
echo Dashboard stopped.
pause >nul
