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
                    logger.info(f"Verwende Spalten: {columns}")
                    
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
            
            if orderbook['retCode'] == 0 and 'result' in orderbook:
                return orderbook['result']
            else:
                logger.warning(f"Fehler beim Abrufen des Orderbuchs: {orderbook.get('retMsg', 'Unbekannter Fehler')}")
                return None
        except Exception as e:
            logger.error(f"Error fetching orderbook: {e}")
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
            
            if trades['retCode'] == 0 and 'result' in trades and 'list' in trades['result']:
                return trades['result']['list']
            else:
                logger.warning(f"Fehler beim Abrufen der letzten Trades: {trades.get('retMsg', 'Unbekannter Fehler')}")
                return []
        except Exception as e:
            logger.error(f"Error fetching recent trades: {e}")
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
            logger.error(f"Error fetching account balance: {e}")
            print(f"[ERROR] Error fetching account balance: {e}")
            return 0.0