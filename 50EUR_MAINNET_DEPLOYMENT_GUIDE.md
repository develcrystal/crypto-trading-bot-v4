# 🚀 50€ MAINNET DEPLOYMENT GUIDE

## ⚠️ WARNUNG: ECHTES GELD

Dieses Dokument beschreibt die Schritte für das Deployment des Enhanced Smart Money Trading Bots mit **echtem Geld** (50€) auf dem Bybit Mainnet. Alle Trades werden mit echtem Kapital ausgeführt.

## 📋 SCHRITT-FÜR-SCHRITT ANLEITUNG

### Schritt 1: System-Readiness überprüfen
```
1. Führe CHECK_LIVE_TRADING_READINESS.bat aus
2. Behebe alle Probleme, die angezeigt werden
3. Stelle sicher, dass alle Abhängigkeiten installiert sind
```

### Schritt 2: Bybit Mainnet Account vorbereiten
```
1. Logge dich in deinen Bybit Account ein (nicht Testnet)
2. Transferiere genau 50€ USDT auf dein Spot Wallet
3. Erstelle einen API-Key mit Trading-Berechtigung
4. Aktiviere IP-Beschränkung für zusätzliche Sicherheit
5. Notiere API-Key und Secret
```

### Schritt 3: Konfiguration für Mainnet
```
1. Öffne die .env Datei
2. Setze BYBIT_API_KEY auf deinen Mainnet API Key
3. Setze BYBIT_API_SECRET auf dein Mainnet API Secret
4. Setze TESTNET=false für Mainnet
5. Speichere die Datei
```

### Schritt 4: Risk Management für 50€
```
1. Stelle sicher, dass config/mainnet_50eur_config.py existiert
2. Überprüfe folgende Parameter:
   - RISK_PERCENTAGE = 2.0 (2% = 1€ pro Trade)
   - MAX_DRAWDOWN = 15.0 (max 7.50€ Verlust)
   - DAILY_RISK_LIMIT = 5.0 (max 5€ Verlust pro Tag)
   - MIN_TRADE_SIZE = 5.0 (min 5€ pro Trade)
   - MAX_CONCURRENT_TRADES = 2 (max 2 offene Positionen)
```