@echo off
echo 🚀 LAUNCHING MODULAR ADVANCED LIVE TRADING DASHBOARD
echo ========================================================
echo 💰 MAINNET MODE - REAL $50.00 USDT!
echo 🔄 Modular Architecture - Better Performance
echo 📊 Professional Trading Interface
echo ========================================================
echo.

cd /d "J:\Meine Ablage\CodingStuff\crypto-bot_V2"

REM Activate conda environment if it exists
if exist "%USERPROFILE%\miniconda3\envs\crypto-bot_V2" (
    echo 🐍 Activating crypto-bot_V2 environment...
    call "%USERPROFILE%\miniconda3\Scripts\activate.bat" crypto-bot_V2
) else (
    echo ℹ️ Using system Python...
)

echo 🎯 Starting modular dashboard...
python launch_modular_dashboard.py

echo.
echo 📊 Dashboard closed. Press any key to exit...
pause >nul
