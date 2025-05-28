@echo off
echo ========================================================
echo    ENHANCED TRADING DASHBOARD - LIVE MAINNET VERSION
echo ========================================================
echo.
echo Starting enhanced dashboard with Market Regime Detection...
echo.

:: Aktiviere die Conda-Umgebung
call D:\miniconda3\Scripts\activate.bat crypto-bot_V2

:: Starte das Dashboard
echo Starting Streamlit server...
streamlit run J:\Meine Ablage\CodingStuff\crypto-bot_V2\monitoring\LIVE_MAINNET_DASHBOARD.py

echo.
echo If the dashboard doesn't open automatically, visit:
echo http://localhost:8501
echo.
echo Press any key to exit...
pause > nul
