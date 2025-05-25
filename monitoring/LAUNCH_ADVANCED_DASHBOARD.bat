@echo off
cls
echo.
echo     ╔═══════════════════════════════════════════════════════════════╗
echo     ║                                                               ║
echo     ║     🚀 ADVANCED LIVE TRADING DASHBOARD LAUNCHER 🚀            ║
echo     ║                                                               ║
echo     ║     Professional Real-time Dashboard                          ║
echo     ║     Enhanced Smart Money Strategy                             ║
echo     ║     Production Ready for 50€ Mainnet Deployment              ║
echo     ║                                                               ║
echo     ║     Version: 2.1 - Professional Grade                        ║
echo     ║     © 2025 Advanced Trading Systems                           ║
echo     ║                                                               ║
echo     ╚═══════════════════════════════════════════════════════════════╝
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: Python is not installed or not in PATH
    echo.
    echo 📦 Please install Python 3.8+ from: https://python.org
    echo.
    pause
    exit /b 1
)

echo ✅ Python found
echo 🔍 Checking Python version...
python -c "import sys; print(f'Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')"

REM Check if we're in the right directory
if not exist "advanced_live_dashboard_final.py" (
    echo.
    echo ❌ ERROR: Dashboard files not found!
    echo 📁 Please run this script from the monitoring directory
    echo 📂 Current directory: %CD%
    echo.
    pause
    exit /b 1
)

echo ✅ Dashboard files found
echo.

REM Check for .env file
if not exist ".env" (
    echo ⚠️  WARNING: .env file not found
    echo 📝 You may need to configure API credentials
    echo.
) else (
    echo ✅ .env configuration file found
)

echo 🚀 LAUNCHING ADVANCED DASHBOARD...
echo ================================================
echo.
echo 🔥 Starting Python launcher...
echo 📊 This will open your professional trading dashboard
echo 💰 Ready for 50€ Mainnet deployment
echo 🛑 Press Ctrl+C to stop
echo.
echo ================================================

REM Launch the Python launcher
python launch_advanced_dashboard.py

REM If we get here, the launcher has finished
echo.
echo 🏁 Dashboard launcher finished
echo.
pause
