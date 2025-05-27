@echo off
title LIVE MAINNET DASHBOARD STARTER

echo ======================================================
echo    LIVE MAINNET TRADING DASHBOARD STARTER
echo ======================================================
echo.
echo This script will:
echo 1. Install required dependencies (if needed)
echo 2. Start the Live Mainnet Dashboard
echo.
echo IMPORTANT: Make sure your .env file is configured for Mainnet:
echo - BYBIT_API_KEY is set to your Mainnet API key
echo - BYBIT_API_SECRET is set to your Mainnet API secret
echo - TESTNET=false
echo.
echo Press any key to continue or CTRL+C to cancel...
pause > nul

echo.
echo Installing dependencies...
python monitoring\install_dependencies.py

echo.
echo Starting Live Mainnet Dashboard...
start "" streamlit run monitoring\LIVE_MAINNET_DASHBOARD.py

echo.
echo Do you want to also start the Enhanced Live Trading Bot?
echo WARNING: This will execute REAL trades with REAL money!
echo.
set /p start_bot=Start trading bot? (y/n): 

if /i "%start_bot%"=="y" (
    echo.
    echo Starting Enhanced Live Trading Bot...
    start "Enhanced Live Bot" cmd /k python enhanced_live_bot.py
    echo.
    echo Both the dashboard and trading bot are now running!
) else (
    echo.
    echo Only the dashboard is running. The trading bot was not started.
)

echo.
echo IMPORTANT: To monitor the system, check the dashboard in your browser.
echo To stop the trading bot, use the EMERGENCY STOP button in the dashboard.
echo.
echo Press any key to exit this window...
pause > nul
