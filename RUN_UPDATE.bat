@echo off
chcp 65001 >nul

echo.
echo ===== DASHBOARD UPDATE =====
echo.

set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

python update_dashboard.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Update fehlgeschlagen. Bitte ueberpruefen Sie die Fehlermeldungen.
    pause
    exit /b 1
)

echo.
echo Update erfolgreich abgeschlossen!
echo.
pause
