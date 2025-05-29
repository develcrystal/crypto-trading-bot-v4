@echo off
REM Installationsskript für den Bybit API Fix
REM Dieses Skript implementiert den Fix und startet das Dashboard

chcp 65001 >nul
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

setlocal enabledelayedexpansion

echo.
echo ===== BYBIT API FIX INSTALLATION =====
echo.

REM Setze Pfad zum Projektverzeichnis
set "PROJECT_DIR=J:\Meine Ablage\CodingStuff\crypto-bot_V2"

if not exist "%PROJECT_DIR%" (
    echo Fehler: Projektverzeichnis nicht gefunden: %PROJECT_DIR%
    pause
    exit /b 1
)

echo Führe Dashboard Update durch...
"%PROJECT_DIR%\venv\Scripts\python.exe" "%PROJECT_DIR%\update_dashboard.py"

if !ERRORLEVEL! NEQ 0 (
    echo.
    echo Fehler beim Update. Bitte überprüfe die Fehlermeldungen.
    echo.
    pause
    exit /b 1
)

echo.
echo Update erfolgreich abgeschlossen!
echo.
echo Möchtest du das Dashboard jetzt starten? (J/N)
choice /c JN /m "Dashboard starten"

if %ERRORLEVEL% EQU 1 (
    echo.
    echo Starte Dashboard...
    cd "%PROJECT_DIR%\monitoring"
    start streamlit run enhanced_smart_money_bot_dashboard.py
    echo.
    echo Das Dashboard wird im Browser geöffnet.
) else (
    echo.
    echo Installation abgeschlossen. Du kannst das Dashboard später starten mit:
    echo cd "%PROJECT_DIR%\monitoring"
    echo streamlit run enhanced_smart_money_bot_dashboard.py
)

echo.
echo Drücke eine Taste, um das Installationsskript zu beenden.
pause > nul
