#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Modul-Test-Script für Enhanced Smart Money Bot
Überprüft, ob alle erforderlichen Module verfügbar sind
"""

import os
import sys

def check_modules():
    """Überprüft die Verfügbarkeit aller benötigten Module"""
    print("Python-Version:", sys.version)
    print("Python-Pfad:", sys.path)
    print("Aktuelles Verzeichnis:", os.getcwd())
    
    # Liste der benötigten Module
    required_modules = [
        "pybit",
        "pandas",
        "numpy",
        "streamlit",
        "plotly"
    ]
    
    # Überprüfe jedes Modul
    print("\nModul-Check:")
    for module in required_modules:
        try:
            __import__(module)
            print(f"[OK] {module}")
        except ImportError:
            print(f"[FEHLT] {module}")
    
    # Überprüfe Bybit-Client
    print("\nBybit-Client Check:")
    try:
        # Füge Projektverzeichnis zum Python-Pfad hinzu
        project_root = os.path.abspath(os.path.join(os.getcwd(), '..'))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
            print(f"Projektverzeichnis zum Python-Pfad hinzugefügt: {project_root}")
        
        # Überprüfe, ob trading/__init__.py existiert
        init_path = os.path.join(project_root, 'trading', '__init__.py')
        if os.path.exists(init_path):
            print(f"[OK] trading/__init__.py existiert")
        else:
            print(f"[FEHLT] trading/__init__.py")
            
            # Erstelle Verzeichnis falls es nicht existiert
            if not os.path.exists(os.path.join(project_root, 'trading')):
                os.makedirs(os.path.join(project_root, 'trading'))
                print(f"Verzeichnis 'trading' erstellt")
            
            # Erstelle __init__.py
            with open(init_path, 'w') as f:
                f.write("# Dieses Skript initialisiert das Python-Paket in diesem Verzeichnis\n")
                f.write("# Es wird benötigt, damit die Module korrekt importiert werden können\n")
            print(f"[OK] trading/__init__.py erstellt")
        
        # Überprüfe, ob bybit_client.py existiert
        client_path = os.path.join(project_root, 'trading', 'bybit_client.py')
        if os.path.exists(client_path):
            print(f"[OK] bybit_client.py existiert")
            
            # Überprüfe ob die erforderlichen Methoden implementiert sind
            with open(client_path, 'r') as f:
                content = f.read()
                if "def get_orderbook" in content:
                    print(f"[OK] get_orderbook() implementiert")
                else:
                    print(f"[FEHLT] get_orderbook()")
                
                if "def get_recent_trades" in content:
                    print(f"[OK] get_recent_trades() implementiert")
                else:
                    print(f"[FEHLT] get_recent_trades()")
        else:
            print(f"[FEHLT] bybit_client.py")
        
        # Versuche, den BybitClient zu importieren
        try:
            from trading.bybit_client import BybitClient
            print(f"[OK] BybitClient erfolgreich importiert")
            
            # Erstelle eine Instanz und teste grundlegende Funktionalität
            client = BybitClient()
            print(f"[OK] BybitClient Instanz erstellt")
        except ImportError as e:
            print(f"[FEHLER] BybitClient Import fehlgeschlagen - {e}")
        except Exception as e:
            print(f"[FEHLER] BybitClient Instanzerstellung - {e}")
    
    except Exception as e:
        print(f"Fehler beim Bybit-Client Check: {e}")
    
    print("\nDiagnostik abgeschlossen. Überprüfen Sie die Ergebnisse oben.")

if __name__ == "__main__":
    check_modules()
