@echo off
echo ----------------------------------------
echo Starte Enhanced Smart Money Bot Dashboard
echo ----------------------------------------
echo.

cd %~dp0
echo Aktuelles Verzeichnis: %CD%
echo.

REM Prüfen, ob Python im Pfad ist
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo FEHLER: Python wurde nicht gefunden!
    echo Bitte stellen Sie sicher, dass Python installiert ist und im PATH steht.
    goto :EOF
)

REM Prüfen, ob Streamlit installiert ist
python -c "import streamlit" >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Streamlit nicht gefunden. Installiere Streamlit...
    pip install streamlit
)

REM Prüfen, ob pybit installiert ist
python -c "import pybit" >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo pybit nicht gefunden. Installiere pybit...
    pip install pybit
)

echo Voraussetzungen erfüllt. Starte Dashboard...
echo.
echo Dashboard wird in Ihrem Browser geöffnet...
echo.
echo Drücken Sie STRG+C im Terminal, um das Dashboard zu beenden.
echo.

streamlit run enhanced_smart_money_bot_dashboard.py --server.port 8505

pause
