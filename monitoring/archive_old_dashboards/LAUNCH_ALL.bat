@echo off
echo.
echo 🚀 CRYPTO TRADING BOT V2 - DASHBOARD LAUNCHER
echo ==============================================
echo.
echo 🎯 Wähle dein Dashboard:
echo.
echo [1] 🎭 DEMO Dashboard (Port 8502)
echo     └─ Simulierte Daten, Offline-Testing
echo.
echo [2] 🚀 ENHANCED Demo (Port 8503) 
echo     └─ Professionelle Features, Demo-Daten
echo.
echo [3] 🔴 LIVE Bybit Testnet (Port 8504) **EMPFOHLEN**
echo     └─ Echte Testnet-Daten, API-Verbindung
echo.
echo [4] 📋 Alle Dashboards gleichzeitig
echo.
echo [0] ❌ Beenden
echo.

set /p choice="👉 Deine Wahl (1-4): "

if "%choice%"=="1" goto demo
if "%choice%"=="2" goto enhanced  
if "%choice%"=="3" goto live
if "%choice%"=="4" goto all
if "%choice%"=="0" goto exit
goto invalid

:demo
echo.
echo 🎭 Starte DEMO Dashboard...
echo 🌐 URL: http://localhost:8502
start /b "" "http://localhost:8502"
call conda activate crypto-bot_V2
streamlit run simple_dashboard.py --server.port 8502
goto end

:enhanced
echo.
echo 🚀 Starte ENHANCED Demo Dashboard...
echo 🌐 URL: http://localhost:8503
start /b "" "http://localhost:8503"
call conda activate crypto-bot_V2
streamlit run enhanced_dashboard.py --server.port 8503
goto end

:live
echo.
echo 🔴 Starte LIVE Bybit Testnet Dashboard...
echo 🌐 URL: http://localhost:8504
echo 💰 Verbinde mit echten Testnet-Daten...
start /b "" "http://localhost:8504"
call conda activate crypto-bot_V2
streamlit run live_dashboard.py --server.port 8504
goto end

:all
echo.
echo 🚀 Starte ALLE Dashboards gleichzeitig...
echo.
echo 🎭 Demo Dashboard: http://localhost:8502
start /min cmd /c "conda activate crypto-bot_V2 && streamlit run simple_dashboard.py --server.port 8502"
timeout /t 3 /nobreak > nul

echo 🚀 Enhanced Demo: http://localhost:8503  
start /min cmd /c "conda activate crypto-bot_V2 && streamlit run enhanced_dashboard.py --server.port 8503"
timeout /t 3 /nobreak > nul

echo 🔴 LIVE Testnet: http://localhost:8504
start /min cmd /c "conda activate crypto-bot_V2 && streamlit run live_dashboard.py --server.port 8504"
timeout /t 3 /nobreak > nul

echo.
echo ✅ Alle Dashboards gestartet!
echo 🌐 Öffne Browser-Tabs:
start "" "http://localhost:8502"
timeout /t 2 /nobreak > nul
start "" "http://localhost:8503"  
timeout /t 2 /nobreak > nul
start "" "http://localhost:8504"
goto end

:invalid
echo.
echo ❌ Ungültige Auswahl. Bitte wähle 1-4 oder 0.
timeout /t 2 /nobreak > nul
goto start

:exit
echo.
echo 👋 Auf Wiedersehen!
goto end

:end
echo.
echo 🏆 Dashboard erfolgreich gestartet!
echo.
pause
