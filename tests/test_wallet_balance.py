#!/usr/bin/env python3
"""
WALLET BALANCE TEST
Testet die Wallet-Balance-Abfrage, um die korrekten Balances im Dashboard anzuzeigen
"""

import sys
import os
import time
from datetime import datetime
from dotenv import load_dotenv

# Füge Projektverzeichnis zum Pfad hinzu
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(script_dir)
sys.path.append(project_dir)

# Lade Umgebungsvariablen
load_dotenv()

# Importiere API-Client
from core.api_client import BybitAPI as BybitAPIClient
try:
    from monitoring.live_bybit_api import LiveBybitAPI
    LIVE_API_AVAILABLE = True
except ImportError:
    LIVE_API_AVAILABLE = False


def test_wallet_balance():
    """Testet die Wallet-Balance-Abfrage mit beiden API-Clients"""
    
    print("=" * 80)
    print("WALLET BALANCE TEST - BYBIT MAINNET")
    print("=" * 80)
    
    # TESTNET Flag aus .env lesen
    testnet_status = os.getenv('TESTNET', 'true').lower() == 'true'
    print(f"TESTNET Configuration: {testnet_status}")
    
    # Wenn TESTNET=true ist, aber wir auf Mainnet testen wollen
    if testnet_status:
        print("\nACHTUNG: TESTNET=true in .env-Datei, aber wir testen MAINNET\n")
        print("Falls dieser Test für Mainnet sein soll, bitte TESTNET=false in .env setzen")
    
    # 1. Teste Standard-API-Client
    print("\n1. Testing Standard API Client...")
    api = BybitAPIClient()
    
    print(f"API Base URL: {api.base_url}")
    print(f"Testnet Mode: {api.testnet}")
    
    # Wallet-Balance-Abfrage
    print("\nWallet Balance Abfrage:")
    result = api.get_wallet_balance()
    
    if result['success']:
        print("Wallet-Balance-Abfrage erfolgreich!")
        print(f"Account Type: {result.get('account_type', 'Unknown')}")
        print(f"Total USDT Value: ${result['total_usdt_value']:.2f}")
        
        print("\nBalances:")
        for coin, amount in result['balances'].items():
            if coin == 'USDT':
                print(f"   {coin}: {amount:.2f}")
            else:
                print(f"   {coin}: {amount:.8f}")
    else:
        print("Wallet-Balance-Abfrage fehlgeschlagen!")
        print(f"Error: {result.get('error', 'Unknown')}")
    
    # 2. Teste Live-API, falls verfügbar
    if LIVE_API_AVAILABLE:
        print("\n" + "=" * 40)
        print("2. Testing Live Bybit API...")
        live_api = LiveBybitAPI()
        
        print(f"API Base URL: {live_api.base_url}")
        print(f"Testnet Mode: {live_api.testnet}")
        
        # Wallet-Balance-Abfrage
        print("\nWallet Balance Abfrage:")
        live_result = live_api.get_wallet_balance()
        
        if live_result['success']:
            print("Wallet-Balance-Abfrage erfolgreich!")
            print(f"Total USDT Value: ${live_result['total_usdt_value']:.2f}")
            
            print("\nBalances:")
            for coin, amount in live_result['balances'].items():
                if coin == 'USDT':
                    print(f"   {coin}: {amount:.2f}")
                else:
                    print(f"   {coin}: {amount:.8f}")
        else:
            print("Wallet-Balance-Abfrage fehlgeschlagen!")
            print(f"Error: {live_result.get('error', 'Unknown')}")
        
        # Teste komplettes Dashboard-Data
        print("\n" + "=" * 40)
        print("3. Testing Complete Dashboard Data...")
        dashboard_result = live_api.get_dashboard_data()
        
        if dashboard_result['success']:
            print("Dashboard-Daten-Abfrage erfolgreich!")
            print(f"Portfolio Value: ${dashboard_result['portfolio_value']:.2f}")
            print(f"BTC Price: ${dashboard_result['btc_price']:,.2f}")
            print(f"Account Type: {dashboard_result['account_type']}")
            
            print("\nBalances:")
            for coin, amount in dashboard_result['balances'].items():
                if coin == 'USDT':
                    print(f"   {coin}: {amount:.2f}")
                else:
                    print(f"   {coin}: {amount:.8f}")
        else:
            print("Dashboard-Daten-Abfrage fehlgeschlagen!")
            print(f"Error: {dashboard_result.get('error', 'Unknown error')}")
    else:
        print("\nLive Bybit API nicht verfügbar. Überspringe Test.")
    
    print("\n" + "=" * 80)
    print("WALLET BALANCE TEST ABGESCHLOSSEN")
    print("=" * 80)
    
    print("\nFalls die Balance-Werte im Dashboard nicht korrekt angezeigt werden, überprüfe die API-Integration.")
    print("Die korrekte Balance sollte sein:")
    print("- USDT: 52.70")
    print("- BTC: 0.00027872")
    print("- Gesamtwert: ~$52.70")
    
    print("\nTipps zur Fehlerbehebung:")
    print("1. Überprüfe, ob der Datenmanager die richtigen Daten von der API erhält")
    print("2. Stelle sicher, dass die Dashboard-Komponenten die richtigen Daten anzeigen")
    print("3. Achte auf zwischengespeicherte Daten im Session State")


if __name__ == "__main__":
    # Führe Test aus
    test_wallet_balance()
