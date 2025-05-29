from pybit.unified_trading import HTTP
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
            # Konvertiere interval in den passenden String für die API
            # Spezialfall für Tages-Intervall: 1440 oder "D"
            if interval == 1440 or interval == "1440":
                interval_str = "D"
            else:
                interval_str = str(interval)
            
            logger.info(f"Abrufen von Kerzen für {symbol}, Intervall {interval_str}, Limit {limit}")
            
            # Definiere die Kategorien, die wir durchprobieren wollen
            categories = ["spot", "linear"]
            
            for category in categories:
                try:
                    logger.info(f"Versuch mit Kategorie {category}")
                    
                    # API-Aufruf mit Fehlerbehandlung
                    klines = self.session.get_kline(
                        category=category,
                        symbol=symbol,
                        interval=interval_str,
                        limit=limit
                    )
                    
                    # Überprüfe API-Antwort
                    if klines.get('retCode') != 0:
                        logger.warning(f"API-Fehler: {klines.get('retMsg')} (Code: {klines.get('retCode')})")
                        continue
                    
                    # Überprüfe Datenstruktur
                    result = klines.get('result', {})
                    data_list = result.get('list', [])
                    
                    if not data_list:
                        logger.warning(f"Keine Daten für {category}/{symbol}/{interval_str}")
                        continue
                    
                    logger.info(f"Daten erhalten: {len(data_list)} Einträge")
                    
                    # Untersuche Datenformat - Bybit gibt manchmal unterschiedliche Formate zurück
                    sample_item = data_list[0]
                    logger.info(f"Beispiel-Element: {sample_item}")
                    
                    # Dynamische Spalten basierend auf der Anzahl der Elemente
                    base_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'turnover']
                    
                    # Prüfe, ob die Anzahl der Elemente passt
                    if len(sample_item) < 6:
                        logger.error(f"Unerwartetes Datenformat: {len(sample_item)} Elemente (min. 6 erwartet)")
                        continue
                    
                    # Verwende nur so viele Spalten, wie wir Daten haben
                    columns = base_columns[:len(sample_item)]
                    logger.info(f"Verwende Spalten: {columns}")
                    
                    # DataFrame erstellen
                    df = pd.DataFrame(data_list, columns=columns)
                    
                    if df.empty:
                        logger.warning(f"Leeres DataFrame für {category}")
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
                        logger.warning(f"DataFrame enthält {nan_count} NaN-Werte")
                        df = df.dropna()
                    
                    # Verify we have enough valid data
                    if len(df) < 5:
                        logger.warning(f"Zu wenig gültige Daten: nur {len(df)} Einträge nach Bereinigung")
                        continue
                    
                    logger.info(f"Erfolgreich {len(df)} Kerzen für {category} geladen")
                    
                    # Debug: Zeige die ersten Zeilen des DataFrames
                    logger.info(f"DataFrame Preview:\n{df.head(2)}")
                    
                    return df
                
                except Exception as cat_error:
                    logger.error(f"Fehler mit Kategorie {category}: {str(cat_error)}")
                    continue
            
            logger.error("Keine gültigen Daten für irgendeine Kategorie gefunden")
            return None
            
        except Exception as e:
            logger.error(f"Kritischer Fehler in get_market_data: {str(e)}")
            return None