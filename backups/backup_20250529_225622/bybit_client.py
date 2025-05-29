from pybit.unified_trading import HTTP
import pandas as pd
from datetime import datetime, timedelta
import time

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
    
    def get_market_data(self, symbol="BTCUSDT", interval=5, limit=200):
        """Get kline/candlestick data"""
        try:
            # Konvertiere interval in den passenden String für die API
            interval_str = str(interval)
            
            # Definiere die Kategorien, die wir durchprobieren wollen
            categories = ["spot", "linear"]
            
            for category in categories:
                try:
                    print(f"Versuch mit Kategorie {category} für {symbol}, Intervall {interval_str}, Limit {limit}")
                    
                    klines = self.session.get_kline(
                        category=category,
                        symbol=symbol,
                        interval=interval_str,
                        limit=limit
                    )
                    
                    print(f"API Response: {klines}")
                    
                    if klines.get('retCode') == 0 and klines.get('result', {}).get('list'):
                        df = pd.DataFrame(
                            klines['result']['list'],
                            columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'turnover']
                        )
                        
                        if df.empty:
                            print(f"Leeres DataFrame für {category}")
                            continue
                            
                        # Convert data types
                        for col in ['open', 'high', 'low', 'close', 'volume']:
                            df[col] = pd.to_numeric(df[col], errors='coerce')
                        
                        df['timestamp'] = pd.to_datetime(df['timestamp'].astype('int64'), unit='ms')
                        df = df.sort_values('timestamp')
                        
                        # Überprüfe auf NaN-Werte
                        if df.isnull().values.any():
                            print("Warnung: DataFrame enthält NaN-Werte")
                            df = df.dropna()
                        
                        print(f"Erfolgreich {len(df)} Kerzen für {category} geladen")
                        return df
                    else:
                        print(f"Keine gültigen Daten in der Antwort für {category}")
                        
                except Exception as cat_error:
                    print(f"Fehler mit Kategorie {category}: {str(cat_error)}")
                    continue
            
            print("Keine gültigen Daten für irgendeine Kategorie gefunden")
            return None
            
        except Exception as e:
            print(f"Kritischer Fehler in get_market_data: {str(e)}")
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
            print(f"Error fetching orderbook: {e}")
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
            print(f"Error fetching recent trades: {e}")
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
            print(f"Error fetching account balance: {e}")
            return 0.0
