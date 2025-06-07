# 🚀 Cross-Platform Setup Guide

**Schnelle Plattform-spezifische Installationsanleitungen**

---

## 🪟 **Windows Setup (5 Minuten)**

### **1. Python installieren**
- Download: https://www.python.org/downloads/windows/
- **WICHTIG**: "Add Python to PATH" aktivieren ✅

### **2. Repository klonen & Setup**
```powershell
# Git installieren (falls nicht vorhanden)
# Download: https://git-scm.com/download/win

# Repository klonen
git clone https://github.com/develcrystal/crypto-trading-bot-v4.git
cd crypto-trading-bot-v4

# Dependencies installieren
pip install -r requirements.txt

# Konfiguration
copy .env.example .env
notepad .env  # API Keys eintragen
```

### **3. Bot starten**
```powershell
# API testen
python test_live_api_connection.py

# Bot starten
python enhanced_live_bot.py
```

---

## 🐧 **Linux Setup (Ubuntu/Debian)**

### **1. System vorbereiten**
```bash
# System aktualisieren
sudo apt update && sudo apt upgrade -y

# Python & Git installieren
sudo apt install python3 python3-pip python3-venv git -y
```

### **2. Repository & Virtual Environment**
```bash
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
nano .env  # API Keys eintragen
```

### **3. Bot starten**
```bash
# API testen
python test_live_api_connection.py

# Bot starten
python enhanced_live_bot.py

# Als Service (optional)
sudo systemctl enable crypto-bot
sudo systemctl start crypto-bot
```

---

## 🍎 **macOS Setup (Terminal)**

### **1. Homebrew & Python installieren**
```bash
# Homebrew installieren
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Python & Git installieren
brew install python3 git
```

### **2. Repository & Virtual Environment**
```bash
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

### **3. Bot starten**
```bash
# API testen
python test_live_api_connection.py

# Bot starten
python enhanced_live_bot.py

# Als LaunchAgent (optional)
launchctl load ~/Library/LaunchAgents/com.crypto-bot.plist
```

---

## 🐳 **Docker Setup (Alle Plattformen)**

### **1. Docker installieren**
- **Windows**: Docker Desktop
- **Linux**: `sudo apt install docker.io docker-compose`
- **macOS**: Docker Desktop

### **2. Repository & Container**
```bash
# Repository klonen
git clone https://github.com/develcrystal/crypto-trading-bot-v4.git
cd crypto-trading-bot-v4

# .env Datei erstellen
cp .env.example .env
# API Keys in .env eintragen

# Docker Container bauen & starten
docker build -t crypto-trading-bot-v4 .
docker run -d --name crypto-bot \
  --restart unless-stopped \
  -v $(pwd)/.env:/app/.env:ro \
  -v $(pwd)/logs:/app/logs \
  crypto-trading-bot-v4

# Logs verfolgen
docker logs -f crypto-bot
```

### **3. Docker Compose (Empfohlen)**
```bash
# Mit docker-compose.yml (bereits im Repository)
docker-compose up -d

# Logs anzeigen
docker-compose logs -f
```

---

## ⚙️ **API Configuration (.env)**

**Für ALLE Plattformen gleich:**
```bash
# 🔑 Bybit API (Mainnet)
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

---

## 🎯 **Quick Start Commands**

### **API Connection Test**
```bash
# Windows
python test_live_api_connection.py

# Linux/macOS
python3 test_live_api_connection.py

# Docker
docker exec crypto-bot python test_live_api_connection.py
```

### **Bot Start**
```bash
# Windows
python enhanced_live_bot.py

# Linux/macOS
python3 enhanced_live_bot.py

# Docker
docker start crypto-bot
```

### **Live Monitoring**
```bash
# Windows (PowerShell)
Get-Content -Path "live_trading_bot.log" -Wait -Tail 10

# Linux/macOS
tail -f live_trading_bot.log

# Docker
docker logs -f crypto-bot
```

---

## 🚨 **Troubleshooting**

### **Python nicht gefunden**
```bash
# Windows: Python zu PATH hinzufügen
# Linux: sudo apt install python3
# macOS: brew install python3
```

### **Permission Denied**
```bash
# Linux/macOS
chmod +x enhanced_live_bot.py
sudo chown -R $USER:$USER crypto-trading-bot-v4/

# Windows: Als Administrator ausführen
```

### **ModuleNotFoundError**
```bash
# Virtual Environment aktivieren
source crypto-bot-env/bin/activate  # Linux/macOS
crypto-bot-env\Scripts\activate     # Windows

# Dependencies neu installieren
pip install --upgrade -r requirements.txt
```

---

## 📞 **Platform-Specific Support**

### **Windows**
- PowerShell 5.1+ required
- Windows Defender Firewall configuration
- Anti-virus whitelist if needed

### **Linux**
- systemd service files available
- UFW firewall configuration
- Cron job setup for monitoring

### **macOS** 
- Xcode command line tools: `xcode-select --install`
- LaunchAgent for automatic startup
- Homebrew package management

### **Docker**
- Multi-platform images (AMD64/ARM64)
- Health checks included
- Persistent volume for logs

---

## 🎯 **Ready to Trade!**

**Nach der Installation sofort startbereit:**
1. ✅ API Keys in `.env` eintragen
2. ✅ `python test_live_api_connection.py` ausführen
3. ✅ `python enhanced_live_bot.py` starten
4. ✅ Live Trading überwachen

**Happy Trading auf allen Plattformen! 🚀📈**
