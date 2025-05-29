@echo off
echo ========================================================
echo    EINFACHES BOT DASHBOARD STARTEN
echo ========================================================
echo.

:: Aktiviere die Conda-Umgebung
call D:\miniconda3\Scripts\activate.bat crypto-bot_V2

:: Wechsle ins Projektverzeichnis
cd /d "J:\Meine Ablage\CodingStuff\crypto-bot_V2"

:: Starte das Dashboard
echo Starting Streamlit server...
streamlit run monitoring\simple_dashboard.py

echo.
echo Press any key to exit...
pause > nul
