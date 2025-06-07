# 🚀 Crypto Trading Bot V4 - Setup Guide

## 📋 **Schritt-für-Schritt Installation**

### **1. Repository klonen**
```bash
git clone https://github.com/yourusername/crypto-trading-bot-v4.git
cd crypto-trading-bot-v4
```

### **2. Python Environment**
```bash
# Python 3.8+ erforderlich
python --version

# Virtual Environment (optional aber empfohlen)
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Dependencies installieren
pip install -r requirements.txt
```

### **3. Bybit Account Setup**

#### **API Key erstellen:**
1. Gehe zu [bybit.com](https://bybit.com)
2. Login → User Center → API Management
3. Create New Key
4. **Permissions aktivieren:**
   - ✅ Read-Write
   - ✅ Spot Trading
   - ✅ Contract Trading (optional)
5. **Wichtig**: IP Restriction für zusätzliche Sicherheit

#### **Testnet vs Mainnet:**
- **Testnet**: Zum Testen ohne echtes Geld
- **Mainnet**: Für echtes Trading (nur mit kleinen Beträgen!)

### **4. Bot Konfiguration**

#### **.env Datei erstellen:**
```bash
cp .env.example .env
```

#### **.env bearbeiten:**
```bash
# 🔑 DEINE API CREDENTIALS
BYBIT_API_KEY=dein_echter_api_key
BYBIT_API_SECRET=dein_echter_api_secret
TESTNET=false  # true für Testnet, false für Mainnet

# 💰 TRADING SETUP (50€ Beispiel)
INITIAL_PORTFOLIO_VALUE=50
MAX_RISK_PER_TRADE=0.02  # 2% = 1€ per Trade
DAILY_RISK_LIMIT=5.0     # Max 5€ Verlust per Tag
```

### **5. API Verbindung testen**
```bash
python test_live_api_connection.py
```

**Erwartete Ausgabe:**
```
==================================================
BYBIT MAINNET API CONNECTION TEST
==================================================
API Key: dein_key...
Testnet Mode: False
[SUCCESS] Mainnet API Connection Working!
BTC Price: $105,133.00
24h Volume: 6,575.35 BTC
24h Change: +1.38%

[READY] READY FOR LIVE TRADING!
```

### **6. Live Trading starten**
```bash
python enhanced_live_bot.py
```

## ⚠️ **Wichtige Sicherheitshinweise**

### **🔒 API Key Security:**
- **Niemals** API Keys in Code committen
- **Immer** .env verwenden für Credentials
- **IP Restriction** aktivieren wenn möglich
- **Regelmäßig** API Keys rotieren

### **💰 Risk Management:**
- **Starte klein**: Max 50-100€ für erste Tests
- **2% Rule**: Nie mehr als 2% per Trade riskieren
- **Stop Loss**: Immer aktiviert (automatisch)
- **Monitor**: Bot kontinuierlich überwachen

### **🧪 Testing Workflow:**
1. **Testnet**: Erst ausgiebig auf Testnet testen
2. **Small Amount**: Mit 50€ auf Mainnet starten
3. **Monitor**: Erste 24h eng überwachen
4. **Scale**: Nur bei bewiesener Profitabilität erhöhen

## 🔧 **Erweiterte Konfiguration**

### **Trading Parameters anpassen:**
```bash
# In .env Datei:
RISK_REWARD_RATIO=1.5        # 1:1.5 Risk-Reward
VOLUME_THRESHOLD=100000      # Min BTC Volumen für Trades
VOLATILITY_THRESHOLD=0.02    # Min Volatilität für Signale
```

### **Strategy Parameters:**
```bash
# Market Regime Detection:
SESSION_MULTIPLIER_LONDON=1.2    # London Session Boost
SESSION_MULTIPLIER_NEW_YORK=1.5  # NY Session Boost
MIN_LIQUIDITY_THRESHOLD=1000     # Min Liquidität für Trades
```

## 📊 **Monitoring & Control**

### **Live Status überwachen:**
```powershell
# Windows PowerShell:
while($true) { 
    Clear-Host
    Write-Host "=== LIVE BOT STATUS ===" -ForegroundColor Cyan
    Get-Content -Path "live_trading_bot.log" -Tail 15
    Start-Sleep 5 
}
```

### **Bot Control Commands:**
```powershell
# Bot stoppen:
echo '{"command": "STOP"}' | Out-File -FilePath "bot_commands.json"

# Trading pausieren:
echo '{"command": "PAUSE"}' | Out-File -FilePath "bot_commands.json"

# Trading fortsetzen:
echo '{"command": "RESUME"}' | Out-File -FilePath "bot_commands.json"
```

## 🚨 **Troubleshooting**

### **Häufige Probleme:**

#### **API Connection Failed:**
```
✓ API Keys korrekt in .env?
✓ Internet-Verbindung stabil?
✓ Bybit Service erreichbar?
✓ IP Restriction richtig konfiguriert?
```

#### **ModuleNotFoundError:**
```bash
# Dependencies neu installieren:
pip install -r requirements.txt

# Oder spezifisches Modul:
pip install pyyaml
```

#### **Unicode Errors (Windows):**
```bash
# PowerShell Encoding fix:
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
```

#### **Permission Errors:**
```
✓ API Key hat Trading-Rechte?
✓ Account hat genügend Balance?
✓ Bybit Maintenance Mode?
```

### **Debug Mode:**
```bash
# Mehr Details im Log:
LOG_LEVEL=DEBUG
python enhanced_live_bot.py
```

## 📈 **Performance Optimization**

### **Parameter Tuning:**
1. **Volume Threshold**: Bei wenigen Signalen reduzieren
2. **Risk-Reward**: Bei vielen Verlusten erhöhen  
3. **Volatility Threshold**: Bei volatilen Märkten anpassen

### **Strategy Optimization:**
- **Backtest** neue Parameter erst
- **A/B Test** verschiedene Settings
- **Monitor** Performance Metrics genau

## ✅ **Checkliste vor Live Trading**

- [ ] API Keys erstellt und getestet
- [ ] .env Datei konfiguriert  
- [ ] API Verbindung erfolgreich
- [ ] Risk Parameters verstanden
- [ ] Monitoring Setup bereit
- [ ] Stop-Loss Mechanismen verstanden
- [ ] Emergency Procedures bekannt
- [ ] Mit kleinem Betrag (50€) starten

## 🎯 **Success Metrics**

### **Was zu erwarten ist:**
- **Setup Zeit**: 30-60 Minuten
- **Erste Signale**: Innerhalb 1-2 Stunden
- **Break-Even**: Nach 1-2 Wochen (bei 50€)
- **Profitable**: Nach 1-2 Monaten (bei guter Marktlage)

### **KPIs zu tracken:**
- **Win Rate**: >60% (Ziel: 75%+)
- **Risk-Reward**: >1.2:1 (Ziel: 1.5:1+)
- **Max Drawdown**: <15% (Ziel: <10%)
- **Profit Factor**: >1.2 (Ziel: 1.5+)

**Ready to start? Good luck and trade safe! 🚀📈**
