#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Dashboard Fix Helper
Behebt Importprobleme und Kodierungsprobleme im Dashboard
"""

import os
import sys
import shutil
import subprocess
from datetime import datetime

def fix_dashboard_issues():
    """Behebt Probleme mit dem Dashboard"""
    print("\n===== DASHBOARD FIX HELPER =====\n")
    
    # Setze Pfade
    project_dir = r"J:\Meine Ablage\CodingStuff\crypto-bot_V2"
    backup_dir = os.path.join(project_dir, "backups", f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    
    # Erstelle Backup-Verzeichnis
    os.makedirs(backup_dir, exist_ok=True)
    print("[INFO] Backup-Verzeichnis erstellt:", backup_dir)
    
    # 1. Pruefe und installiere pybit
    print("\n[STEP 1] Pruefe pybit-Installation")
    try:
        import pybit
        print("[OK] pybit ist bereits installiert. Version:", pybit.__version__)
    except ImportError:
        print("[WARN] pybit ist nicht installiert. Versuche zu installieren...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pybit"])
            print("[OK] pybit erfolgreich installiert")
        except Exception as e:
            print("[ERROR] Fehler bei der Installation von pybit:", str(e))
            print("[INFO] Bitte manuell installieren mit: pip install pybit")
    
    # 2. Fixiere bybit_client.py
    print("\n[STEP 2] Fixiere bybit_client.py")
    bybit_client_path = os.path.join(project_dir, "trading", "bybit_client.py")
    bybit_client_backup = os.path.join(backup_dir, "bybit_client.py")
    
    # Backup erstellen
    if os.path.exists(bybit_client_path):
        shutil.copy2(bybit_client_path, bybit_client_backup)
        print("[OK] Backup von bybit_client.py erstellt")
    
    # Korrigiere den Client-Code
    try:
        # Erstelle neuen bybit_client.py ohne Kodierungsprobleme
        with open(bybit_client_path, 'w', encoding='utf-8') as f:
            f.write("""from pybit.unified_trading import HTTP
import pandas as pd
from datetime import datetime, timedelta
import time
import logging

# Konfiguriere Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("BybitClient")

class BybitClient:
    def __init__(self, api_key=None, api_secret=None, testnet=False):
        """Initialize Bybit client with API credentials"""
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        self.session = HTTP(
            testnet=self.testnet,
            api_key=self.api_key,
            api_secret=self.api_secret
        )
        logger.info(f"BybitClient initialisiert (Testnet: {self.testnet})")
    
    def get_market_data(self, symbol="BTCUSDT", interval=5, limit=200):
        """
        Get kline/candlestick data with improved error handling and debugging
        
        Args:
            symbol (str): Trading pair, e.g. "BTCUSDT"
            interval (str/int): Timeframe, e.g. "1", "5", "15", "30", "60", "240", "D"
            limit (int): Number of candles to retrieve (max 1000)
            
        Returns:
            pd.DataFrame or None: DataFrame with candlestick data or None on error
        """
        try:
            # Konvertiere interval in den passenden String fuer die API
            # Spezialfall fuer Tages-Intervall: 1440 oder "D"
            if interval == 1440 or interval == "1440":
                interval_str = "D"
            else:
                interval_str = str(interval)
            
            logger.info(f"Abrufen von Kerzen fuer {symbol}, Intervall {interval_str}, Limit {limit}")
            print(f"Fetching kline data for {symbol}, interval {interval_str}, limit {limit}")
            
            # Definiere die Kategorien, die wir durchprobieren wollen
            categories = ["spot", "linear"]
            
            for category in categories:
                try:
                    logger.info(f"Versuch mit Kategorie {category}")
                    
                    # API-Aufruf mit Fehlerbehandlung
                    print(f"Request URL: https://api.bybit.com/v5/market/kline")
                    print(f"Request params: {{'category': '{category}', 'symbol': '{symbol}', 'interval': '{interval_str}', 'limit': '{limit}'}}")
                    
                    klines = self.session.get_kline(
                        category=category,
                        symbol=symbol,
                        interval=interval_str,
                        limit=limit
                    )
                    
                    print(f"Response status code: {klines.get('retMsg', 'unknown')}")
                    print(f"Response retCode: {klines.get('retCode', -1)}")
                    
                    # Ueberpruefe API-Antwort
                    if klines.get('retCode') != 0:
                        logger.warning(f"API-Fehler: {klines.get('retMsg')} (Code: {klines.get('retCode')})")
                        continue
                    
                    # Ueberpruefe Datenstruktur
                    result = klines.get('result', {})
                    data_list = result.get('list', [])
                    
                    if not data_list:
                        logger.warning(f"Keine Daten fuer {category}/{symbol}/{interval_str}")
                        continue
                    
                    logger.info(f"Daten erhalten: {len(data_list)} Eintraege")
                    print(f"Received {len(data_list)} kline records")
                    
                    # Dynamische Spalten basierend auf der Anzahl der Elemente
                    base_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'turnover']
                    
                    # Pruefe, ob die Anzahl der Elemente passt
                    if len(data_list[0]) < 6:
                        logger.error(f"Unerwartetes Datenformat: {len(data_list[0])} Elemente (min. 6 erwartet)")
                        continue
                    
                    # Verwende nur so viele Spalten, wie wir Daten haben
                    columns = base_columns[:len(data_list[0])]
                    
                    # DataFrame erstellen
                    df = pd.DataFrame(data_list, columns=columns)
                    
                    if df.empty:
                        logger.warning(f"Leeres DataFrame fuer {category}")
                        continue
                    
                    # Convert data types with robust error handling
                    for col in ['open', 'high', 'low', 'close', 'volume']:
                        if col in df.columns:
                            df[col] = pd.to_numeric(df[col], errors='coerce')
                    
                    # Handle timestamp conversion safely
                    if 'timestamp' in df.columns:
                        try:
                            # Try different timestamp formats (ms or s)
                            if df['timestamp'].iloc[0] and len(str(df['timestamp'].iloc[0])) > 10:
                                # Milliseconds timestamp
                                df['timestamp'] = pd.to_datetime(df['timestamp'].astype('int64'), unit='ms')
                            else:
                                # Seconds timestamp
                                df['timestamp'] = pd.to_datetime(df['timestamp'].astype('int64'), unit='s')
                        except Exception as ts_err:
                            logger.warning(f"Timestamp-Konvertierungsfehler: {ts_err}")
                            # Try as string if numeric conversion fails
                            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
                    
                    # Sort and check for NaN values
                    if 'timestamp' in df.columns:
                        df = df.sort_values('timestamp')
                    
                    # Check for NaN values
                    nan_count = df.isnull().sum().sum()
                    if nan_count > 0:
                        logger.warning(f"DataFrame enthaelt {nan_count} NaN-Werte")
                        df = df.dropna()
                    
                    # Verify we have enough valid data
                    if len(df) < 5:
                        logger.warning(f"Zu wenig gueltige Daten: nur {len(df)} Eintraege nach Bereinigung")
                        continue
                    
                    logger.info(f"Erfolgreich {len(df)} Kerzen fuer {category} geladen")
                    print(f"Successfully processed {len(df)} kline records for {symbol}")
                    print(f"First row: {df.iloc[0]['timestamp']} - Open: {df.iloc[0]['open']}, Close: {df.iloc[0]['close']}")
                    print(f"Last row: {df.iloc[-1]['timestamp']} - Open: {df.iloc[-1]['open']}, Close: {df.iloc[-1]['close']}")
                    
                    return df
                
                except Exception as cat_error:
                    logger.error(f"Fehler mit Kategorie {category}: {str(cat_error)}")
                    print(f"[ERROR] Fehler mit Kategorie {category}: {str(cat_error)}")
                    continue
            
            logger.error("Keine gueltigen Daten fuer irgendeine Kategorie gefunden")
            return None
            
        except Exception as e:
            logger.error(f"Kritischer Fehler in get_market_data: {str(e)}")
            print(f"[ERROR] Kritischer Fehler in get_market_data: {str(e)}")
            return None
    
    def get_orderbook(self, symbol="BTCUSDT"):
        """Get current orderbook"""
        try:
            orderbook = self.session.get_orderbook(
                category="spot",
                symbol=symbol
            )
            return orderbook['result'] if orderbook['retCode'] == 0 else None
        except Exception as e:
            print(f"[ERROR] Error fetching orderbook: {e}")
            return None
    
    def get_recent_trades(self, symbol="BTCUSDT", limit=50):
        """Get recent public trades"""
        try:
            trades = self.session.get_public_trade_history(
                category="spot",
                symbol=symbol,
                limit=limit
            )
            return trades['result']['list'] if trades['retCode'] == 0 else []
        except Exception as e:
            print(f"[ERROR] Error fetching recent trades: {e}")
            return []
    
    def get_account_balance(self, account_type="UNIFIED"):
        """Get account balance"""
        try:
            balance = self.session.get_wallet_balance(
                accountType=account_type,
                coin="USDT"
            )
            if balance['retCode'] == 0 and 'list' in balance['result'] and balance['result']['list']:
                return float(balance['result']['list'][0]['totalEquity'])
            return 0.0
        except Exception as e:
            print(f"[ERROR] Error fetching account balance: {e}")
            return 0.0
""")
        print("[OK] bybit_client.py ohne Kodierungsprobleme geschrieben")
    except Exception as e:
        print("[ERROR] Fehler beim Schreiben von bybit_client.py:", str(e))
    
    # 3. Erstelle einen Test-Wrapper fuer das Dashboard
    print("\n[STEP 3] Erstelle Test-Wrapper fuer das Dashboard")
    test_wrapper_path = os.path.join(project_dir, "start_dashboard_fixed.py")
    
    try:
        with open(test_wrapper_path, 'w', encoding='utf-8') as f:
            f.write("""#!/usr/bin/env python
# -*- coding: utf-8 -*-

\"\"\"
Dashboard Test Wrapper
Startet das Dashboard mit importiertem BybitClient
\"\"\"

import os
import sys
import importlib

# Pfad zum Projekt-Verzeichnis hinzufuegen
project_dir = r"J:\Meine Ablage\CodingStuff\crypto-bot_V2"
sys.path.append(project_dir)

def test_bybit_client():
    \"\"\"Testet den BybitClient vor dem Starten des Dashboards\"\"\"
    print("\\n[INFO] Teste BybitClient...")
    
    try:
        # Importiere den BybitClient
        from trading.bybit_client import BybitClient
        
        # Teste mit Beispiel-Aufruf
        client = BybitClient()
        data = client.get_market_data(symbol="BTCUSDT", interval=5, limit=10)
        
        if data is not None:
            print("[OK] BybitClient funktioniert korrekt!")
            print(f"[INFO] {len(data)} Kerzen geladen.")
            return True
        else:
            print("[WARN] BybitClient gibt None zurueck.")
            return False
    except Exception as e:
        print("[ERROR] Fehler beim Testen des BybitClient:", str(e))
        return False

def start_dashboard():
    \"\"\"Startet das Dashboard\"\"\"
    print("\\n[INFO] Starte Dashboard...")
    
    # Setze Umgebungsvariablen fuer streamlit
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    
    try:
        # Importiere streamlit
        import streamlit
        
        # Pfad zum Dashboard
        dashboard_path = os.path.join(project_dir, "monitoring", "enhanced_smart_money_bot_dashboard.py")
        
        if os.path.exists(dashboard_path):
            print("[INFO] Dashboard-Pfad gefunden:", dashboard_path)
            print("[INFO] Starte Dashboard mit streamlit...")
            
            # Starte das Dashboard mit streamlit
            os.chdir(os.path.dirname(dashboard_path))
            os.system(f"{sys.executable} -m streamlit run {os.path.basename(dashboard_path)}")
        else:
            print("[ERROR] Dashboard-Datei nicht gefunden:", dashboard_path)
    except Exception as e:
        print("[ERROR] Fehler beim Starten des Dashboards:", str(e))

if __name__ == "__main__":
    print("===== DASHBOARD TEST WRAPPER =====")
    
    # Teste BybitClient
    client_ok = test_bybit_client()
    
    if client_ok:
        # Starte Dashboard
        start_dashboard()
    else:
        print("\\n[WARN] BybitClient funktioniert nicht korrekt. Das Dashboard wird moeglicherweise nicht richtig funktionieren.")
        
        # Frage, ob Dashboard trotzdem gestartet werden soll
        choice = input("Dashboard trotzdem starten? (j/n): ")
        if choice.lower() == 'j':
            start_dashboard()
        else:
            print("[INFO] Dashboard-Start abgebrochen.")
""")
        print("[OK] Test-Wrapper fuer das Dashboard erstellt")
    except Exception as e:
        print("[ERROR] Fehler beim Erstellen des Test-Wrappers:", str(e))
    
    # 4. Erstelle eine Batch-Datei zum einfachen Starten
    print("\n[STEP 4] Erstelle Batch-Datei zum Starten des Dashboards")
    batch_path = os.path.join(project_dir, "START_DASHBOARD_FIXED.bat")
    
    try:
        with open(batch_path, 'w', encoding='utf-8') as f:
            f.write("""@echo off
REM Start-Script fuer das fixierte Dashboard

echo ===== DASHBOARD STARTER =====
echo.

REM Setze Umgebungsvariablen
set PYTHONIOENCODING=utf-8

REM Aktiviere conda-Umgebung
call conda activate crypto-bot_V2

REM Starte das Dashboard
python "J:\\Meine Ablage\\CodingStuff\\crypto-bot_V2\\start_dashboard_fixed.py"

pause
""")
        print("[OK] Batch-Datei zum Starten des Dashboards erstellt")
    except Exception as e:
        print("[ERROR] Fehler beim Erstellen der Batch-Datei:", str(e))
    
    # Zusammenfassung
    print("\n===== ZUSAMMENFASSUNG =====")
    print("1. pybit-Installation geprueft")
    print("2. bybit_client.py ohne Kodierungsprobleme erstellt")
    print("3. Test-Wrapper fuer das Dashboard erstellt")
    print("4. Batch-Datei zum Starten des Dashboards erstellt")
    
    print("\nStarten Sie das Dashboard mit:")
    print(f"  {batch_path}")
    print("\nBei Problemen kann das Backup aus dem Ordner wiederhergestellt werden:")
    print(f"  {backup_dir}")

if __name__ == "__main__":
    fix_dashboard_issues()
