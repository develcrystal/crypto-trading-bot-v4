@echo off
echo.
echo ====================================================
echo    STARTING LIVE MAINNET TRADING DASHBOARD
echo ====================================================
echo.
echo This dashboard connects to your REAL Bybit account!
echo All data shown is LIVE and REAL - NO SIMULATION!
echo.
echo Press any key to start...
pause > nul
cd "%~dp0\monitoring"
start http://localhost:8504
streamlit run LIVE_MAINNET_DASHBOARD.py --server.port 8504
