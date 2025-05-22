@echo off
echo.
echo 🚀 LIVE BYBIT TESTNET DASHBOARD
echo ================================
echo.
echo 🔴 CONNECTING TO LIVE BYBIT TESTNET API...
echo 💰 Your real Testnet balance will be displayed
echo 📊 Live market data streaming from Bybit
echo 🧪 TESTNET ONLY - No real money at risk
echo.

cd /d "J:\Meine Ablage\CodingStuff\crypto-bot_V2\monitoring"

echo 🔧 Activating crypto-bot_V2 environment...
call conda activate crypto-bot_V2

echo 📦 Ensuring dependencies are installed...
pip install plotly streamlit pandas numpy python-dateutil --quiet > nul 2>&1

echo.
echo 🚀 Launching LIVE Dashboard...
echo 🌐 Dashboard will be available at: http://localhost:8504
echo.
echo ⚡ LIVE Features Active:
echo   - ✅ Real Bybit Testnet API connection
echo   - 💰 Live wallet balance display
echo   - 📊 Real market data streaming
echo   - 📋 Actual trade history from Testnet
echo   - 🔄 30-second auto-refresh option
echo.
echo 🧪 SAFETY: This connects to Bybit TESTNET only!
echo 💰 NO REAL MONEY IS AT RISK!
echo.

start /b "" "http://localhost:8504"
streamlit run live_dashboard.py --server.port 8504

pause
