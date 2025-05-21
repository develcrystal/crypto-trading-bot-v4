@echo off
title Enhanced Smart Money Bot - Monitoring Dashboard

echo.
echo ======================================================
echo 🚀 CRYPTO TRADING BOT V2 - MONITORING DASHBOARD
echo ======================================================
echo.
echo Starting dashboard...
echo Dashboard will open in your browser automatically!
echo.
echo 💡 Press CTRL+C to stop the dashboard
echo 🌐 URL: http://localhost:8501
echo.

cd /d "%~dp0"
python start_dashboard.py

pause
