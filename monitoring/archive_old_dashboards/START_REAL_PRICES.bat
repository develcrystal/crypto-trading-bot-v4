@echo off
echo.
echo 💹 DASHBOARD MIT ECHTEN LIVE-PREISEN - FIX
echo ========================================
echo.
echo 🎯 PROBLEM GELÖST:
echo   ✅ Direkte API-Calls zu Bybit
echo   ✅ Mehrere Datenquellen (Bybit + CoinGecko)
echo   ✅ Echte Live-Preise (keine Fallback-Daten)
echo   ✅ Preisvergleich mit TradingView möglich
echo.
echo 📊 DATENQUELLEN:
echo   1. Bybit Testnet API (primär)
echo   2. Bybit Mainnet API (Referenz)
echo   3. CoinGecko API (Fallback)
echo.
echo 🚀 NEUE FEATURES:
echo   • Echte Live-Preise (~$111k wie TradingView)
echo   • 15-Sekunden Auto-Refresh
echo   • Preisquellen-Anzeige
echo   • Manuelle Verifikations-Hinweise
echo.

cd /d "J:\Meine Ablage\CodingStuff\crypto-bot_V2\monitoring"

echo 🔧 Aktiviere Environment...
call conda activate crypto-bot_V2

echo 📦 Installiere Dependencies für Real-Time Pricing...
pip install requests --quiet

echo.
echo 🌐 REAL-TIME DASHBOARD startet auf: http://localhost:8506
echo 💹 Zeigt ECHTE Live-Preise von mehreren Quellen
echo 🔄 Auto-Refresh: Alle 15 Sekunden
echo.

start /b "" "http://localhost:8506"
streamlit run live_dashboard_real_prices.py --server.port 8506

pause
