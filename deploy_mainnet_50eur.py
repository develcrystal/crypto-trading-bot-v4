#!/usr/bin/env python
"""
🚀 MAINNET DEPLOYMENT SCRIPT - 50 EUR
Automatisiert das Setup für Bybit Mainnet Trading mit 50€
"""

import os
import sys
import shutil
from datetime import datetime

def main():
    print("=" * 60)
    print("🚀 MAINNET DEPLOYMENT - 50 EUR TRADING SETUP")
    print("=" * 60)
    print("⚠️  ACHTUNG: Dieser Script bereitet ECHTES Trading vor!")
    print("💰 Startkapital: 50 EUR | Risk: 2% per Trade")
    print("🛡️  Emergency Stop: 7.50 EUR (-15%)")
    print("=" * 60)
    
    # Bestätigung vom User
    confirm = input("\n🎯 Bereit für Mainnet Deployment? (ja/NEIN): ").lower()
    if confirm != 'ja':
        print("❌ Deployment abgebrochen.")
        return
    
    # API Keys prüfen
    print("\n📋 SCHRITT 1: API KEYS SETUP")
    print("Bitte gib deine BYBIT MAINNET API Credentials ein:")
    api_key = input("API Key: ").strip()
    api_secret = input("API Secret: ").strip()
    
    if not api_key or not api_secret:
        print("❌ API Keys sind erforderlich!")
        return
    
    # Backup der aktuellen .env
    print("\n📋 SCHRITT 2: BACKUP ERSTELLEN")
    try:
        shutil.copy('.env', f'.env.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
        print("✅ Backup erstellt")
    except Exception as e:
        print(f"⚠️  Backup fehlgeschlagen: {e}")
    
    # Mainnet .env erstellen
    print("\n📋 SCHRITT 3: MAINNET KONFIGURATION")
    mainnet_config = f"""# MAINNET CONFIGURATION - 50 EUR DEPLOYMENT
BYBIT_API_KEY={api_key}
BYBIT_API_SECRET={api_secret}
TESTNET=false

# 50 EUR TRADING PARAMETERS
INITIAL_PORTFOLIO_VALUE=50
MAX_RISK_PER_TRADE=0.02
MAX_DRAWDOWN=0.15
DAILY_RISK_LIMIT=5.0
MIN_TRADE_SIZE=5.0
MAX_TRADE_SIZE=10.0

# ENHANCED STRATEGY
RISK_REWARD_RATIO=1.5
POSITION_SIZE=0.1
VOLUME_THRESHOLD=100000

# LOGGING
LOG_LEVEL=INFO
LOG_FILE=mainnet_trading_50eur.log
"""
    
    with open('.env', 'w') as f:
        f.write(mainnet_config)
    
    print("✅ Mainnet-Konfiguration erstellt")
    
    print("\n🚀 DEPLOYMENT COMPLETE!")
    print("=" * 60)
    print("Nächste Schritte:")
    print("1. python enhanced_live_bot.py")
    print("2. Monitor Dashboard: streamlit run monitoring/bybit_focused_dashboard.py")
    print("3. Überwache die ersten Trades genau!")
    print("=" * 60)

if __name__ == "__main__":
    main()
