#!/usr/bin/env python3
"""
LIVE MAINNET READINESS CHECK
Überprüft, ob alle Komponenten für Live Trading bereit sind
"""

import os
import sys
import time
import importlib
from pathlib import Path

# Banner
print("=" * 70)
print("🚀 LIVE MAINNET READINESS CHECK")
print("=" * 70)
print("Überprüft, ob dein System bereit für Live Trading ist...")
print()

# 1. Check-Funktion für Pakete
def check_package(package_name, required=True):
    """Überprüft, ob ein Paket installiert ist"""
    try:
        importlib.import_module(package_name)
        print(f"✅ {package_name} ist installiert")
        return True
    except ImportError:
        if required:
            print(f"❌ {package_name} ist NICHT installiert (ERFORDERLICH)")
        else:
            print(f"⚠️ {package_name} ist nicht installiert (optional)")
        return False

# 2. Überprüfe erforderliche Python-Pakete
print("\n📦 PYTHON PAKETE ÜBERPRÜFUNG:")
required_packages = [
    "streamlit", 
    "pandas", 
    "plotly", 
    "requests", 
    "python-dotenv", 
    "psutil", 
    "numpy"
]

all_packages_installed = True
for package in required_packages:
    if not check_package(package):
        all_packages_installed = False

# 3. Überprüfe, ob Dateien existieren
print("\n📁 DATEI-ÜBERPRÜFUNG:")
base_dir = Path(__file__).parent.parent
required_files = [
    "enhanced_live_bot.py",
    "monitoring/LIVE_MAINNET_DASHBOARD.py",
    "monitoring/live_bybit_api.py",
    ".env"
]

all_files_exist = True
for file_path in required_files:
    full_path = base_dir / file_path
    if full_path.exists():
        print(f"✅ {file_path} existiert")
    else:
        print(f"❌ {file_path} existiert NICHT!")
        all_files_exist = False# 4. Überprüfe API-Konfiguration
print("\n🔑 API KONFIGURATION:")
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("BYBIT_API_KEY")
api_secret = os.getenv("BYBIT_API_SECRET")
testnet = os.getenv("TESTNET", "true").lower() == "true"

if api_key:
    # Nur die ersten und letzten 4 Zeichen anzeigen
    masked_key = api_key[:4] + "..." + api_key[-4:]
    print(f"✅ API Key ist konfiguriert: {masked_key}")
else:
    print("❌ API Key ist NICHT konfiguriert!")
    all_files_exist = False

if api_secret:
    masked_secret = api_secret[:4] + "..." + api_secret[-4:]
    print(f"✅ API Secret ist konfiguriert: {masked_secret}")
else:
    print("❌ API Secret ist NICHT konfiguriert!")
    all_files_exist = False

if testnet:
    print("⚠️ TESTNET=true - Für Mainnet auf false setzen!")
else:
    print("✅ TESTNET=false - Konfiguriert für MAINNET!")

# 5. Teste API-Verbindung
print("\n📡 API VERBINDUNGSTEST:")
sys.path.append(str(base_dir))
try:
    from monitoring.live_bybit_api import LiveBybitAPI
    
    print("🔄 Verbinde mit Bybit API...")
    api = LiveBybitAPI()
    result = api.get_wallet_balance()
    
    if result.get('success', False):
        print(f"✅ API-Verbindung erfolgreich!")
        print(f"💰 Balances gefunden:")
        for coin, amount in result.get('balances', {}).items():
            if coin == 'USDT':
                print(f"   • {coin}: {amount:.2f}")
            else:
                print(f"   • {coin}: {amount:.6f}")
        print(f"💵 Gesamtwert: ${result.get('total_usdt_value', 0):.2f} USDT")
    else:
        print(f"❌ API-Verbindung fehlgeschlagen: {result.get('error', 'Unbekannter Fehler')}")
        all_packages_installed = False
except Exception as e:
    print(f"❌ API-Test fehlgeschlagen: {str(e)}")
    all_packages_installed = False

# 6. Überprüfe Bot-Konfiguration für 50€ Deployment
print("\n⚙️ 50€ DEPLOYMENT CONFIG CHECK:")
try:
    sys.path.append(str(base_dir / "config"))
    import mainnet_50eur_config as config
    
    print(f"✅ 50€ Config geladen: Risk {config.RISK_PERCENTAGE}%, Max DD {config.MAX_DRAWDOWN}%")
    if hasattr(config, 'DAILY_RISK_LIMIT'):
        print(f"✅ Tägliches Risikolimit: {config.DAILY_RISK_LIMIT} USDT")
    
    if hasattr(config, 'MIN_TRADE_SIZE'):
        print(f"✅ Minimale Trade-Größe: {config.MIN_TRADE_SIZE} USDT")
    
    if hasattr(config, 'MAX_CONCURRENT_TRADES'):
        print(f"✅ Maximale gleichzeitige Trades: {config.MAX_CONCURRENT_TRADES}")
except Exception as e:
    print(f"⚠️ 50€ Config nicht geladen: {str(e)}")

# 7. Finale Bewertung
print("\n" + "=" * 70)
print("🚀 LIVE TRADING READINESS BEWERTUNG:")
print("=" * 70)

if all_packages_installed and all_files_exist:
    print("✅ SYSTEM IST BEREIT FÜR LIVE TRADING!")
    print("🚀 Du kannst das System mit folgendem Befehl starten:")
    print("   START_LIVE_MAINNET_SYSTEM.bat")
    
    if testnet:
        print("\n⚠️ WICHTIG: TESTNET=true in .env gefunden!")
        print("   Ändere zu TESTNET=false für echtes Mainnet Trading.")
else:
    print("❌ SYSTEM IST NICHT BEREIT FÜR LIVE TRADING!")
    print("   Bitte behebe die oben genannten Probleme.")

print("\n" + "=" * 70)
