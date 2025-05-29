#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Installation und Test-Script für Enhanced Smart Money Bot
Richtet die notwendigen Module und Dateien ein
"""

import os
import sys
import subprocess
import importlib

# Setze den korrekten Projektpfad
PROJECT_PATH = r"J:\Meine Ablage\CodingStuff\crypto-bot_V2"
os.chdir(PROJECT_PATH)

def setup_environment():
    """Richtet die Umgebung ein und überprüft Module"""
    print("=== SETUP UND TEST FÜR ENHANCED SMART MONEY BOT ===")
    print(f"Projektpfad: {PROJECT_PATH}")
    print(f"Aktuelles Verzeichnis: {os.getcwd()}")
    
    # Erstelle trading-Verzeichnis, falls es nicht existiert
    trading_dir = os.path.join(PROJECT_PATH, 'trading')
    if not os.path.exists(trading_dir):
        os.makedirs(trading_dir)
        print(f"[OK] Trading-Verzeichnis erstellt: {trading_dir}")
    
    # Erstelle __init__.py, falls es nicht existiert
    init_file = os.path.join(trading_dir, '__init__.py')
    if not os.path.exists(init_file):
        with open(init_file, 'w') as f:
            f.write("# Dieses Skript initialisiert das Python-Paket in diesem Verzeichnis\n")
            f.write("# Es wird benötigt, damit die Module korrekt importiert werden können\n")
        print(f"[OK] __init__.py erstellt: {init_file}")
    
    # Überprüfe Module
    required_modules = ["pybit", "pandas", "numpy", "streamlit", "plotly"]
    missing_modules = []
    
    for module in required_modules:
        try:
            importlib.import_module(module)
            print(f"[OK] Modul gefunden: {module}")
        except ImportError:
            print(f"[FEHLT] Modul nicht gefunden: {module}")
            missing_modules.append(module)
    
    # Installiere fehlende Module
    if missing_modules:
        print("\n=== INSTALLATION FEHLENDER MODULE ===")
        for module in missing_modules:
            try:
                print(f"Installiere {module}...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", module])
                print(f"[OK] {module} erfolgreich installiert")
            except Exception as e:
                print(f"[FEHLER] Konnte {module} nicht installieren: {e}")
    
    # Starte das Dashboard neu
    print("\n=== STARTE DASHBOARD NEU ===")
    try:
        print("Öffne eine neue Kommandozeile und führe aus:")
        print(f"cd {os.path.join(PROJECT_PATH, 'monitoring')}")
        print("streamlit run enhanced_smart_money_bot_dashboard.py")
    except Exception as e:
        print(f"[FEHLER] Konnte Dashboard nicht starten: {e}")
    
    print("\nSetup und Test abgeschlossen. Überprüfen Sie die Ergebnisse oben.")

if __name__ == "__main__":
    setup_environment()
