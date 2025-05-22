@echo off
color 0A
title 🔧 Fixed Dashboard - No Config Errors

echo.
echo ========================================================
echo        🔧 FIXED DASHBOARD VERSION  
echo        📊 Real-time Monitoring Dashboard
echo        ✅ No Config Errors - Pure Demo Data
echo ========================================================
echo.

cd /d "%~dp0"

echo 🐍 Activating crypto-bot_V2 environment...
call conda activate crypto-bot_V2

if errorlevel 1 (
    echo ❌ Failed to activate crypto-bot_V2 environment!
    pause
    exit /b 1
)

echo ✅ Environment activated: crypto-bot_V2
echo 🔧 Starting FIXED dashboard version...
echo 🌐 Dashboard URL: http://localhost:8501
echo.
echo 💡 Press CTRL+C to stop dashboard
echo.

REM Start fixed dashboard version
streamlit run dashboard_fixed.py --server.port 8501

echo.
echo 🛑 Dashboard stopped.
call conda deactivate
pause
