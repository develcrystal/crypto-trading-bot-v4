#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Bybit API Vergleichs-Test
Vergleicht die Original- und die fixierte Version der BybitClient-Klasse
"""

import pandas as pd
import os
import sys
import time
from dotenv import load_dotenv

# Pfad zum Projekt-Verzeichnis hinzufügen
sys.path.append('J:\Meine Ablage\CodingStuff\crypto-bot_V2')

# Lade Umgebungsvariablen
load_dotenv()

def compare_bybit_clients():
    """Vergleicht die Original- und fixierte BybitClient-Implementierung"""
    print("\n===== BYBIT CLIENT VERGLEICH =====\n")
    
    # API-Konfiguration aus Umgebungsvariablen
    api_key = os.getenv('BYBIT_API_KEY')
    api_secret = os.getenv('BYBIT_API_SECRET')
    testnet = os.getenv('TESTNET', 'true').lower() == 'true'
    
    print(f"Testnet Mode: {testnet}")
    print(f"API Key vorhanden: {'Ja' if api_key else 'Nein'}")
    print(f"API Secret vorhanden: {'Ja' if api_secret else 'Nein'}")
    
    # Teste verschiedene Szenarien
    scenarios = [
        {"symbol": "BTCUSDT", "interval": 5, "limit": 10, "desc": "5-Minuten BTCUSDT (Klein)"},
        {"symbol": "BTCUSDT", "interval": 60, "limit": 30, "desc": "1-Stunde BTCUSDT (Mittel)"},
        {"symbol": "BTCUSDT", "interval": 1440, "limit": 30, "desc": "1-Tag BTCUSDT (Groß)"},
        {"symbol": "BTCUSDT", "interval": "D", "limit": 30, "desc": "1-Tag BTCUSDT (String)"},
        {"symbol": "ETHUSDT", "interval": 60, "limit": 30, "desc": "1-Stunde ETHUSDT (Alternative)"},
    ]
    
    # Teste Original-Client
    print("\n----- ORIGINAL CLIENT -----")
    from trading.bybit_client import BybitClient as OriginalClient
    original_client = OriginalClient(api_key=api_key, api_secret=api_secret, testnet=testnet)
    
    original_results = {}
    for scenario in scenarios:
        print(f"\nTeste: {scenario['desc']}")
        try:
            start_time = time.time()
            df = original_client.get_market_data(
                symbol=scenario['symbol'],
                interval=scenario['interval'],
                limit=scenario['limit']
            )
            end_time = time.time()
            
            print(f"Dauer: {end_time - start_time:.2f} Sekunden")
            if df is not None and isinstance(df, pd.DataFrame) and not df.empty:
                print(f"✅ Erfolg: {len(df)} Kerzen geladen")
                print(f"Erste Kerze: {df.iloc[0]['timestamp']} - Open: {df.iloc[0]['open']}, Close: {df.iloc[0]['close']}")
                print(f"Letzte Kerze: {df.iloc[-1]['timestamp']} - Open: {df.iloc[-1]['open']}, Close: {df.iloc[-1]['close']}")
                original_results[scenario['desc']] = True
            else:
                print("❌ Fehler: Keine Daten zurückgegeben")
                original_results[scenario['desc']] = False
        
        except Exception as e:
            print(f"❌ Fehler: {str(e)}")
            original_results[scenario['desc']] = False
    
    # Teste Fixierte Client
    print("\n----- FIXIERTE CLIENT -----")
    from trading.bybit_client_fixed import BybitClient as FixedClient
    fixed_client = FixedClient(api_key=api_key, api_secret=api_secret, testnet=testnet)
    
    fixed_results = {}
    for scenario in scenarios:
        print(f"\nTeste: {scenario['desc']}")
        try:
            start_time = time.time()
            df = fixed_client.get_market_data(
                symbol=scenario['symbol'],
                interval=scenario['interval'],
                limit=scenario['limit']
            )
            end_time = time.time()
            
            print(f"Dauer: {end_time - start_time:.2f} Sekunden")
            if df is not None and isinstance(df, pd.DataFrame) and not df.empty:
                print(f"✅ Erfolg: {len(df)} Kerzen geladen")
                print(f"Erste Kerze: {df.iloc[0]['timestamp']} - Open: {df.iloc[0]['open']}, Close: {df.iloc[0]['close']}")
                print(f"Letzte Kerze: {df.iloc[-1]['timestamp']} - Open: {df.iloc[-1]['open']}, Close: {df.iloc[-1]['close']}")
                fixed_results[scenario['desc']] = True
            else:
                print("❌ Fehler: Keine Daten zurückgegeben")
                fixed_results[scenario['desc']] = False
        
        except Exception as e:
            print(f"❌ Fehler: {str(e)}")
            fixed_results[scenario['desc']] = False
    
    # Ergebnis-Zusammenfassung
    print("\n===== ERGEBNIS-ZUSAMMENFASSUNG =====\n")
    print("| Szenario | Original | Fixiert |")
    print("|----------|----------|---------|")
    
    overall_original = True
    overall_fixed = True
    
    for scenario in scenarios:
        desc = scenario['desc']
        orig_result = "✅" if original_results.get(desc, False) else "❌"
        fixed_result = "✅" if fixed_results.get(desc, False) else "❌"
        print(f"| {desc} | {orig_result} | {fixed_result} |")
        
        if not original_results.get(desc, False):
            overall_original = False
        if not fixed_results.get(desc, False):
            overall_fixed = False
    
    print("\n----- GESAMTERGEBNIS -----")
    print(f"Original Client: {'✅ ERFOLGREICH' if overall_original else '❌ FEHLGESCHLAGEN'}")
    print(f"Fixierter Client: {'✅ ERFOLGREICH' if overall_fixed else '❌ FEHLGESCHLAGEN'}")
    
    if overall_fixed and not overall_original:
        print("\n🎉 ERFOLG: Der fixierte Client behebt die Probleme des Original-Clients!")
    elif overall_fixed and overall_original:
        print("\n✅ Beide Clients funktionieren korrekt.")
    else:
        print("\n⚠️ Der fixierte Client hat immer noch Probleme. Weitere Debugging erforderlich.")

if __name__ == "__main__":
    compare_bybit_clients()
