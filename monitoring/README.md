# 🚀 Enhanced Smart Money Trading Bot - Dashboard

## 📊 Professional Real-time Monitoring System
**Version:** 2.0 Enhanced  
**Status:** Production Ready  
**Last Update:** 21.05.2025

![Dashboard Status](https://img.shields.io/badge/Status-Production_Ready-green)
![Bybit API](https://img.shields.io/badge/Bybit_API-Connected-blue)
![Enhanced Strategy](https://img.shields.io/badge/Strategy-Enhanced_Smart_Money-orange)

---

## 🎯 Features

### 🚀 Core Dashboard Components
- **📊 Professional Real-time Dashboard**: Comprehensive monitoring of all trading metrics
- **🧠 Market Regime Detection**: Automatic Bull/Bear/Sideways market identification
- **📈 Performance Analytics**: Interactive equity curve and performance metrics 
- **⚡ Live Trading Signals**: Real-time signal monitoring with filter breakdown
- **🛡️ Risk Management**: Advanced risk metrics, exposure tracking, and safety limits
- **📋 Trade History**: Complete trade log with filtering and export

### ⚙️ Enhanced Features
- **Adaptive Trading Parameters**: Automatically adjusts based on market regime
- **Advanced Market Analytics**: Signal strength assessment and regime confidence
- **Emergency Controls**: Immediate trading halt and system reset functions
- **Real-time Alerts**: Visual notifications for critical events
- **Data Export**: CSV and report generation capabilities

---

## 🚀 Quick Start

### Option 1: One-Click Launch (Recommended)
Simply run the `START_ENHANCED.bat` file to launch the dashboard with all features.

### Option 2: Manual Launch
```bash
# Navigate to monitoring directory
cd J:\Meine Ablage\CodingStuff\crypto-bot_V2\monitoring

# Activate conda environment
conda activate crypto-bot_V2

# Launch dashboard
streamlit run enhanced_dashboard.py --server.port 8503
```

---

## 📋 Dashboard Sections

### 1. Main Overview
Key metrics including Portfolio Value, PnL, Trade Count, Win Rate, and BTC Price

### 2. Market Regime Analysis
- Current market regime (Bull/Bear/Sideways)
- Confidence score and regime duration
- Score breakdown by regime type
- Adaptive parameter adjustments

### 3. Performance Analytics
- Interactive equity curve
- Drawdown analysis
- Risk-adjusted performance metrics
- Profit factor and Sharpe ratio

### 4. Live Signals Panel
- Current trading signal status
- Filter breakdown with detailed metrics
- Signal strength assessment
- Next analysis countdown

### 5. Risk Management Dashboard
- Portfolio exposure gauge
- Daily risk budget tracking
- Health status monitoring
- Maximum drawdown tracking

### 6. Trade History Log
- Recent trades with outcome details
- Performance statistics by trade
- Filtering capabilities
- Export functionality

---

## ⚙️ Configuration Options

The dashboard offers several configuration options accessible via the sidebar:

- **🔄 Auto-Refresh**: Toggle automatic 5-second refresh
- **🌍 Trading Session**: Shows current active trading session
- **🚨 Emergency Controls**: Stop, pause, or reset trading operations
- **📥 Data Export**: Generate CSV files or complete reports

---

## 📋 System Requirements

- **Python 3.8+**
- **Dependencies**:
  - streamlit
  - pandas
  - numpy
  - plotly
  - python-dateutil

These are automatically installed when using the `START_ENHANCED.bat` file.

---

## 🔧 Troubleshooting

### Dashboard Not Loading
- Try an alternative port by editing the port number in `START_ENHANCED.bat`
- Ensure all dependencies are installed using `INSTALL_MISSING.bat`
- Check if another dashboard instance is already running

### Data Not Updating
- Verify Auto-Refresh is enabled in the sidebar
- Check system status indicators in sidebar
- Restart the dashboard for a complete refresh

---

## 📞 Support

For assistance, contact the development team at support@romainhill.com or check the developer documentation in the project wiki.

---

## 🔒 Legal Disclaimer

This software is provided for educational purposes only. Trading cryptocurrency carries significant risk of financial loss. Past performance is not indicative of future results. Use this software at your own risk.

---

© 2025 Romain Hill - All Rights Reserved
