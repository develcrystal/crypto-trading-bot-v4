@echo off
echo.
echo 🚀 ENHANCED SMART MONEY BOT DASHBOARD
echo ======================================
echo.
echo 🎯 Starting Enhanced Dashboard with Professional Features...
echo.

cd /d "J:\Meine Ablage\CodingStuff\crypto-bot_V2\monitoring"

echo 🔧 Activating crypto-bot_V2 environment...
call conda activate crypto-bot_V2

echo 📦 Installing missing dependencies...
pip install plotly --quiet > nul 2>&1
pip install streamlit --quiet > nul 2>&1

echo.
echo 🚀 Launching Enhanced Dashboard...
echo 🌐 Dashboard will be available at: http://localhost:8503
echo.
echo ⚡ Features Active:
echo   - Real-time Market Regime Detection
echo   - Advanced Performance Analytics  
echo   - Professional Risk Management
echo   - Live Signal Monitoring
echo   - Interactive Charts & Gauges
echo.

start /b "" "http://localhost:8503"
streamlit run enhanced_dashboard.py --server.port 8503

pause
