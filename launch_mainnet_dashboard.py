#!/usr/bin/env python3
"""
Launcher für das Advanced Live Trading Dashboard.
Startet das Dashboard mit den korrekten Pfaden und optimalen Einstellungen.
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
print("🚀 LAUNCHING ADVANCED LIVE TRADING DASHBOARD")
print("=" * 60)
print(f"📁 Dashboard Path: {DASHBOARD_PATH}")

# Prüfe, ob .env auf MAINNET eingestellt ist
try:
    with open(os.path.join(PROJECT_DIR, ".env"), "r") as env_file:
        env_content = env_file.read()
        if "TESTNET=false" in env_content:
            print("🔴 MAINNET MODE - REAL $50.00 USDT!")
        else:
            print("⚠️ WARNING: Not in MAINNET mode! Check .env file.")
except Exception as e:
    print(f"⚠️ Warning: Could not check .env file: {str(e)}")

print("💼 Professional Trading Interface")
print("⚡ Modular Architecture - Optimized Performance")
print("=" * 60)

# Starte das Dashboard
port = 8505  # Spezifischer Port für das Dashboard
print(f"🎯 Starting dashboard on http://localhost:{port}")
print(f"📊 Loading modular components...")

# Command zusammenstellen
streamlit_cmd = [
    "streamlit", "run", DASHBOARD_PATH,
    "--server.port", str(port),
    "--theme.base", "dark"
]

# Dashboard starten
try:
    process = subprocess.Popen(streamlit_cmd)
    print(f"✅ Dashboard gestartet mit PID {process.pid}")
    print(f"📈 Open http://localhost:{port} in deinem Browser")
    
    # Warte auf Benutzer-Input, um das Dashboard zu beenden
    print("\nDrücke CTRL+C, um das Dashboard zu beenden...")
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n⚠️ Dashboard wird beendet...")
    process.terminate()
    print("✅ Dashboard gestoppt.")
except Exception as e:
    print(f"❌ Fehler beim Starten des Dashboards: {str(e)}")
    sys.exit(1)
