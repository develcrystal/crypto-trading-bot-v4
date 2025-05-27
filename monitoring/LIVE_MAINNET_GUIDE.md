# 🚀 LIVE MAINNET DASHBOARD - SETUP & USAGE GUIDE

## 📋 Überblick

Das **Live Mainnet Dashboard** ist eine professionelle Schnittstelle für den **Enhanced Smart Money Trading Bot**. Es ermöglicht Echtzeit-Monitoring deiner Bybit-Trades und -Balances, mit manuellen Trading-Funktionen und Emergency-Controls.

**⚠️ WICHTIG: Diese Dashboard arbeitet mit ECHTEM GELD auf dem Bybit Mainnet!**

## 🔧 Setup

### 1. Abhängigkeiten installieren
```bash
# Führe das Setup-Script aus
python monitoring/install_dependencies.py

# Oder installiere manuell
pip install streamlit pandas plotly requests python-dotenv psutil numpy
```

### 2. API-Konfiguration (`.env` Datei)
```
# .env Datei für Mainnet konfigurieren
BYBIT_API_KEY=dein_mainnet_api_key
BYBIT_API_SECRET=dein_mainnet_api_secret
TESTNET=false  # WICHTIG: auf false setzen für Mainnet!
```

### 3. Dashboard starten
```bash
# Dashboard direkt starten
streamlit run monitoring/LIVE_MAINNET_DASHBOARD.py

# ODER verwende das Startup-Script
START_LIVE_MAINNET_SYSTEM.bat
```## 🎮 Dashboard-Funktionen

### 1. Live Portfolio Tracking
- Echte USDT und BTC Balances
- Live BTC Preis mit 24h Änderung
- Aktuelles Portfolio-Value in Echtzeit

### 2. Trading Bot Status
- Bot-Prozess-Überwachung
- Uptime-Tracking
- Market Regime Detection (BULL/BEAR/SIDEWAYS)
- Letztes Signal (BUY/SELL)

### 3. Manuelle Trading-Kontrollen
- Auswahl von Trading-Symbolen (BTC, ETH, SOL)
- Market und Limit Orders
- Stop-Loss und Take-Profit Einstellungen
- Order-Bestätigung mit Zusammenfassung

### 4. Notfall-Kontrollen
- Emergency Stop Button (stoppt Bot sofort)
- Position-Closing Optionen
- Live Trading Readiness Check

## 🚀 50€ Mainnet Deployment

### Risk Management für 50€
1. **Risiko pro Trade:** 1€ (2% von 50€)
2. **Position Size:** 5-10€ pro Trade
3. **Stop-Loss:** ~1€ pro verlorenem Trade
4. **Take-Profit:** 1.5-2€ pro gewonnenem Trade
5. **Daily Risk Limit:** 5€ (10% des Kapitals)
6. **Emergency Stop:** Bei 7.50€ Verlust (-15%)

### Bot-Konfiguration
Stelle sicher, dass der Enhanced Smart Money Bot konfiguriert ist:
- `RISK_PERCENTAGE = 2.0` (2% = 1€ pro Trade bei 50€)
- `MAX_DRAWDOWN = 15.0` (Emergency Stop bei 7.50€ Verlust)
- `POSITION_SIZE = 0.0001` (Kleine BTC-Positionen)
- `MIN_TRADE_SIZE = 5.0` (Minimum 5€ per Trade)

## ⚠️ Warnhinweise

1. **ECHTES GELD:** Alle Trades erfolgen mit echtem Geld auf dem Bybit Mainnet
2. **API-SICHERHEIT:** Beschränke API-Rechte auf das Notwendige
3. **RISIKO-MANAGEMENT:** Setze immer Stop-Loss um Verluste zu begrenzen
4. **MONITORING:** Überwache regelmäßig den Bot-Status und Performances
5. **TESTNET ZUERST:** Teste neue Strategien immer zuerst auf dem Testnet

## 🔍 Troubleshooting

### API Verbindungsprobleme
- Überprüfe API-Keys und Secret
- Stelle sicher, dass TESTNET=false in .env
- Prüfe Internet-Verbindung
- Prüfe, ob Bybit API erreichbar ist

### Bot-Status nicht sichtbar
- Stelle sicher, dass psutil installiert ist
- Prüfe, ob der Bot tatsächlich läuft
- Überprüfe Logfiles auf Fehler

### Order-Ausführungsprobleme
- Prüfe auf ausreichende Balance
- Stelle sicher, dass Order-Größe > Minimum
- Prüfe auf API-Berechtigungen für Trading

## 💼 Verantwortungsvoller Einsatz

Dieses Live Mainnet Dashboard ist ein professionelles Tool für echtes Trading. Verwende es verantwortungsvoll und starte mit kleinen Beträgen (50€), bis du die Performance und Zuverlässigkeit validiert hast.

**Start mit dem Deployment-Plan:**
1. Validiere Strategie mit 50€ für 1-2 Monate
2. Scale-Up auf 100€ bei +20% Erfolg
3. Weiter auf 250€ bei bewiesener Konsistenz
4. 500€+ nur bei nachgewiesener Profitabilität über 6+ Monate

---

**🚀 Ready for Live Trading? Start the system and monitor your real trades!**