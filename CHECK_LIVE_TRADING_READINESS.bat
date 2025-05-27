@echo off
title LIVE MAINNET READINESS CHECK

echo ======================================================
echo    LIVE MAINNET TRADING READINESS CHECK
echo ======================================================
echo.
echo Dieses Tool prüft, ob dein System bereit für
echo Live Trading mit echtem Geld ist.
echo.
echo Folgende Komponenten werden überprüft:
echo - Notwendige Python-Pakete
echo - Existenz aller erforderlichen Dateien
echo - API-Konfiguration in .env
echo - Bybit API-Verbindung
echo - 50€ Deployment-Konfiguration
echo.
echo HINWEIS: Diese Überprüfung dauert etwa 10 Sekunden...
echo.
echo Drücke eine beliebige Taste um die Überprüfung zu starten...
pause > nul

echo.
echo Führe Readiness Check aus...
python check_live_trading_readiness.py

echo.
echo Drücke eine beliebige Taste um das Fenster zu schließen...
pause > nul
