@echo off
echo ****************************************************
echo *                                                  *
echo *   LIVE MAINNET DASHBOARD - FIXED API VERSION     *
echo *                                                  *
echo ****************************************************
echo.
echo Starting dashboard with fixed API integration...
echo.
echo Note: If this doesn't work, make sure streamlit is installed:
echo       pip install streamlit plotly pandas python-dotenv psutil
echo.

cd /d %~dp0
streamlit run LIVE_MAINNET_DASHBOARD.py --server.port 8504

echo.
echo If the browser didn't open automatically, go to:
echo http://localhost:8504
echo.
pause
