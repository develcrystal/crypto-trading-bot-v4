"""
Unified API Client für den Crypto Trading Bot V2.

Diese Datei stellt eine zentrale, vereinheitlichte API-Schnittstelle für die 
Kommunikation mit der Bybit Börse bereit.
"""

import hmac
import hashlib
import time
import json
import logging
import requests
from typing import Dict, List, Optional, Union, Any
import urllib.parse
import os
from datetime import datetime
from dotenv import load_dotenv

# Lade Umgebungsvariablen
load_dotenv()

# Konfiguriere Logging
logger = logging.getLogger(__name__)

class BybitAPIClient:
    """
    Vereinheitlichte Bybit API-Integration für den Crypto Trading Bot.
    
    Diese Klasse stellt Funktionen für die Kommunikation mit der Bybit API bereit,
    einschließlich Marktdatenabruf, Account-Informationen und Handelsausführung.
    """
    
    def __init__(self, api_key: str = None, api_secret: str = None, testnet: bool = None):
        """
        Initialisiere die Bybit API-Integration.
        
        Args:
            api_key: API-Schlüssel für Bybit (optional, sonst aus .env)
            api_secret: API-Secret für Bybit (optional, sonst aus .env)
            testnet: Ob Testnet oder Mainnet verwendet werden soll (optional, sonst aus .env)
        """
        # Wenn nicht explizit angegeben, lade aus Umgebungsvariablen
        self.api_key = api_key or os.getenv('BYBIT_API_KEY')
        self.api_secret = api_secret or os.getenv('BYBIT_API_SECRET')
        
        # Wenn testnet nicht explizit angegeben, lade aus Umgebungsvariablen
        if testnet is None:
            testnet_env = os.getenv('TESTNET', 'false').lower()
            self.testnet = testnet_env in ('true', '1', 'yes')
        else:
            self.testnet = testnet
        
        # Basis-URLs basierend auf Testnet/Mainnet
        if self.testnet:
            self.base_url = "https://api-testnet.bybit.com"
            self.ws_url = "wss://stream-testnet.bybit.com"
        else:
            self.base_url = "https://api.bybit.com"
            self.ws_url = "wss://stream.bybit.com"
        
        # Standardwerte für API-Anfragen
        self.recv_window = 5000
            
        logger.info(f"BybitAPIClient initialisiert. API Key: {self.api_key[:8] if self.api_key else 'MISSING'}...")
        logger.info(f"Testnet: {self.testnet} | Base URL: {self.base_url}")
    
    def generate_signature(self, timestamp: str, payload: str) -> str:
        """
        Generiert die HMAC-SHA256-Signatur für API-Anfragen im V5-Format.
        
        Args:
            timestamp: Zeitstempel in Millisekunden
            payload: Parameter-String oder JSON-Payload
            
        Returns:
            Generierte Signatur
        """
        param_str = str(timestamp) + self.api_key + str(self.recv_window) + payload
        
        signature = hmac.new(
            bytes(self.api_secret, "utf-8"), 
            param_str.encode("utf-8"), 
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def make_request(self, method: str, endpoint: str, params: Dict = None, json_data: Dict = None) -> Dict:
        """
        Führt eine HTTP-Anfrage an die Bybit API aus.
        
        Args:
            method: HTTP-Methode (GET, POST, etc.)
            endpoint: API-Endpunkt
            params: Query-Parameter für GET-Anfragen
            json_data: JSON-Daten für POST-Anfragen
            
        Returns:
            API-Antwort als Dictionary
        """
        # Parameter initialisieren
        params = params or {}
        payload = ""
        
        # Bei POST-Anfragen mit JSON-Daten
        if json_data:
            payload = json.dumps(json_data, separators=(',', ':'))
        elif params and method.upper() == 'GET':
            # Bei GET-Anfragen mit Parametern
            payload = urllib.parse.urlencode(params)
        
        # Signatur erstellen
        timestamp = str(int(time.time() * 1000))
        signature = self.generate_signature(timestamp, payload)
        
        # Headers erstellen
        headers = {
            'X-BAPI-API-KEY': self.api_key,
            'X-BAPI-SIGN': signature,
            'X-BAPI-SIGN-TYPE': '2',
            'X-BAPI-TIMESTAMP': timestamp,
            'X-BAPI-RECV-WINDOW': str(self.recv_window),
            'Content-Type': 'application/json'
        }
        
        # URL zusammensetzen
        url = f"{self.base_url}{endpoint}"
        
        # Debug-Informationen
        logger.debug(f"Sending {method} request to {url}")
        if params:
            logger.debug(f"Params: {params}")
        if json_data:
            logger.debug(f"JSON Data: {json_data}")
        
        try:
            # Anfrage senden
            if method.upper() == 'GET':
                response = requests.get(url, params=params, headers=headers, timeout=10)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, data=payload, timeout=10)
            else:
                logger.error(f"Nicht unterstützte HTTP-Methode: {method}")
                return {'success': False, 'error': f"Unsupported method: {method}"}
            
            # Debug-Informationen
            logger.debug(f"Response status: {response.status_code}")
            
            # Antwort verarbeiten
            if response.status_code == 200:
                data = response.json()
                
                # API-Struktur überprüfen
                if data.get('retCode') == 0:
                    # Erfolgreiche Anfrage
                    return {'success': True, 'data': data.get('result', {})}
                else:
                    # API-Fehler
                    error_msg = data.get('retMsg', 'Unknown API error')
                    logger.warning(f"API-Fehler: {error_msg}")
                    return {'success': False, 'error': error_msg, 'code': data.get('retCode')}
            else:
                # HTTP-Fehler
                logger.error(f"HTTP-Fehler: {response.status_code}, {response.text}")
                return {'success': False, 'error': f"HTTP Error: {response.status_code}"}
        except Exception as e:
            # Allgemeiner Fehler
            logger.error(f"Fehler bei API-Anfrage: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    # --- MARKET DATA METHODS ---
    
    def get_ticker(self, symbol: str = 'BTCUSDT') -> Dict:
        """
        Ruft aktuelle Ticker-Informationen für ein Symbol ab.
        
        Args:
            symbol: Handelssymbol (z.B. "BTCUSDT")
            
        Returns:
            Ticker-Informationen mit Preis, 24h Change, etc.
        """
        endpoint = "/v5/market/ticker"
        params = {
            'category': 'spot',
            'symbol': symbol
        }
        
        response = self.make_request('GET', endpoint, params=params)
        
        if response['success']:
            ticker_data = response['data']
            if 'list' in ticker_data and ticker_data['list']:
                ticker = ticker_data['list'][0]
                return {
                    'success': True,
                    'price': float(ticker.get('lastPrice', 0)),
                    'bid': float(ticker.get('bid1Price', 0)),
                    'ask': float(ticker.get('ask1Price', 0)),
                    'volume_24h': float(ticker.get('volume24h', 0)),
                    'change_24h': float(ticker.get('price24hPcnt', 0)) * 100,
                    'high_24h': float(ticker.get('highPrice24h', 0)),
                    'low_24h': float(ticker.get('lowPrice24h', 0)),
                    'timestamp': datetime.now()
                }
        
        return {'success': False, 'error': response.get('error', 'No ticker data')}
    
    def get_kline_data(self, symbol: str = 'BTCUSDT', interval: str = '5', limit: int = 100) -> Dict:
        """
        Ruft Kerzenchartdaten (OHLCV) für ein Symbol ab.
        
        Args:
            symbol: Handelssymbol (z.B. "BTCUSDT")
            interval: Zeitintervall (z.B. "5" für 5 Minuten)
            limit: Maximale Anzahl von Datenpunkten
            
        Returns:
            Kerzenchartdaten als DataFrame
        """
        endpoint = "/v5/market/kline"
        params = {
            'category': 'spot',
            'symbol': symbol,
            'interval': interval,
            'limit': limit
        }
        
        response = self.make_request('GET', endpoint, params=params)
        
        if response['success']:
            data = response['data']
            if 'list' in data:
                import pandas as pd
                
                # Convert API response to DataFrame
                klines = data['list']
                df = pd.DataFrame(klines, columns=[
                    'timestamp', 'open', 'high', 'low', 'close', 'volume', 'turnover'
                ])
                
                # Convert types
                df['timestamp'] = pd.to_datetime(df['timestamp'].astype(int), unit='ms')
                for col in ['open', 'high', 'low', 'close', 'volume', 'turnover']:
                    df[col] = df[col].astype(float)
                
                # Sort by timestamp
                df = df.sort_values('timestamp').reset_index(drop=True)
                
                return {'success': True, 'data': df}
        
        return {'success': False, 'error': response.get('error', 'No kline data')}
    
    def get_order_book(self, symbol: str = 'BTCUSDT', limit: int = 10) -> Dict:
        """
        Ruft das aktuelle Orderbuch für ein Symbol ab.
        
        Args:
            symbol: Handelssymbol (z.B. "BTCUSDT")
            limit: Tiefe des Orderbuchs
            
        Returns:
            Orderbuch-Daten mit Bids und Asks
        """
        endpoint = "/v5/market/orderbook"
        params = {
            'category': 'spot',
            'symbol': symbol,
            'limit': limit
        }
        
        response = self.make_request('GET', endpoint, params=params)
        
        if response['success']:
            book = response['data']
            return {
                'success': True,
                'bids': [[float(x[0]), float(x[1])] for x in book.get('b', [])],
                'asks': [[float(x[0]), float(x[1])] for x in book.get('a', [])],
                'timestamp': datetime.now(),
                'symbol': symbol
            }
        
        return {'success': False, 'error': response.get('error', 'No orderbook data')}
    
    # --- ACCOUNT DATA METHODS ---
    
    def get_wallet_balance(self) -> Dict:
        """
        Ruft den aktuellen Wallet-Kontostand ab.
        
        Returns:
            Wallet-Informationen mit Balances für alle Coins
        """
        endpoint = "/v5/account/wallet-balance"
        params = {
            'accountType': 'UNIFIED'
        }
        
        response = self.make_request('GET', endpoint, params=params)
        
        if response['success']:
            data = response['data']
            if 'list' in data and data['list']:
                account = data['list'][0]
                coins = account.get('coin', [])
                
                balances = {}
                total_usdt_value = 0
                
                for coin in coins:
                    balance = float(coin.get('walletBalance', 0))
                    if balance > 0:
                        balances[coin['coin']] = balance
                        
                        # Berechne USD-Wert
                        if coin['coin'] == 'USDT':
                            total_usdt_value += balance
                        elif coin['coin'] == 'BTC' and balance > 0:
                            # Hole BTC-Preis für die Berechnung
                            btc_ticker = self.get_ticker('BTCUSDT')
                            if btc_ticker['success']:
                                btc_price = btc_ticker['price']
                                total_usdt_value += balance * btc_price
                
                return {
                    'success': True,
                    'balances': balances,
                    'total_usdt_value': total_usdt_value,
                    'account_type': 'TESTNET' if self.testnet else 'MAINNET'
                }
        
        return {'success': False, 'error': response.get('error', 'No wallet data')}
    
    # --- TRADING METHODS ---
    
    def place_order(self, symbol: str, side: str, order_type: str, qty: float, price: float = None) -> Dict:
        """
        Platziert eine Handelsorder.
        
        Args:
            symbol: Handelssymbol (z.B. "BTCUSDT")
            side: Orderrichtung ("Buy" oder "Sell")
            order_type: Ordertyp ("Market" oder "Limit")
            qty: Ordermenge
            price: Orderpreis (nur für Limit-Orders)
            
        Returns:
            Order-Informationen
        """
        endpoint = "/v5/order/create"
        
        order_data = {
            'category': 'spot',
            'symbol': symbol,
            'side': side,
            'orderType': order_type,
            'qty': str(qty)
        }
        
        if price and order_type.lower() == 'limit':
            order_data['price'] = str(price)
            order_data['timeInForce'] = 'GTC'
        
        response = self.make_request('POST', endpoint, json_data=order_data)
        
        if response['success']:
            order_id = response['data'].get('orderId')
            return {
                'success': True,
                'order_id': order_id,
                'symbol': symbol,
                'side': side,
                'qty': qty,
                'price': price if price else 'Market',
                'timestamp': datetime.now()
            }
        
        return {'success': False, 'error': response.get('error', 'Order placement failed')}
    
    def cancel_order(self, symbol: str, order_id: str) -> Dict:
        """
        Storniert eine offene Order.
        
        Args:
            symbol: Handelssymbol
            order_id: Order-ID
            
        Returns:
            Stornierungsstatus
        """
        endpoint = "/v5/order/cancel"
        
        cancel_data = {
            'category': 'spot',
            'symbol': symbol,
            'orderId': order_id
        }
        
        response = self.make_request('POST', endpoint, json_data=cancel_data)
        
        if response['success']:
            return {
                'success': True,
                'order_id': order_id,
                'symbol': symbol,
                'timestamp': datetime.now()
            }
        
        return {'success': False, 'error': response.get('error', 'Order cancellation failed')}
    
    def get_open_orders(self, symbol: str = None) -> Dict:
        """
        Ruft alle offenen Orders ab.
        
        Args:
            symbol: Optionales Handelssymbol zum Filtern
            
        Returns:
            Liste von offenen Orders
        """
        endpoint = "/v5/order/realtime"
        
        params = {
            'category': 'spot'
        }
        
        if symbol:
            params['symbol'] = symbol
        
        response = self.make_request('GET', endpoint, params=params)
        
        if response['success']:
            orders_data = response['data']
            if 'list' in orders_data:
                return {
                    'success': True,
                    'orders': orders_data['list']
                }
        
        return {'success': False, 'error': response.get('error', 'No open orders data')}
    
    # --- CONVENIENCE METHODS ---
    
    def get_dashboard_data(self) -> Dict:
        """
        Liefert alle wichtigen Daten für das Dashboard.
        
        Returns:
            Kombinierte Daten für Portfolio, BTC-Preis, etc.
        """
        # Get wallet balance
        balance_data = self.get_wallet_balance()
        
        # Get BTC ticker data
        ticker_data = self.get_ticker('BTCUSDT')
        
        if balance_data['success'] and ticker_data['success']:
            return {
                'success': True,
                'portfolio_value': balance_data['total_usdt_value'],
                'balances': balance_data['balances'],
                'btc_price': ticker_data['price'],
                'btc_change_24h': ticker_data['change_24h'],
                'btc_high_24h': ticker_data['high_24h'],
                'btc_low_24h': ticker_data['low_24h'],
                'btc_volume_24h': ticker_data['volume_24h'],
                'account_type': balance_data['account_type'],
            }
        else:
            return {
                'success': False,
                'error': balance_data.get('error') or ticker_data.get('error'),
                'balance_error': balance_data.get('error', ''),
                'ticker_error': ticker_data.get('error', '')
            }

# Test function
def test_api_client():
    """
    Testet die API-Client Verbindung und Funktionen.
    """
    api = BybitAPIClient()
    
    print("=" * 50)
    print("TESTING BYBIT API CLIENT")
    print("=" * 50)
    print(f"API Base URL: {api.base_url}")
    print(f"Testnet Mode: {api.testnet}")
    print("-" * 50)
    
    # Test ticker data
    print("\nTesting Ticker Data:")
    ticker = api.get_ticker("BTCUSDT")
    if ticker['success']:
        print(f"BTC Price: ${ticker['price']:,.2f}")
        print(f"24h Change: {ticker['change_24h']:+.2f}%")
        print(f"24h Volume: {ticker['volume_24h']:,.2f} BTC")
    else:
        print(f"Ticker Error: {ticker.get('error', 'Unknown')}")
    
    # Test wallet balance
    print("\nTesting Wallet Balance:")
    balance = api.get_wallet_balance()
    if balance['success']:
        print(f"Total USDT Value: ${balance['total_usdt_value']:,.2f}")
        print("Balances:")
        for coin, amount in balance['balances'].items():
            if coin == 'USDT':
                print(f"   {coin}: {amount:.2f}")
            else:
                print(f"   {coin}: {amount:.6f}")
    else:
        print(f"Balance Error: {balance.get('error', 'Unknown')}")
    
    # Test dashboard data
    print("\nTesting Dashboard Data:")
    dashboard = api.get_dashboard_data()
    if dashboard['success']:
        print(f"Portfolio Value: ${dashboard['portfolio_value']:,.2f}")
        print(f"BTC Price: ${dashboard['btc_price']:,.2f}")
        print(f"Account Type: {dashboard['account_type']}")
    else:
        print(f"Dashboard Error: {dashboard.get('error', 'Unknown')}")
    
    print("=" * 50)

if __name__ == "__main__":
    # Setup basic logging
    logging.basicConfig(level=logging.INFO)
    
    # Test the API client
    test_api_client()
