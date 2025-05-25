@echo off
color 0A
title 🚀 SIMPLE DASHBOARD TEST

echo.
echo ========================================================
echo        🚀 SIMPLE DASHBOARD TEST
echo        📊 Minimal Working Version
echo ========================================================
echo.

cd /d "%~dp0"

echo 🐍 Activating crypto-bot_V2 environment...
call conda activate crypto-bot_V2

echo 🚀 Starting SIMPLE dashboard...
echo 🌐 URL: http://localhost:8502
echo.

streamlit run simple_dashboard.py --server.port 8502

call conda deactivate
pause
