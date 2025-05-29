@echo off
echo ========================================================
echo    LIVE MAINNET DASHBOARD - STARTING UP
echo ========================================================
echo.
echo Starting dashboard with Market Regime Detection...
echo.

:: Starte das Dashboard mit absoluten Pfaden
cd J:\Meine Ablage\CodingStuff\crypto-bot_V2
streamlit run monitoring\LIVE_MAINNET_DASHBOARD.py

echo.
echo If the dashboard doesn't open automatically, visit:
echo http://localhost:8501
echo.
echo Press any key to exit...
pause > nul
