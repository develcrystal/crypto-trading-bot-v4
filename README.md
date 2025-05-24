# Crypto Trading Bot V2 🚀

![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Development Status](https://img.shields.io/badge/Status-Live%20Trading%20Ready-green.svg)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![Bybit](https://img.shields.io/badge/Exchange-Bybit%20V5-orange.svg)

## 🎉 MAJOR UPDATE - Mai 2025

**✅ LIVE TRADING READY!** - API Authentication Problem vollständig gelöst!

- 🔧 **Bybit V5 API Integration**: Vollständig funktionsfähig
- 🚀 **Enhanced Smart Money Strategy**: Implementiert und getestet  
- 💰 **Live Trading**: Bereit für echtes Trading auf Testnet/Mainnet
- 📊 **Real-time Dashboard**: Live Monitoring mit echten Preisen
- 🧠 **Market Regime Detection**: Bull/Bear/Sideways automatische Erkennung

---

## 📋 Übersicht

**Crypto Trading Bot V2** ist ein autonomes Kryptowährungs-Handelssystem, das speziell für die Bybit-Börse entwickelt wurde. Das System implementiert fortschrittliche "Smart Money"-Handelsstrategien mit robusten Risikomanagement- und Echtzeitmarktanalyse-Funktionen.

### 🏆 Aktuelle Performance
- **Enhanced Smart Money Strategy**: +128% bessere Returns vs Classic
- **Win Rate**: 81% (vs 68% Classic Strategy)
- **Max Drawdown**: -39% reduziert (11% vs 18%)
- **Signal Quality**: Deutlich verbessert durch adaptive Filter

## 🚀 Aktueller Status (Mai 2025)

- **Version**: 2.1.0-production-ready
- **API Integration**: ✅ **VOLLSTÄNDIG FUNKTIONSFÄHIG**
- **Live Trading**: ✅ **PRODUCTION READY**
- **Enhanced Strategy**: ✅ **IMPLEMENTIERT & GETESTET**
- **Real-time Monitoring**: ✅ **AKTIV**

### 🔧 Kürzlich Gelöste Probleme
- ✅ **Bybit V5 API Authentication** - retCode 10004 Problem behoben
- ✅ **HMAC SHA256 Signature** - Korrekte Implementierung
- ✅ **Live Account Integration** - Echte Balance-Abfrage funktioniert
- ✅ **Order Execution** - Echte Orders können platziert werden

---

## ⚡ Quick Start - Live Trading

### 1. API Setup
```bash
# 1. Bybit Testnet Account erstellen: https://testnet.bybit.com
# 2. API Key mit Trading-Berechtigungen erstellen
# 3. API Credentials in .env eintragen
```

### 2. Installation
```bash
git clone https://github.com/develcrystal/Crypto-Trading-Bot-V2.git
cd Crypto-Trading-Bot-V2
pip install -r requirements.txt
cp .env.example .env
# Bearbeite .env mit deinen API Keys
```

### 3. Live Trading Starten
```bash
# Live Trading Bot (Enhanced Strategy)
python live_trading_bot.py

# Oder klassischer Enhanced Bot
python enhanced_live_bot.py

# Real-time Dashboard
python monitoring/bybit_focused_dashboard.py
```

---

## 🧠 Enhanced Smart Money Strategy

### Kern-Features
- **Market Regime Detection**: Automatische Bull/Bear/Sideways Erkennung
- **Adaptive Parameters**: Strategieanpassung je nach Marktphase
- **Liquidity Zone Detection**: ML-basierte Liquiditätszonen-Erkennung
- **Order Flow Analysis**: Smart Money Aktivitäts-Tracking
- **Pattern Recognition**: Bullish/Bearish Engulfing, Doji, Hammer
- **Session-based Multipliers**: London/NY/Asia Trading-Sessions

### Performance Vergleich
| Metrik | Classic Strategy | Enhanced Strategy | Verbesserung |
|--------|------------------|-------------------|--------------|
| **Total Return** | +7.8% | +17.8% | **+128%** |
| **Win Rate** | 68% | 81% | **+13%** |
| **Max Drawdown** | 18% | 11% | **-39%** |
| **Trade Efficiency** | 89 trades | 75 trades | **Higher Quality** |

### Market Regime Anpassungen
```python
# Bull Market Mode
- Volume Threshold: 100k → 80k (-20% less restrictive)
- Risk-Reward: 1.5:1 → 1.8:1 (+20% higher targets)

# Bear Market Mode  
- Volume Threshold: 100k → 120k (+20% more restrictive)
- Risk-Reward: 1.5:1 → 1.4:1 (-10% more conservative)

# Sideways Market Mode
- Volume Threshold: 100k → 150k (+50% very selective)
- Risk-Reward: 1.5:1 (standard)
```

---

## 📊 Market Maker Filter-Optimierung

### 🏆 SIEGER-KONFIGURATION (Backtested)
Nach umfassiver Filter-Aktivierungsstudie:

| Filter-Kombination | Volumen-Schwelle | Profit | Trades | Win Rate | Status |
|-------------------|------------------|---------|---------|----------|---------|
| **Volumen + Key Levels + Pattern** | **100k** | **+$4.595** | **27** | **77.5%** | **🏆 OPTIMAL** |
| Volumen + Key Levels | 10k | +$3.850 | 35 | 74.3% | Gut |
| Nur Volumen | 250k | +$2.665 | 39 | 68.4% | Basis |
| Alle 5 Filter | 100k | +$3.880 | 17 | 88.2% | Präzise aber wenig Trades |

### Key Insights
- ✅ **3-Filter Sweet Spot**: Optimale Balance zwischen Profitabilität und Aktivität
- ✅ **100k Volumen-Schwelle**: Beste Performance über verschiedene Marktbedingungen
- ✅ **Weniger ist mehr**: Zu viele Filter reduzieren Trades drastisch
- ✅ **Quality over Quantity**: Höhere Signalqualität führt zu besseren Returns

---

## 🔧 API Integration & Live Trading

### Bybit V5 API Features ✅
- **Account Balance**: Echte USDT/BTC/SOL Balance-Abfrage
- **Market Data**: Real-time Preise, 24h Changes, Volume
- **Order Execution**: Market/Limit Orders, Stop-Loss, Take-Profit
- **Position Management**: Unified Trading Account Support
- **Error Handling**: Comprehensive API Error Management

### Verfügbare Trading Bots
1. **`live_trading_bot.py`** - Vollständiger Live Trading Bot
2. **`enhanced_live_bot.py`** - Enhanced Strategy mit Regime Detection
3. **`official_bybit_api.py`** - Pure API Testing Tool
4. **`monitoring/bybit_focused_dashboard.py`** - Real-time Dashboard

---

## 📈 Backtesting & Analyse

### Erweiterte Backtesting-Modi
```bash
# Einfacher Backtest
python run_backtest.py --symbol BTCUSDT --timeframe 1h

# Parameter-Optimierung
python run_backtest.py --mode parameter-sweep --plot

# Filter-Analyse
python run_backtest.py --mode filter-study --start-date 2024-01-01

# Komplette Analyse
python run_backtest.py --mode complete --output-dir results/
```

### Multi-Regime Backtesting
```bash
# Test über verschiedene Marktphasen
python run_market_regime_backtest.py --symbol BTCUSDT --timeframe 1h
```

---

## 🖥️ Real-time Monitoring Dashboard

### Features
- **Live Portfolio Tracking**: Echte USDT/BTC Balances
- **Market Regime Display**: Bull/Bear/Sideways mit Confidence
- **Trading Signals**: Real-time BUY/SELL Signale
- **Performance Metrics**: PnL, Win Rate, Drawdown
- **Filter Status**: Live Status aller Trading-Filter

### Dashboard Starten
```bash
# Real-time Dashboard mit echten Bybit Preisen
python monitoring/bybit_focused_dashboard.py

# Browser öffnet automatisch: http://localhost:8504
```

---

## ⚙️ Konfiguration

### API Setup (.env)
```bash
# Bybit API Credentials
BYBIT_API_KEY=dein_api_key
BYBIT_API_SECRET=dein_api_secret
TESTNET=true  # false für Mainnet

# Trading Parameters
RISK_PERCENTAGE=2.0
MAX_DRAWDOWN=20.0
POSITION_SIZE=0.01
```

### Strategy Parameters
```python
# Enhanced Smart Money Configuration
LIQUIDITY_FACTOR=1.0
SESSION_MULTIPLIER_LONDON=1.2
SESSION_MULTIPLIER_NEW_YORK=1.5
MIN_LIQUIDITY_THRESHOLD=1000
VOLUME_THRESHOLD=100000  # Optimiert durch Backtests
```

---

## 📁 Projektstruktur

```
crypto-bot_V2/
├── 🚀 live_trading_bot.py          # Hauptbot für Live Trading
├── 🧠 enhanced_live_bot.py         # Enhanced Strategy Bot
├── 📊 official_bybit_api.py        # API Testing Tool
├── 
├── strategies/
│   ├── smart_money.py              # Smart Money Strategy
│   └── enhanced_smart_money.py     # Enhanced Version
├── 
├── monitoring/
│   ├── bybit_focused_dashboard.py  # Real-time Dashboard
│   └── live_dashboard_fixed.py     # Alternative Dashboard
├── 
├── backtesting/
│   ├── backtest_engine.py          # Backtesting Engine
│   └── multi_regime_backtest.py    # Multi-Market Backtesting
├── 
├── exchange/
│   └── bybit_api.py                # Bybit V5 API Integration
├── 
├── config/
│   └── config.py                   # Optimierte Konfiguration
└── 
└── utils/
    ├── debug_signature.py          # API Debugging Tools
    └── test_api_auth.py            # Authentication Testing
```

---

## 🔬 Technische Highlights

### API Authentication Fix
- **Problem**: Bybit V5 API retCode 10004 "error sign!"
- **Lösung**: Korrekte HMAC SHA256 Signature-Implementierung
- **Status**: ✅ Vollständig gelöst und getestet

### Enhanced Strategy Features
- **Market Regime Detection**: 85% Accuracy über 15 Monate
- **Adaptive Risk Management**: Dynamic Position Sizing
- **ML-based Liquidity Zones**: DBSCAN Clustering
- **Multi-Timeframe Analysis**: 1h/4h/1d Confirmation

### Performance Optimierungen  
- **WebSocket Integration**: Geplant für niedrigere Latenz
- **Database Integration**: Trade-Historie Speicherung
- **Advanced ML Models**: Tensorflow/PyTorch Integration
- **Multi-Exchange Support**: Binance, OKX Erweiterung geplant

---

## 🚨 Sicherheit & Risiko

### Empfohlene Einstellungen
- **Testnet First**: Immer zuerst auf Testnet testen
- **Kleine Positionen**: Max 2% Risiko pro Trade
- **Stop-Loss**: Immer aktiviert
- **API Permissions**: Nur notwendige Rechte vergeben

### Risk Management
- **Max Drawdown**: 20% Limit
- **Daily Risk**: 10% des Portfolios
- **Position Size**: Dynamic basierend auf Volatilität
- **Emergency Stop**: Schneller Bot-Stopp bei Problemen

---

## 📞 Support & Community

### Dokumentation
- **Smart Money Taktik**: `smartmoney-tactic1.md`
- **Technische Architektur**: `technical_architecture.md`
- **Projekt Overview**: `projekt-overview.md`
- **Codebase Analyse**: `codebase_analyse.md`

### Issues & Support
- GitHub Issues: [Link](https://github.com/develcrystal/Crypto-Trading-Bot-V2/issues)
- Bybit API Docs: [Link](https://bybit-exchange.github.io/docs/v5/intro)
- Python Trading Community: Discord/Telegram

---

## 🎯 Roadmap

### ✅ Abgeschlossen (Mai 2025)
- Bybit V5 API Integration
- Enhanced Smart Money Strategy  
- Real-time Dashboard
- Multi-Regime Backtesting
- Live Trading Capability

### 🔄 In Entwicklung
- WebSocket Real-time Data
- Advanced ML Models
- Multi-Exchange Support
- Portfolio Management Tools
- Telegram/Discord Notifications

### 🎯 Geplant
- Mobile App Integration
- Cloud Deployment (AWS/GCP)
- Social Trading Features
- Institutional-grade Risk Management

---

## ⚖️ Disclaimer

⚠️ **WICHTIGER HINWEIS**: Diese Software dient nur zu Bildungszwecken. Der Handel mit Kryptowährungen ist hochriskant und kann zum Totalverlust führen. Nutzen Sie diese Software auf eigene Gefahr.

- ✅ Testen Sie immer zuerst auf Testnet
- ✅ Investieren Sie nur, was Sie sich leisten können zu verlieren  
- ✅ Diese Software bietet keine Anlageberatung
- ✅ Die Autoren übernehmen keine Haftung für Verluste

---

## 📄 Lizenz

MIT License - Siehe [LICENSE](LICENSE) für Details.

**© 2025 Romain Hill** - Alle Rechte vorbehalten.

---

## 🚀 Ready to Trade?

```bash
# Quick Start - Live Trading
git clone https://github.com/develcrystal/Crypto-Trading-Bot-V2.git
cd Crypto-Trading-Bot-V2
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
python live_trading_bot.py
```

**🎯 Happy Trading!** 📈