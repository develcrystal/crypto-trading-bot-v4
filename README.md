# 🚀 Crypto Trading Bot V4 - Production Ready

![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Status](https://img.shields.io/badge/Status-Production%20Ready-green.svg)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![Exchange](https://img.shields.io/badge/Exchange-Bybit%20V5-orange.svg)

**🎉 FINALLY WORKING VERSION!** - Enhanced Smart Money Trading Bot mit echter Bybit Mainnet Integration

---

## ✨ **Was ist neu in V4?**

- ✅ **100% funktionsfähige Bybit Mainnet Integration**
- ✅ **Enhanced Smart Money Strategy** mit Market Regime Detection
- ✅ **Echte API-Authentifizierung** (HMAC SHA256)
- ✅ **Windows PowerShell kompatibel** (Unicode-Encoding behoben)
- ✅ **Live Trading ready** für 50€ Startkapital
- ✅ **Professionelle Fehlerbehandlung**

---

## 🎯 **Quick Start**

### **1. Installation**
```bash
git clone https://github.com/develcrystal/crypto-trading-bot-v4.git
cd crypto-trading-bot-v4
pip install -r requirements.txt
```

### **2. Konfiguration**
```bash
# .env Datei erstellen
cp .env.example .env

# API Keys eintragen (siehe Setup Guide)
# BYBIT_API_KEY=your_api_key
# BYBIT_API_SECRET=your_api_secret
# TESTNET=false
```

### **3. Live Trading starten**
```bash
# API Verbindung testen
python test_live_api_connection.py

# Enhanced Live Bot starten
python enhanced_live_bot.py
```

---

## 📊 **Enhanced Smart Money Strategy**

### **🧠 Market Regime Detection**
- **BULL Market**: >2% 24h Change → Long-Positionen
- **BEAR Market**: <-2% 24h Change → Short-Positionen  
- **SIDEWAYS Market**: -2% bis +2% → Wartet auf Setup

### **💰 Risk Management**
- **Startkapital**: 50€ (konfigurierbar)
- **Risk per Trade**: 2% = ~1€ pro Position
- **Stop Loss**: 2% unter/über Entry
- **Take Profit**: 4% über/unter Entry
- **Max Drawdown**: 20%

### **⚡ Real-time Features**
- **30-Sekunden-Zyklen**: Kontinuierliche Marktanalyse
- **Live Bybit Preise**: Echte Mainnet-Daten
- **Adaptive Strategy**: Passt sich an Marktbedingungen an
- **Command Interface**: Start/Stop/Pause via JSON Commands

---

## 🏗️ **Architektur**

### **Core Files**
```
enhanced_live_bot.py          # 🚀 Haupt-Trading-Bot
test_live_api_connection.py   # 🔧 API-Verbindung testen
exchange/bybit_api.py         # 📡 Bybit V5 API Integration
core/bot_status_monitor.py    # 📊 Status & Monitoring
.env.example                  # ⚙️ Konfiguration Template
```

### **Strategy Components**
- **Market Regime Detection**: Bull/Bear/Sideways Erkennung
- **Enhanced Signal Generation**: Smart Money Patterns
- **Risk Management**: Dynamic Position Sizing
- **Order Execution**: Echte Bybit Mainnet Orders

---

## 📈 **Live Trading Example**

```
==================================================
ENHANCED SMART MONEY LIVE TRADING BOT - MAINNET
==================================================
Mode: MAINNET (Echte Trades)
Strategy: Enhanced Smart Money
Startkapital: $50.00
==================================================
2025-06-07 12:59:50 - INFO - [SUCCESS] Connected to Bybit Mainnet | BTC Price: $105,133.00
2025-06-07 12:59:50 - INFO - BTC Price: $105,133.00 | 24h Change: +1.38% | Regime: SIDEWAYS (Confidence: 0.60)
2025-06-07 12:59:51 - INFO - Signal: HOLD (No valid setup)
2025-06-07 12:59:51 - INFO - Waiting 30 seconds for next analysis...
```

---

## ⚙️ **Konfiguration**

### **Environment Variables (.env)**
```bash
# 🔑 API Configuration
BYBIT_API_KEY=your_api_key_here
BYBIT_API_SECRET=your_api_secret_here
TESTNET=false

# 💰 Trading Parameters
INITIAL_PORTFOLIO_VALUE=50
MAX_RISK_PER_TRADE=0.02
MAX_DRAWDOWN=0.15
DAILY_RISK_LIMIT=5.0

# 🧠 Strategy Parameters
RISK_REWARD_RATIO=1.5
VOLATILITY_THRESHOLD=0.02
VOLUME_THRESHOLD=100000
```

### **Key Parameters**
- **TESTNET**: false = Mainnet (echte Trades), true = Testnet
- **INITIAL_PORTFOLIO_VALUE**: Startkapital in USD
- **MAX_RISK_PER_TRADE**: 0.02 = 2% Risiko pro Trade
- **VOLUME_THRESHOLD**: Mindestvolumen für Trades

---

## 🔧 **PowerShell Commands**

### **API Test & Bot Start**
```powershell
cd path\to\crypto-trading-bot-v4; python test_live_api_connection.py; python enhanced_live_bot.py
```

### **Live Monitoring**
```powershell
cd path\to\crypto-trading-bot-v4; while($true) { Clear-Host; Write-Host "=== LIVE BOT STATUS ===" -ForegroundColor Cyan; if(Test-Path "live_trading_bot.log") { Get-Content -Path "live_trading_bot.log" -Tail 15 }; Start-Sleep 5 }
```

### **Bot Control**
```powershell
# Bot stoppen
echo '{"command": "STOP", "timestamp": '$(Get-Date -UFormat %s)'}' | Out-File -FilePath "bot_commands.json" -Encoding utf8

# Trading pausieren
echo '{"command": "PAUSE", "timestamp": '$(Get-Date -UFormat %s)'}' | Out-File -FilePath "bot_commands.json" -Encoding utf8
```

---

## 📊 **Performance Tracking**

### **Live Metrics**
- **Real-time P&L**: Kontinuierliche Gewinn/Verlust-Berechnung
- **Trade History**: Alle Trades mit Timestamps und Reasoning
- **Market Regime History**: Verlauf der Marktphasen-Erkennung
- **Status Monitoring**: Bot-Status, API-Verbindung, Fehler

### **Logging**
- **live_trading_bot.log**: Alle Trading-Aktivitäten
- **bot_status.json**: Aktueller Bot-Status
- **Trade Records**: Detaillierte Trade-Informationen

---

## 🛡️ **Sicherheit**

### **API Security**
- **HMAC SHA256**: Echte Bybit V5 API-Authentifizierung
- **Environment Variables**: Keine Hardcoded API Keys
- **Rate Limiting**: Respektiert Bybit API-Limits
- **Error Handling**: Robuste Fehlerbehandlung

### **Risk Management**
- **Position Limits**: Max 50% des Kapitals pro Trade
- **Stop Loss**: Automatische 2% Stop Loss
- **Daily Limits**: Maximales tägliches Risiko
- **Emergency Stop**: Sofortiger Bot-Stopp möglich

---

## 🚀 **Deployment Guide**

### **1. Bybit Account Setup**
1. Account auf [bybit.com](https://bybit.com) erstellen
2. API Key mit Trading-Rechten erstellen
3. IP-Restriction für zusätzliche Sicherheit (optional)

### **2. Bot Configuration**
1. `.env` Datei mit API Keys konfigurieren
2. Startkapital und Risk-Parameter anpassen
3. API-Verbindung testen: `python test_live_api_connection.py`

### **3. Live Trading**
1. Mit kleinem Kapital starten (50€ empfohlen)
2. Bot kontinuierlich überwachen
3. Performance evaluieren und Parameter anpassen

---

## 📋 **Requirements**

### **Python Dependencies**
```
requests>=2.28.0
python-dotenv>=0.19.0
psutil>=5.8.0
pyyaml>=6.0
```

### **System Requirements**
- **Python**: 3.8+
- **OS**: Windows 10/11, macOS, Linux
- **Internet**: Stabile Verbindung für API-Calls
- **Memory**: Min 256MB RAM

---

## 🤝 **Contributing**

1. Fork das Repository
2. Erstelle einen Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit deine Änderungen (`git commit -m 'Add some AmazingFeature'`)
4. Push zum Branch (`git push origin feature/AmazingFeature`)
5. Erstelle einen Pull Request

---

## 📞 **Support**

- **Issues**: [GitHub Issues](https://github.com/develcrystal/crypto-trading-bot-v4/issues)
- **Discussions**: [GitHub Discussions](https://github.com/develcrystal/crypto-trading-bot-v4/discussions)
- **Documentation**: Siehe `docs/` Verzeichnis

---

## ⚖️ **Disclaimer**

⚠️ **WICHTIGER HINWEIS**: Diese Software dient nur zu Bildungszwecken. Der Handel mit Kryptowährungen ist hochriskant und kann zum Totalverlust führen.

- ✅ Testen Sie immer zuerst auf Testnet
- ✅ Investieren Sie nur, was Sie sich leisten können zu verlieren
- ✅ Diese Software bietet keine Anlageberatung
- ✅ Die Autoren übernehmen keine Haftung für Verluste

---

## 📄 **Lizenz**

MIT License - Siehe [LICENSE](LICENSE) für Details.

**© 2025 Crypto Trading Bot V4** - Production Ready Trading Solution

---

## 🎯 **Was macht V4 besonders?**

- **🔥 Endlich funktionsfähig**: Keine Dummy-Implementierungen mehr
- **💰 Echtes Mainnet Trading**: Wirkliche Bybit-Integration
- **🧠 Smart Strategy**: Market Regime Detection
- **🛡️ Professionelle Security**: HMAC-Authentifizierung
- **📊 Live Monitoring**: Real-time Status und Performance
- **🚀 Production Ready**: Bereit für echtes Trading

**Ready to trade? Let's make money! 📈**
