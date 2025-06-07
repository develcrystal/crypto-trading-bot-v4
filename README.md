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

## 🔧 **Platform Commands**

### **🪟 Windows (PowerShell)**

#### **API Test & Bot Start**
```powershell
cd path\to\crypto-trading-bot-v4; python test_live_api_connection.py; python enhanced_live_bot.py
```

#### **Live Monitoring**
```powershell
cd path\to\crypto-trading-bot-v4; while($true) { Clear-Host; Write-Host "=== LIVE BOT STATUS ===" -ForegroundColor Cyan; if(Test-Path "live_trading_bot.log") { Get-Content -Path "live_trading_bot.log" -Tail 15 }; Start-Sleep 5 }
```

#### **Bot Control**
```powershell
# Bot stoppen
echo '{"command": "STOP", "timestamp": '$(Get-Date -UFormat %s)'}' | Out-File -FilePath "bot_commands.json" -Encoding utf8

# Trading pausieren
echo '{"command": "PAUSE", "timestamp": '$(Get-Date -UFormat %s)'}' | Out-File -FilePath "bot_commands.json" -Encoding utf8
```

### **🐧 Linux (Bash)**

#### **Installation & Setup**
```bash
# Repository klonen
git clone https://github.com/develcrystal/crypto-trading-bot-v4.git
cd crypto-trading-bot-v4

# Python Virtual Environment erstellen
python3 -m venv crypto-bot-env
source crypto-bot-env/bin/activate

# Dependencies installieren
pip install -r requirements.txt

# Konfiguration
cp .env.example .env
nano .env  # API Keys eintragen
```

#### **API Test & Bot Start**
```bash
cd /path/to/crypto-trading-bot-v4 && python test_live_api_connection.py && python enhanced_live_bot.py
```

#### **Live Monitoring**
```bash
# Live Log Monitoring
cd /path/to/crypto-trading-bot-v4
while true; do 
    clear
    echo "=== LIVE BOT STATUS ==="
    if [ -f "live_trading_bot.log" ]; then
        tail -15 live_trading_bot.log
    fi
    sleep 5
done
```

#### **Bot Control**
```bash
# Bot stoppen
cd /path/to/crypto-trading-bot-v4
echo '{"command": "STOP", "timestamp": '$(date +%s)'}' > bot_commands.json

# Trading pausieren
echo '{"command": "PAUSE", "timestamp": '$(date +%s)'}' > bot_commands.json

# Bot als Service (systemd)
sudo nano /etc/systemd/system/crypto-bot.service
sudo systemctl enable crypto-bot
sudo systemctl start crypto-bot
```

#### **Screen Session (Detached Running)**
```bash
# Bot in Screen Session starten
screen -S crypto-bot
cd /path/to/crypto-trading-bot-v4
source crypto-bot-env/bin/activate
python enhanced_live_bot.py

# Session detachen: Ctrl+A, dann D
# Session wieder verbinden: screen -r crypto-bot
```

### **🍎 macOS (Terminal)**

#### **Installation & Setup**
```bash
# Homebrew installieren (falls nicht vorhanden)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Python 3 installieren
brew install python3

# Repository klonen
git clone https://github.com/develcrystal/crypto-trading-bot-v4.git
cd crypto-trading-bot-v4

# Virtual Environment erstellen
python3 -m venv crypto-bot-env
source crypto-bot-env/bin/activate

# Dependencies installieren
pip install -r requirements.txt

# Konfiguration
cp .env.example .env
nano .env  # oder: code .env (VS Code)
```

#### **API Test & Bot Start**
```bash
cd /path/to/crypto-trading-bot-v4 && python test_live_api_connection.py && python enhanced_live_bot.py
```

#### **Live Monitoring**
```bash
# Live Log Monitoring
cd /path/to/crypto-trading-bot-v4
while true; do 
    clear
    echo "=== LIVE BOT STATUS ==="
    if [ -f "live_trading_bot.log" ]; then
        tail -15 live_trading_bot.log
    fi
    sleep 5
done
```

#### **Bot Control**
```bash
# Bot stoppen
cd /path/to/crypto-trading-bot-v4
echo '{"command": "STOP", "timestamp": '$(date +%s)'}' > bot_commands.json

# Trading pausieren
echo '{"command": "PAUSE", "timestamp": '$(date +%s)'}' > bot_commands.json

# Bot als LaunchAgent (automatischer Start)
mkdir -p ~/Library/LaunchAgents
cat > ~/Library/LaunchAgents/com.crypto-bot.plist << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.crypto-bot</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/crypto-trading-bot-v4/crypto-bot-env/bin/python</string>
        <string>/path/to/crypto-trading-bot-v4/enhanced_live_bot.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/path/to/crypto-trading-bot-v4</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
EOF

# Service laden und starten
launchctl load ~/Library/LaunchAgents/com.crypto-bot.plist
launchctl start com.crypto-bot
```

### **🐳 Docker (Alle Plattformen)**

#### **Dockerfile erstellen**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Health Check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

CMD ["python", "enhanced_live_bot.py"]
```

#### **Docker Commands**
```bash
# Image bauen
docker build -t crypto-trading-bot-v4 .

# Container starten
docker run -d \
  --name crypto-bot \
  --restart unless-stopped \
  -v $(pwd)/.env:/app/.env:ro \
  -v $(pwd)/logs:/app/logs \
  crypto-trading-bot-v4

# Logs anzeigen
docker logs -f crypto-bot

# Container stoppen
docker stop crypto-bot
```

#### **Docker Compose**
```yaml
# docker-compose.yml
version: '3.8'
services:
  crypto-bot:
    build: .
    container_name: crypto-trading-bot
    restart: unless-stopped
    volumes:
      - ./.env:/app/.env:ro
      - ./logs:/app/logs
    environment:
      - PYTHONUNBUFFERED=1
    healthcheck:
      test: ["CMD", "python", "-c", "import sys; sys.exit(0)"]
      interval: 30s
      timeout: 10s
      retries: 3
```

```bash
# Docker Compose starten
docker-compose up -d

# Logs verfolgen
docker-compose logs -f
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

## 📋 **System Requirements**

### **🪟 Windows**
```powershell
# Python 3.8+ installieren
# Download: https://www.python.org/downloads/windows/
python --version  # Sollte 3.8+ anzeigen

# Git installieren (optional)
# Download: https://git-scm.com/download/win

# PowerShell 5.1+ (meist schon installiert)
$PSVersionTable.PSVersion
```

### **🐧 Linux (Ubuntu/Debian)**
```bash
# System aktualisieren
sudo apt update && sudo apt upgrade -y

# Python 3.8+ installieren
sudo apt install python3 python3-pip python3-venv git -y

# Version prüfen
python3 --version  # Sollte 3.8+ anzeigen
```

### **🐧 Linux (CentOS/RHEL/Fedora)**
```bash
# System aktualisieren
sudo dnf update -y  # oder: sudo yum update -y

# Python 3.8+ installieren
sudo dnf install python3 python3-pip git -y

# Version prüfen
python3 --version  # Sollte 3.8+ anzeigen
```

### **🍎 macOS**
```bash
# Homebrew installieren
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Python 3.8+ installieren
brew install python3 git

# Version prüfen
python3 --version  # Sollte 3.8+ anzeigen
```

### **🐳 Docker Requirements**
```bash
# Docker installieren
# Windows: Docker Desktop
# Linux: docker.io package
# macOS: Docker Desktop

# Version prüfen
docker --version
docker-compose --version
```

### **📦 Python Dependencies**
```
requests>=2.28.0
python-dotenv>=0.19.0
psutil>=5.8.0
pyyaml>=6.0
```

### **💾 Hardware Requirements**
- **CPU**: 1 Core (empfohlen: 2+ Cores)
- **RAM**: 512MB (empfohlen: 1GB+)
- **Storage**: 100MB (empfohlen: 1GB für Logs)
- **Internet**: Stabile Verbindung (min 1 Mbps)

### **🌐 Network Requirements**
- **Bybit API**: api.bybit.com (Port 443)
- **Outbound HTTPS**: Port 443 geöffnet
- **No Proxy**: Oder Proxy konfiguriert
- **Latenz**: <100ms für optimale Performance

---

## 🤝 **Contributing**

1. Fork das Repository
2. Erstelle einen Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit deine Änderungen (`git commit -m 'Add some AmazingFeature'`)
4. Push zum Branch (`git push origin feature/AmazingFeature`)
5. Erstelle einen Pull Request

---

## 🔧 **Troubleshooting**

### **🚨 Häufige Probleme & Lösungen**

#### **API Connection Failed**
```bash
# Problem: "Failed to connect to Bybit API"
# Lösung 1: Internet-Verbindung prüfen
ping api.bybit.com

# Lösung 2: API Keys prüfen
python test_live_api_connection.py

# Lösung 3: Firewall/Proxy prüfen
curl -I https://api.bybit.com/v5/market/tickers
```

#### **Python ModuleNotFoundError**
```bash
# Problem: "ModuleNotFoundError: No module named 'requests'"
# Lösung: Dependencies installieren
pip install -r requirements.txt

# Oder einzeln installieren
pip install requests python-dotenv psutil pyyaml
```

#### **Permission Denied**
```bash
# Linux/macOS: Python executable permission
chmod +x enhanced_live_bot.py

# Windows: Als Administrator ausführen
# Rechtsklick -> "Als Administrator ausführen"
```

#### **Unicode/Encoding Errors**
```bash
# Windows PowerShell Encoding
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Linux/macOS Locale
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
```

#### **Bot stoppt unerwartet**
```bash
# Logs prüfen
tail -100 live_trading_bot.log

# Speicher prüfen
free -h  # Linux
vm_stat  # macOS
Get-ComputerInfo | Select-Object TotalPhysicalMemory  # Windows

# Prozess prüfen
ps aux | grep python  # Linux/macOS
Get-Process python    # Windows
```

### **📊 Performance Monitoring**

#### **Bot Health Check**
```bash
# Status prüfen
cat bot_status.json

# Live Performance
watch -n 5 "cat bot_status.json | python -m json.tool"

# Memory Usage
ps -o pid,vsz,rss,comm -p $(pgrep -f enhanced_live_bot.py)
```

#### **Log Analysis**
```bash
# Fehler in Logs finden
grep -i "error\|exception\|failed" live_trading_bot.log

# Trading Performance
grep "TRADE\|SIGNAL\|PROFIT" live_trading_bot.log

# API Calls zählen
grep -c "API" live_trading_bot.log
```

### **🐛 Debug Mode**

#### **Verbose Logging aktivieren**
```bash
# .env Datei erweitern
echo "DEBUG=true" >> .env
echo "LOG_LEVEL=DEBUG" >> .env

# Bot mit Debug-Info starten
python -u enhanced_live_bot.py 2>&1 | tee debug.log
```

#### **Python Debug**
```python
# Debug-Modus in Python Code
import logging
logging.basicConfig(level=logging.DEBUG)

# Oder mit pdb debuggen
import pdb; pdb.set_trace()
```

### **📞 Support & Community**

#### **Bevor du Support anfragst:**
1. ✅ Logs geprüft (`live_trading_bot.log`)
2. ✅ API Connection getestet (`python test_live_api_connection.py`)
3. ✅ Dependencies installiert (`pip install -r requirements.txt`)
4. ✅ .env Datei konfiguriert
5. ✅ System Requirements erfüllt

#### **Support Kanäle:**
- **GitHub Issues**: [Technische Probleme](https://github.com/develcrystal/crypto-trading-bot-v4/issues)
- **GitHub Discussions**: [Allgemeine Fragen](https://github.com/develcrystal/crypto-trading-bot-v4/discussions)
- **Documentation**: README.md & SETUP_GUIDE.md

#### **Bug Report Template:**
```
**System Info:**
- OS: [Windows 10/Ubuntu 20.04/macOS 12]
- Python Version: [3.9.7]
- Bot Version: [V4.0]

**Problem:**
- Was ist passiert?
- Wann ist es passiert?
- Erwartetes Verhalten?

**Logs:**
```
[Log-Ausgabe hier einfügen]
```

**Steps to Reproduce:**
1. Schritt 1
2. Schritt 2
3. ...
```

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
