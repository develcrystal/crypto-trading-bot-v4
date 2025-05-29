#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Bybit API Debug Script
Diagnose und Behebung von Problemen mit der get_market_data-Methode
"""

from pybit.unified_trading import HTTP
import pandas as pd
import json
import os
import time
from dotenv import load_dotenv

# Lade Umgebungsvariablen
load_dotenv()

# API-Konfiguration
API_KEY = os.getenv('BYBIT_API_KEY')
API_SECRET = os.getenv('BYBIT_API_SECRET')
TESTNET = os.getenv('TESTNET', 'true').lower() == 'true'

def debug_bybit_api():
    """Diagnose und Debug der Bybit API-Verbindung"""
    print("\n===== BYBIT API DEBUGGING =====\n")
    print(f"Testnet Mode: {TESTNET}")
    print(f"API Key vorhanden: {'Ja' if API_KEY else 'Nein'}")
    print(f"API Secret vorhanden: {'Ja' if API_SECRET else 'Nein'}")
    
    try:
        # Initialisiere Session
        session = HTTP(
            testnet=TESTNET,
            api_key=API_KEY,
            api_secret=API_SECRET
        )
        
        print("\n----- Server Time Check -----")
        server_time = session.get_server_time()
        print(f"Server Time: {server_time}")
        
        print("\n----- Test API Verbindung -----")
        # Teste mit einfachem API-Aufruf
        symbols = session.get_instruments_info(category="spot")
        print(f"API-Verbindung erfolgreich: {symbols['retCode'] == 0}")
        print(f"Anzahl Spot-Instrumente: {len(symbols.get('result', {}).get('list', []))}")
        
        # Teste verschiedene Kategorien und Intervalle
        categories = ["spot", "linear"]
        intervals = ["1", "5", "15", "30", "60", "240", "D"]
        symbol = "BTCUSDT"
        limit = 10
        
        print("\n----- Teste verschiedene Konfigurationen -----")
        
        for category in categories:
            for interval in intervals:
                print(f"\nTeste: Category={category}, Symbol={symbol}, Interval={interval}, Limit={limit}")
                
                try:
                    start_time = time.time()
                    response = session.get_kline(
                        category=category,
                        symbol=symbol,
                        interval=interval,
                        limit=limit
                    )
                    end_time = time.time()
                    
                    print(f"Dauer: {end_time - start_time:.2f} Sekunden")
                    print(f"Response Code: {response.get('retCode')}")
                    print(f"Response Msg: {response.get('retMsg')}")
                    
                    if response.get('retCode') == 0:
                        data = response.get('result', {}).get('list', [])
                        print(f"Daten erhalten: {len(data)} Einträge")
                        
                        if data:
                            # Untersuche Datenstruktur des ersten Elements
                            print(f"Erstes Element Schema:")
                            for i, value in enumerate(data[0]):
                                print(f"  Position {i}: {value} (Typ: {type(value).__name__})")
                            
                            # Wandle Daten in DataFrame um
                            columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'turnover']
                            if len(data[0]) >= len(columns):
                                df = pd.DataFrame(data, columns=columns)
                                print(f"DataFrame erstellt mit Spalten: {df.columns.tolist()}")
                                print(f"Datentypen: {df.dtypes}")
                                print(f"Nullwerte: {df.isnull().sum().sum()}")
                                print(f"DataFrame Beispiel:")
                                print(df.head(2))
                            else:
                                print(f"WARNUNG: Daten haben {len(data[0])} Elemente, erwartet wurden {len(columns)}")
                                print(f"Vollständige Daten: {data[0]}")
                        else:
                            print("Keine Daten in der Antwort")
                    else:
                        print(f"Fehler: {response.get('retMsg')}")
                
                except Exception as e:
                    print(f"Fehler beim Testen von {category}/{interval}: {str(e)}")
        
        # Tieferer Test für einen spezifischen Fall
        print("\n----- Detaillierter Test für 1-Tages-Intervall (BTCUSDT) -----")
        try:
            category = "spot"
            interval = "D"
            response = session.get_kline(
                category=category,
                symbol=symbol,
                interval=interval,
                limit=5
            )
            
            print(f"Response Code: {response.get('retCode')}")
            print(f"Response Msg: {response.get('retMsg')}")
            
            if response.get('retCode') == 0:
                print("\nVollständige API-Antwort:")
                print(json.dumps(response, indent=2))
                
                data = response.get('result', {}).get('list', [])
                if data:
                    # Versuche mit korrekten Spalten
                    columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'turnover']
                    if len(data[0]) >= len(columns):
                        df = pd.DataFrame(data, columns=columns)
                        
                        # Convert data types
                        for col in ['open', 'high', 'low', 'close', 'volume']:
                            df[col] = pd.to_numeric(df[col], errors='coerce')
                        
                        df['timestamp'] = pd.to_datetime(df['timestamp'].astype('int64'), unit='ms')
                        df = df.sort_values('timestamp')
                        
                        print("\nErfolgreich konvertiertes DataFrame:")
                        print(df[['timestamp', 'open', 'high', 'low', 'close', 'volume']])
                    else:
                        print(f"WARNUNG: Daten haben {len(data[0])} Elemente, erwartet wurden {len(columns)}")
            else:
                print(f"Fehler: {response.get('retMsg')}")
        
        except Exception as e:
            print(f"Fehler beim detaillierten Test: {str(e)}")
    
    except Exception as e:
        print(f"Kritischer Fehler: {str(e)}")

if __name__ == "__main__":
    debug_bybit_api()
