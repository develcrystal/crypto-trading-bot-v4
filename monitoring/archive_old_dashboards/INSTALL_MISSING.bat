@echo off
echo.
echo 📦 INSTALLING ENHANCED DASHBOARD DEPENDENCIES
echo =============================================
echo.

cd /d "J:\Meine Ablage\CodingStuff\crypto-bot_V2\monitoring"

echo 🔧 Activating crypto-bot_V2 environment...
call conda activate crypto-bot_V2

echo.
echo 📦 Installing required packages...
pip install -r requirements.txt

echo.
echo ✅ Installation complete! You can now run START_ENHANCED.bat
echo.

pause
