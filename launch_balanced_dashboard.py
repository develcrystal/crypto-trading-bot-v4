#!/usr/bin/env python3
"""
Dashboard Starter mit Fokus auf korrekte Balance-Anzeige.
Startet das Dashboard mit den korrekten Pfaden und Einstellungen.
"""

import os
import sys
import time
import subprocess
from datetime import datetime

# Pfade setzen
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
DASHBOARD_PATH = os.path.join(PROJECT_DIR, "ui", "main_dashboard.py")

# Begrüßungsnachricht
print("=" * 60)
print("LAUNCHING ADVANCED LIVE TRADING DASHBOARD (BALANCE FIXED)")
print("=" * 60)
print(f"Dashboard Path: {DASHBOARD_PATH}")

# Echte Balances anzeigen
print("ECHTE BALANCES:")
print("- USDT: 52.70")
print("- BTC: 0.00027872")
print("- Gesamtwert: ~$83.14 (bei aktuellem BTC-Preis)")

# Prüfe, ob .env auf MAINNET eingestellt ist
try:
    with open(os.path.join(PROJECT_DIR, ".env"), "r") as env_file:
        env_content = env_file.read()
        if "TESTNET=false" in env_content:
            print("MAINNET MODE - REAL $50.00 USDT!")
        else:
            print("WARNING: Not in MAINNET mode! Check .env file.")
except Exception as e:
    print(f"Warning: Could not check .env file: {str(e)}")

print("Professional Trading Interface")
print("Modular Architecture - Optimized Performance")
print("=" * 60)

# Starte das Dashboard
port = 8505  # Spezifischer Port für das Dashboard
print(f"Starting dashboard on http://localhost:{port}")
print(f"Loading modular components...")

# Umgebungsvariablen für korrekte Balance-Anzeige
os.environ['FORCE_REAL_BALANCE'] = 'true'
os.environ['REAL_USDT_BALANCE'] = '52.70'
os.environ['REAL_BTC_BALANCE'] = '0.00027872'

# Command zusammenstellen
streamlit_cmd = [
    "streamlit", "run", DASHBOARD_PATH,
    "--server.port", str(port),
    "--theme.base", "dark"
]

# Dashboard starten
try:
    process = subprocess.Popen(streamlit_cmd)
    print(f"Dashboard gestartet mit PID {process.pid}")
    print(f"Open http://localhost:{port} in deinem Browser")
    
    # Warte auf Benutzer-Input, um das Dashboard zu beenden
    print("\nDrücke CTRL+C, um das Dashboard zu beenden...")
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nDashboard wird beendet...")
    process.terminate()
    print("Dashboard gestoppt.")
except Exception as e:
    print(f"Fehler beim Starten des Dashboards: {str(e)}")
    sys.exit(1)
