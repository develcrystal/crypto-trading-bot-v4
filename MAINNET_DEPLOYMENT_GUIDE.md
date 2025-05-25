# 🚀 MAINNET DEPLOYMENT INSTRUCTIONS - 50 EUR TRADING

## SCHRITT 1: API SETUP
1. Gehe zu https://bybit.com (NICHT testnet.bybit.com)
2. Erstelle API Key mit Trading-Berechtigungen
3. Ersetze in .env Datei:
   BYBIT_API_KEY=DEINE_MAINNET_API_KEY
   BYBIT_API_SECRET=DEINE_MAINNET_API_SECRET
   TESTNET=false  # ← WICHTIG: auf false setzen!

## SCHRITT 2: SICHERHEITS-KONFIGURATION
Öffne .env und setze für 50 EUR Trading:
INITIAL_PORTFOLIO_VALUE=50
MAX_RISK_PER_TRADE=0.02  # 2% = 1 EUR pro Trade
MAX_DRAWDOWN=0.15        # 15% = 7.50 EUR Emergency Stop
DAILY_RISK_LIMIT=5.0     # Max 5 EUR Verlust pro Tag

## SCHRITT 3: DEPLOYMENT COMMANDS
cd "J:\Meine Ablage\CodingStuff\crypto-bot_V2"
conda activate crypto-bot_V2

# Backup erstellen
copy .env .env.backup

# Mainnet-Konfiguration aktivieren
copy .env.MAINNET .env

# Bot starten
python enhanced_live_bot.py

## WARNUNG: Erst .env auf TESTNET=false setzen!
