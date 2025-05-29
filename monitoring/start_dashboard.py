"""
🚀 Enhanced Smart Money Bot Dashboard - Startup Script
Startet das Dashboard und stellt sicher, dass alle Voraussetzungen erfüllt sind
"""

import sys
import os
import subprocess
import importlib.util
import time

def check_dependencies():
    """Überprüft, ob alle notwendigen Abhängigkeiten installiert sind"""
    missing_packages = []
    
    # Liste der benötigten Pakete
    required_packages = [
        'streamlit',
        'pandas',
        'numpy',
        'plotly',
        'pybit',
        'requests',
        'python-dotenv'
    ]
    
    for package in required_packages:
        if importlib.util.find_spec(package) is None:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"Fehlende Abhängigkeiten: {', '.join(missing_packages)}")
        install = input("Möchten Sie die fehlenden Pakete installieren? (j/n): ")
        if install.lower() == 'j':
            for package in missing_packages:
                try:
                    subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
                    print(f"{package} erfolgreich installiert.")
                except subprocess.CalledProcessError:
                    print(f"Fehler beim Installieren von {package}.")
                    return False
            return True
        else:
            return False
    else:
        print("✅ Alle benötigten Abhängigkeiten sind installiert.")
        return True

def check_trading_module():
    """Überprüft, ob das Trading-Modul korrekt konfiguriert ist"""
    # Füge das Projektverzeichnis zum Python-Pfad hinzu
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
        print(f"Projektverzeichnis zum Python-Pfad hinzugefügt: {project_root}")
    
    # Überprüfe, ob die __init__.py-Datei im Trading-Modul existiert
    init_file = os.path.join(project_root, 'trading', '__init__.py')
    if not os.path.exists(init_file):
        print("⚠️ trading/__init__.py nicht gefunden. Erstelle Datei...")
        try:
            os.makedirs(os.path.dirname(init_file), exist_ok=True)
            with open(init_file, 'w') as f:
                f.write('"""Trading module for Smart Money Bot"""')
            print("✅ trading/__init__.py erfolgreich erstellt.")
        except Exception as e:
            print(f"❌ Fehler beim Erstellen von trading/__init__.py: {e}")
            return False
    
    # Überprüfe, ob die bybit_client.py-Datei existiert
    client_file = os.path.join(project_root, 'trading', 'bybit_client.py')
    if not os.path.exists(client_file):
        print("❌ trading/bybit_client.py nicht gefunden.")
        return False
    
    # Versuche, das Trading-Modul zu importieren
    try:
        import trading
        print(f"✅ Trading-Modul erfolgreich importiert. Modul-Pfad: {trading.__file__}")
        return True
    except ImportError as e:
        print(f"❌ Fehler beim Importieren des Trading-Moduls: {e}")
        return False

def check_env_file():
    """Überprüft, ob die .env-Datei existiert und korrekt konfiguriert ist"""
    env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    if not os.path.exists(env_file):
        print("⚠️ .env-Datei nicht gefunden. Erstelle Beispiel-Datei...")
        try:
            with open(env_file, 'w') as f:
                f.write("""# Bybit API Credentials
BYBIT_API_KEY=your_api_key_here
BYBIT_API_SECRET=your_api_secret_here
TESTNET=true
""")
            print("✅ .env-Beispiel-Datei erstellt. Bitte bearbeiten Sie die Datei mit Ihren API-Zugangsdaten.")
        except Exception as e:
            print(f"❌ Fehler beim Erstellen der .env-Datei: {e}")
            return False
    else:
        print("✅ .env-Datei gefunden.")
    return True

def start_dashboard():
    """Startet das Streamlit-Dashboard"""
    dashboard_file = os.path.join(os.path.dirname(__file__), 'enhanced_smart_money_bot_dashboard.py')
    if not os.path.exists(dashboard_file):
        print(f"❌ Dashboard-Datei nicht gefunden: {dashboard_file}")
        return False
    
    print("🚀 Starte Dashboard...")
    try:
        subprocess.run([sys.executable, '-m', 'streamlit', 'run', dashboard_file, '--server.port', '8505'])
        return True
    except Exception as e:
        print(f"❌ Fehler beim Starten des Dashboards: {e}")
        return False

def main():
    """Hauptfunktion"""
    print("=" * 60)
    print("🚀 ENHANCED SMART MONEY BOT DASHBOARD - STARTUP")
    print("=" * 60)
    print()
    
    # Überprüfe Abhängigkeiten
    if not check_dependencies():
        print("❌ Abhängigkeiten nicht vollständig. Bitte installieren Sie die fehlenden Pakete.")
        return
    
    # Überprüfe Trading-Modul
    if not check_trading_module():
        print("❌ Trading-Modul nicht korrekt konfiguriert.")
        return
    
    # Überprüfe .env-Datei
    if not check_env_file():
        print("❌ .env-Datei nicht korrekt konfiguriert.")
        return
    
    # Starte Dashboard
    print()
    print("=" * 60)
    print("✅ Alle Voraussetzungen erfüllt. Dashboard wird gestartet...")
    print("=" * 60)
    print()
    
    # Kurze Verzögerung für bessere Lesbarkeit
    time.sleep(1)
    
    start_dashboard()

if __name__ == "__main__":
    main()
