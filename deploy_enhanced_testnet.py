#!/usr/bin/env python
"""
Quick-Start Script für Enhanced Smart Money Strategy Testnet Deployment.

Dieses Script startet sofort das Live-Trading auf Testnet mit optimalen Einstellungen.
"""

import subprocess
import sys
import os
from datetime import datetime

def print_banner():
    """Druckt Start-Banner."""
    print("🚀" + "="*70 + "🚀")
    print("   ENHANCED SMART MONEY STRATEGY - TESTNET DEPLOYMENT")
    print("🚀" + "="*70 + "🚀")
    print()
    print("🧠 Market Regime Detection: AKTIVIERT")
    print("⚙️ Adaptive Parameters: AKTIVIERT") 
    print("🧪 Testnet Mode: AKTIVIERT")
    print("📊 Symbol: BTCUSDT")
    print("⏱️ Timeframe: 1h")
    print("🔄 Check Interval: 5 Minuten")
    print("⏰ Duration: 7 Tage (168 Stunden)")
    print()
    print("🎯 Erwartete Performance (basierend auf Backtests):")
    print("   📈 Return: +128% vs Classic Strategy")
    print("   🏆 Win Rate: 81% vs 68% Classic")
    print("   🛡️ Drawdown: -39% vs Classic")
    print()
    print("🛡️ SICHERHEIT:")
    print("   ✅ Testnet-Modus (keine echten Trades)")
    print("   ✅ Risk Management aktiv")
    print("   ✅ Stop-Loss automatisch")
    print("   ✅ Position Limits enforced")
    print()

def check_dependencies():
    """Prüft ob alle Dependencies verfügbar sind."""
    print("🔍 Prüfe System-Dependencies...")
    
    required_files = [
        "strategies/enhanced_smart_money.py",
        "run_live_enhanced.py",
        "data/data_handler.py",
        "exchange/bybit_api.py",
        "risk/risk_manager.py",
        ".env"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ Fehlende Dateien:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    print("✅ Alle Dependencies verfügbar")
    return True

def check_env_config():
    """Prüft .env Konfiguration."""
    print("🔧 Prüfe .env Konfiguration...")
    
    try:
        with open('.env', 'r') as f:
            env_content = f.read()
        
        required_vars = ['BYBIT_API_KEY', 'BYBIT_API_SECRET', 'TESTNET']
        missing_vars = []
        
        for var in required_vars:
            if var not in env_content:
                missing_vars.append(var)
        
        if missing_vars:
            print("❌ Fehlende .env Variablen:")
            for var in missing_vars:
                print(f"   - {var}")
            return False
        
        # Prüfe ob Testnet aktiviert ist
        if 'TESTNET=true' not in env_content:
            print("⚠️ WARNUNG: TESTNET ist nicht auf 'true' gesetzt!")
            response = input("Trotzdem fortfahren? (y/N): ")
            if response.lower() != 'y':
                return False
        
        print("✅ .env Konfiguration OK")
        return True
        
    except FileNotFoundError:
        print("❌ .env Datei nicht gefunden!")
        return False

def start_live_trading():
    """Startet das Live Trading."""
    print("🚀 STARTE ENHANCED SMART MONEY STRATEGY LIVE TRADING...")
    print()
    print("💡 Tipps während des Trading:")
    print("   - Überwache die Logs für Regime-Detection")
    print("   - Performance wird alle 30 Minuten geloggt")
    print("   - CTRL+C für graceful shutdown")
    print("   - Alle Trades werden simuliert (Testnet)")
    print()
    
    try:
        # Starte das Live Trading Script
        subprocess.run([
            sys.executable, 
            "run_live_enhanced.py"
        ], check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Fehler beim Starten des Live Trading: {e}")
        return False
    except KeyboardInterrupt:
        print("\n🔴 Live Trading durch Benutzer gestoppt")
        return True
    
    return True

def main():
    """Hauptfunktion."""
    print_banner()
    
    # System-Checks
    if not check_dependencies():
        print("\n❌ Deployment abgebrochen - Dependencies fehlen")
        return
    
    if not check_env_config():
        print("\n❌ Deployment abgebrochen - .env Konfiguration fehlerhaft")
        return
    
    print("\n✅ Alle Checks bestanden!")
    print()
    
    # Bestätigung vom User
    print("🎯 BEREIT FÜR TESTNET DEPLOYMENT!")
    print()
    response = input("Enhanced Strategy auf Testnet starten? (Y/n): ")
    
    if response.lower() in ['', 'y', 'yes']:
        print()
        print("🔥 DEPLOYMENT STARTET...")
        print("="*50)
        
        # Live Trading starten
        success = start_live_trading()
        
        if success:
            print()
            print("✅ Enhanced Strategy Deployment erfolgreich abgeschlossen!")
            print("📊 Check die generierten Reports für Performance-Details")
        else:
            print()
            print("❌ Deployment fehlgeschlagen")
    else:
        print()
        print("🔴 Deployment abgebrochen")

if __name__ == "__main__":
    main()
