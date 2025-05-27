#!/usr/bin/env python3
"""
Installiert notwendige Abhängigkeiten für das LIVE_MAINNET_DASHBOARD
"""

import subprocess
import sys
import os

def check_and_install(package):
    """Prüft ob Paket installiert ist und installiert es wenn nötig"""
    try:
        __import__(package)
        print(f"✅ {package} ist bereits installiert.")
        return True
    except ImportError:
        print(f"⚠️ {package} ist nicht installiert. Wird installiert...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ {package} wurde erfolgreich installiert.")
            return True
        except Exception as e:
            print(f"❌ Fehler bei der Installation von {package}: {e}")
            return False

def main():
    """Hauptfunktion zur Installation der Abhängigkeiten"""
    print("🔍 Prüfe und installiere notwendige Abhängigkeiten für das Live Mainnet Dashboard...")
    
    # Liste der benötigten Pakete
    packages = [
        "streamlit",
        "pandas",
        "plotly",
        "requests",
        "python-dotenv",
        "psutil",
        "numpy"
    ]
    
    # Installiere alle Pakete
    all_success = True
    for package in packages:
        if not check_and_install(package):
            all_success = False
    
    if all_success:
        print("\n✅ Alle Abhängigkeiten wurden erfolgreich installiert!")
        print("🚀 Du kannst das Dashboard jetzt mit folgendem Befehl starten:")
        print("   streamlit run monitoring/LIVE_MAINNET_DASHBOARD.py")
    else:
        print("\n⚠️ Es gab Probleme bei der Installation einiger Abhängigkeiten.")
        print("   Bitte installiere die fehlenden Pakete manuell mit pip install.")

if __name__ == "__main__":
    main()
