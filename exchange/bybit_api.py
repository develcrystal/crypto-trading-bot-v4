"""
Exchange-Integrationsmodul für den Crypto Trading Bot V2.

Dieses Modul stellt Funktionen für die Kommunikation mit verschiedenen
Kryptowährungsbörsen bereit, mit Fokus auf Bybit.
"""

import hmac
import hashlib
import time
import json
import logging
import requests
from typing import Dict, List, Optional, Union, Any
import urllib.parse
from datetime import datetime

# Konfiguriere Logging
logger = logging.getLogger(__name__)

class BybitAPI:
    """
    Implementierung der Bybit API für den Crypto Trading Bot.
    
    Diese Klasse stellt Funktionen für die Kommunikation mit der Bybit API bereit,
    einschließlich Marktdatenabruf und Handelsausführung.
    """
    
    def __init__(self, api_key: str = None, api_secret: str = None, 
               testnet: bool = True):
        """
        Initialisiere die Bybit API-Integration.
        
        Args:
            api_key: API-Schlüssel für Bybit
            api_secret: API-Secret für Bybit
            testnet: Ob Testnet oder Mainnet verwendet werden soll
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        
        # Basis-URLs basierend auf Testnet/Mainnet
        if testnet:
            # Testnet URLs
            self.base_url = "https://api-testnet.bybit.com"
            self.ws_url = "wss://stream-testnet.bybit.com"
        else:
            # MAINNET URLs (für echte Trades)
            self.base_url = "https://api.bybit.com"
            self.ws_url = "wss://stream.bybit.com"
            
        logger.info(f"BybitAPI initialisiert. Testnet: {testnet}")
    
    def _generate_signature(self, params: Dict) -> str:
        """
        Generiert die HMAC-SHA256-Signatur für API-Anfragen.
        
        Args:
            params: Parameter für die API-Anfrage
            
        Returns:
            Generierte Signatur
        """
        # Sortierte Parameter-Strings erstellen
        param_str = urllib.parse.urlencode(dict(sorted(params.items())))
        
        # HMAC-SHA256-Signatur erstellen
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            param_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def _add_auth_params(self, params: Dict) -> Dict:
        """
        Fügt Authentifizierungsparameter zu API-Anfragen hinzu.
        
        Args:
            params: Ursprüngliche Parameter
            
        Returns:
            Parameter mit Authentifizierungsinformationen
        """
        if not self.api_key or not self.api_secret:
            logger.warning("API-Schlüssel oder -Secret nicht konfiguriert")
            return params
        
        # Timestamp und API-Schlüssel hinzufügen
        params['api_key'] = self.api_key
        params['timestamp'] = str(int(time.time() * 1000))
        params['recv_window'] = '5000'
        
        # Signatur generieren und hinzufügen
        params['sign'] = self._generate_signature(params)
        
        return params
    
    def _make_request(self, method: str, endpoint: str, params: Dict = None, 
                    auth: bool = False) -> Dict:
        """
        Führt eine HTTP-Anfrage an die Bybit API aus.
        
        Args:
            method: HTTP-Methode (GET, POST, etc.)
            endpoint: API-Endpunkt
            params: Anfrageparameter
            auth: Ob Authentifizierung erforderlich ist
            
        Returns:
            API-Antwort als Dictionary
        """
        # Parameter initialisieren
        params = params or {}
        
        # URL zusammensetzen
        url = f"{self.base_url}{endpoint}"
        
        # Authentifizierung hinzufügen, wenn erforderlich
        if auth:
            params = self._add_auth_params(params)
        
        # Debug-Informationen
        logger.debug(f"Sending {method} request to {url}")
        logger.debug(f"Params: {params}")
        
        try:
            # Anfrage senden
            if method.upper() == 'GET':
                response = requests.get(url, params=params)
            elif method.upper() == 'POST':
                response = requests.post(url, json=params)
            else:
                logger.error(f"Nicht unterstützte HTTP-Methode: {method}")
                return {'error': f"Unsupported method: {method}"}
            
            # Debug-Informationen
            logger.debug(f"Response status: {response.status_code}")
            logger.debug(f"Response headers: {response.headers}")
            
            # Antwort verarbeiten
            if response.status_code == 200:
                data = response.json()
                
                # API-Struktur überprüfen
                logger.debug(f"Response keys: {data.keys()}")
                
                # Fehlerbehandlung
                if data.get('retCode') != 0:
                    logger.warning(f"API-Fehler: {data.get('retMsg')}")
                
                return data
            else:
                logger.error(f"HTTP-Fehler: {response.status_code}, {response.text}")
                return {'error': f"HTTP Error: {response.status_code}"}
        except Exception as e:
            logger.error(f"Fehler bei API-Anfrage: {str(e)}")
            return {'error': str(e)}
    
    def get_historical_data(self, symbol: str, interval: str, 
                           start_time: int = None, end_time: int = None, 
                           limit: int = 200) -> List[Dict]:
        """
        Ruft historische Kline/Candlestick-Daten ab.
        
        Args:
            symbol: Handelssymbol (z.B. "BTCUSDT")
            interval: Zeitintervall (z.B. "1h", "1d")
            start_time: Startzeit in Millisekunden
            end_time: Endzeit in Millisekunden
            limit: Maximale Anzahl von Datenpunkten
            
        Returns:
            Liste von OHLCV-Daten
        """
        # Endpunkt für Kline-Daten
        endpoint = "/v5/market/kline"
        
        # Parameter zusammenstellen
        # Bybit API erwartet spezifische Intervall-Notationen
        interval_mapping = {
            '1m': '1',
            '3m': '3',
            '5m': '5',
            '15m': '15',
            '30m': '30',
            '1h': '60',
            '2h': '120',
            '4h': '240',
            '6h': '360',
            '12h': '720',
            '1d': 'D',
            '1w': 'W',
            '1M': 'M'
        }
        
        # Falls angefordertes Intervall nicht bekannt ist, Fallback auf Standard
        mapped_interval = interval_mapping.get(interval, interval)
        
        params = {
            'category': 'spot',
            'symbol': symbol,
            'interval': mapped_interval,
            'limit': str(limit)
        }
        
        logger.info(f"Anfrageparameter für historische Daten - Symbol: {symbol}, Intervall: {interval} (gemappt zu: {mapped_interval}), Limit: {limit}")
        
        # Zeitparameter hinzufügen, wenn vorhanden
        # Bybit erwartet Timestamps in Millisekunden, wir bekommen sie bereits in Millisekunden
        if start_time:
            params['start'] = str(int(start_time))
        if end_time:
            params['end'] = str(int(end_time))
        
        # API-Anfrage senden
        logger.info(f"Sending GET request to {self.base_url}{endpoint}")
        logger.info(f"Params: {params}")
        response = self._make_request('GET', endpoint, params)
        
        # API-Antwortstruktur überprüfen
        if response:
            logger.info(f"API Response: {response}")
            if isinstance(response, dict):
                logger.info(f"API Response structure: {response.keys()}")
            
        # Fehlerbehandlung
        if response and 'error' in response:
            logger.error(f"Fehler beim Abrufen historischer Daten: {response['error']}")
            return []
        
        # Daten aus der Antwort extrahieren
        if 'result' in response and 'list' in response['result']:
            data_list = response['result']['list']
            
            # Daten umformen für einfachere Verarbeitung
            formatted_data = []
            for item in data_list:
                # Bybit gibt Daten als Array zurück [timestamp, open, high, low, close, volume, ...]
                if isinstance(item, list) and len(item) >= 6:
                    formatted_data.append({
                        'timestamp': int(item[0]),
                        'open': float(item[1]),
                        'high': float(item[2]),
                        'low': float(item[3]),
                        'close': float(item[4]),
                        'volume': float(item[5])
                    })
                # Oder möglicherweise als Dictionary
                elif isinstance(item, dict):
                    formatted_data.append(item)
            
            return formatted_data
        else:
            logger.warning("Keine Daten in API-Antwort gefunden")
            return []
    
    def get_ticker(self, symbol: str) -> Dict:
        """
        Ruft aktuelle Ticker-Informationen für ein Symbol ab.
        
        Args:
            symbol: Handelssymbol (z.B. "BTCUSDT")
            
        Returns:
            Ticker-Informationen
        """
        endpoint = "/v5/market/ticker"
        params = {
            'category': 'spot',
            'symbol': symbol
        }
        
        response = self._make_request('GET', endpoint, params)
        
        if 'error' in response:
            logger.error(f"Fehler beim Abrufen von Ticker-Daten: {response['error']}")
            return {}
        
        if 'result' in response and 'list' in response['result']:
            ticker_list = response['result']['list']
            if ticker_list:
                return ticker_list[0]
        
        return {}
    
    def get_order_book(self, symbol: str, limit: int = 50) -> Dict:
        """
        Ruft das aktuelle Orderbuch für ein Symbol ab.
        
        Args:
            symbol: Handelssymbol (z.B. "BTCUSDT")
            limit: Tiefe des Orderbuchs
            
        Returns:
            Orderbuch-Daten
        """
        endpoint = "/v5/market/orderbook"
        params = {
            'category': 'spot',
            'symbol': symbol,
            'limit': str(limit)
        }
        
        response = self._make_request('GET', endpoint, params)
        
        if 'error' in response:
            logger.error(f"Fehler beim Abrufen des Orderbuchs: {response['error']}")
            return {'bids': [], 'asks': []}
        
        if 'result' in response:
            return response['result']
        
        return {'bids': [], 'asks': []}
    
    def get_wallet_balance(self) -> Dict:
        """
        Ruft den aktuellen Wallet-Kontostand ab.
        
        Returns:
            Wallet-Informationen
        """
        endpoint = "/v5/account/wallet-balance"
        params = {
            'accountType': 'SPOT'
        }
        
        response = self._make_request('GET', endpoint, params, auth=True)
        
        if 'error' in response:
            logger.error(f"Fehler beim Abrufen des Wallet-Kontostands: {response['error']}")
            return {}
        
        if 'result' in response and 'list' in response['result']:
            balance_list = response['result']['list']
            if balance_list:
                return balance_list[0]
        
        return {}
    
    def place_order(self, symbol: str, side: str, order_type: str, 
                  qty: float, price: float = None, time_in_force: str = 'GTC') -> Dict:
        """
        Platziert eine Handelsorder.
        
        Args:
            symbol: Handelssymbol (z.B. "BTCUSDT")
            side: Orderrichtung ("Buy" oder "Sell")
            order_type: Ordertyp ("Market" oder "Limit")
            qty: Ordermenge
            price: Orderpreis (nur für Limit-Orders)
            time_in_force: Zeitbeschränkung der Order
            
        Returns:
            Order-Informationen
        """
        endpoint = "/v5/order/create"
        
        params = {
            'category': 'spot',
            'symbol': symbol,
            'side': side,
            'orderType': order_type,
            'qty': str(qty),
            'timeInForce': time_in_force
        }
        
        # Preis hinzufügen für Limit-Orders
        if order_type.lower() == 'limit' and price is not None:
            params['price'] = str(price)
        
        response = self._make_request('POST', endpoint, params, auth=True)
        
        if 'error' in response:
            logger.error(f"Fehler beim Platzieren der Order: {response['error']}")
            return {'success': False, 'error': response['error']}
        
        if response.get('retCode') == 0:
            return {'success': True, 'order_id': response.get('result', {}).get('orderId')}
        else:
            return {'success': False, 'error': response.get('retMsg')}
    
    def cancel_order(self, symbol: str, order_id: str = None) -> Dict:
        """
        Storniert eine offene Order.
        
        Args:
            symbol: Handelssymbol
            order_id: Order-ID
            
        Returns:
            Stornierungsstatus
        """
        endpoint = "/v5/order/cancel"
        
        params = {
            'category': 'spot',
            'symbol': symbol
        }
        
        if order_id:
            params['orderId'] = order_id
        
        response = self._make_request('POST', endpoint, params, auth=True)
        
        if 'error' in response:
            logger.error(f"Fehler beim Stornieren der Order: {response['error']}")
            return {'success': False, 'error': response['error']}
        
        if response.get('retCode') == 0:
            return {'success': True}
        else:
            return {'success': False, 'error': response.get('retMsg')}
    
    def get_open_orders(self, symbol: str = None) -> List[Dict]:
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
        
        response = self._make_request('GET', endpoint, params, auth=True)
        
        if 'error' in response:
            logger.error(f"Fehler beim Abrufen offener Orders: {response['error']}")
            return []
        
        if 'result' in response and 'list' in response['result']:
            return response['result']['list']
        
        return []
    
    def get_order_history(self, symbol: str = None, limit: int = 50) -> List[Dict]:
        """
        Ruft den Orderverlauf ab.
        
        Args:
            symbol: Optionales Handelssymbol zum Filtern
            limit: Maximale Anzahl von Ergebnissen
            
        Returns:
            Liste von historischen Orders
        """
        endpoint = "/v5/order/history"
        
        params = {
            'category': 'spot',
            'limit': str(limit)
        }
        
        if symbol:
            params['symbol'] = symbol
        
        response = self._make_request('GET', endpoint, params, auth=True)
        
        if 'error' in response:
            logger.error(f"Fehler beim Abrufen des Orderverlaufs: {response['error']}")
            return []
        
        if 'result' in response and 'list' in response['result']:
            return response['result']['list']
        
        return []

# Beispiel für die Verwendung
if __name__ == "__main__":
    # Konfiguriere Logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # API-Instanz erstellen (für Testnet)
    bybit = BybitAPI(testnet=True)
    
    # Historische Daten abrufen
    data = bybit.get_historical_data(
        symbol="BTCUSDT",
        interval="1h",
        limit=10
    )
    
    print(f"Historical data: {data}")
