#!/usr/bin/env python
"""
100% KORREKTE BYBIT V5 API IMPLEMENTIERUNG
Basierend auf aktueller offizieller Dokumentation und funktionierenden Beispielen
"""

import os
import sys
import time
import logging
import requests
import hmac
import hashlib
import json
from datetime import datetime
from dotenv import load_dotenv

# Environment laden
load_dotenv()

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('correct_bybit_api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CorrectBybitAPI:
    """100% korrekte Bybit V5 API Implementierung"""
    
    def __init__(self):
        # API Credentials aus .env
        self.api_key = os.getenv('BYBIT_API_KEY')
        self.api_secret = os.getenv('BYBIT_API_SECRET')
        self.base_url = "https://api-testnet.bybit.com"
        self.recv_window = '5000'
        
        if not self.api_key or not self.api_secret:
            raise ValueError("BYBIT_API_KEY and BYBIT_API_SECRET must be set in .env file")
        
        logger.info("Correct Bybit V5 API initialisiert")
        logger.info(f"API Key: {self.api_key}")
        logger.info(f"API Secret: {self.api_secret[:8]}...")
    
    def generate_signature(self, timestamp, recv_window, payload):
        """
        Generiert 100% korrekte Bybit V5 API Signature
        Exakte Implementierung laut offizieller Dokumentation
        
        Format: timestamp + api_key + recv_window + payload
        """
        # Exakte String-Zusammensetzung wie in Bybit Docs
        param_str = str(timestamp) + self.api_key + str(recv_window) + str(payload)
        
        logger.debug(f"Signature string: '{param_str}'")
        
        # HMAC SHA256 mit Secret Key
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            param_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        logger.debug(f"Generated signature: {signature}")
        return signature
    
    def make_authenticated_request(self, method, endpoint, params=None, json_data=None):
        """
        Macht authentifizierten Request mit korrekten V5 Headers
        """
        # Timestamp generieren (in Millisekunden)
        timestamp = int(time.time() * 1000)
        
        # URL konstruieren
        url = f"{self.base_url}{endpoint}"
        
        # Payload für Signature bestimmen
        if method.upper() == 'GET':
            # GET Request: Query Parameters als String
            if params:
                # Parameter sortieren und als query string formatieren
                query_pairs = []
                for key in sorted(params.keys()):
                    query_pairs.append(f"{key}={params[key]}")
                query_string = "&".join(query_pairs)
                payload = query_string
                url += f"?{query_string}"
            else:
                payload = ""
        else:
            # POST Request: JSON Body als String
            if json_data:
                payload = json.dumps(json_data, separators=(',', ':'))
            else:
                payload = ""
        
        # Signature generieren
        signature = self.generate_signature(timestamp, self.recv_window, payload)
        
        # Offizielle V5 API Headers
        headers = {
            'X-BAPI-API-KEY': self.api_key,
            'X-BAPI-SIGN': signature,
            'X-BAPI-SIGN-TYPE': '2',
            'X-BAPI-TIMESTAMP': str(timestamp),
            'X-BAPI-RECV-WINDOW': self.recv_window,
            'Content-Type': 'application/json'
        }
        
        logger.info(f"Request: {method} {endpoint}")
        logger.debug(f"Timestamp: {timestamp}")
        logger.debug(f"Payload: '{payload}'")
        logger.debug(f"Headers: {headers}")
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, data=payload if payload else None, timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            logger.info(f"Response: {response.status_code}")
            logger.debug(f"Response text: {response.text}")
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"HTTP Error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Request failed: {e}")
            return None
    
    def get_account_balance(self):
        """Holt Account Balance mit korrekter Signature"""
        endpoint = "/v5/account/wallet-balance"
        params = {'accountType': 'UNIFIED'}
        
        result = self.make_authenticated_request('GET', endpoint, params=params)
        
        if result and result.get('retCode') == 0:
            account_info = result.get('result', {})
            account_list = account_info.get('list', [])
            
            if account_list:
                account = account_list[0]
                coins = account.get('coin', [])
                
                balances = {}
                for coin in coins:
                    coin_name = coin.get('coin')
                    balance = float(coin.get('walletBalance', 0))
                    if balance > 0:
                        balances[coin_name] = balance
                
                logger.info(f"Account Balance: {balances}")
                return {'success': True, 'balances': balances}
            else:
                logger.warning("No account data found")
                return {'success': False, 'error': 'No account data'}
        else:
            error_msg = result.get('retMsg', 'Unknown error') if result else 'No response'
            logger.error(f"Balance request failed: {error_msg}")
            return {'success': False, 'error': error_msg, 'response': result}
    
    def get_market_price(self, symbol='BTCUSDT'):
        """Holt aktuellen Marktpreis (Public API - keine Authentication)"""
        try:
            url = f"{self.base_url}/v5/market/tickers"
            params = {'category': 'spot', 'symbol': symbol}
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('retCode') == 0:
                    ticker = data['result']['list'][0]
                    price = float(ticker['lastPrice'])
                    change_24h = float(ticker['price24hPcnt']) * 100
                    
                    logger.info(f"{symbol}: ${price:.2f} ({change_24h:+.2f}%)")
                    return {
                        'success': True,
                        'symbol': symbol,
                        'price': price,
                        'change_24h': change_24h
                    }
            
            return {'success': False}
            
        except Exception as e:
            logger.error(f"Error getting price: {e}")
            return {'success': False}
    
    def place_spot_order(self, symbol='BTCUSDT', side='Buy', order_type='Market', qty='0.001', price=None):
        """
        Platziert Spot Order mit korrekter V5 API Signature
        """
        endpoint = "/v5/order/create"
        
        order_data = {
            'category': 'spot',
            'symbol': symbol,
            'side': side,
            'orderType': order_type,
            'qty': str(qty)
        }
        
        if price and order_type == 'Limit':
            order_data['price'] = str(price)
            order_data['timeInForce'] = 'GTC'
        
        result = self.make_authenticated_request('POST', endpoint, json_data=order_data)
        
        if result and result.get('retCode') == 0:
            order_id = result.get('result', {}).get('orderId')
            logger.info(f"ORDER SUCCESS: {side} {qty} {symbol} | Order ID: {order_id}")
            return {'success': True, 'order_id': order_id, 'response': result}
        else:
            error_msg = result.get('retMsg', 'Unknown error') if result else 'No response'
            logger.error(f"ORDER FAILED: {error_msg}")
            return {'success': False, 'error': error_msg, 'response': result}
    
    def get_server_time(self):
        """Holt Bybit Server Zeit (Public API)"""
        try:
            url = f"{self.base_url}/v5/market/time"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('retCode') == 0:
                    server_time = int(data['result']['timeSecond'])
                    logger.info(f"Server Time: {server_time} ({datetime.fromtimestamp(server_time)})")
                    return {'success': True, 'time': server_time}
            
            return {'success': False}
            
        except Exception as e:
            logger.error(f"Error getting server time: {e}")
            return {'success': False}

def comprehensive_api_test():
    """Umfassender Test der korrigierten API Implementierung"""
    print("=" * 70)
    print("BYBIT V5 API - COMPREHENSIVE CONNECTION TEST")
    print("=" * 70)
    
    try:
        api = CorrectBybitAPI()
    except Exception as e:
        print(f"[FAIL] API Initialization failed: {e}")
        return
    
    # Test 1: Server Zeit (Public API)
    print("\n1. Testing Server Time (Public API)...")
    server_time = api.get_server_time()
    if server_time['success']:
        print(f"[PASS] Server Time: {datetime.fromtimestamp(server_time['time'])}")
    else:
        print("[FAIL] Server Time test failed")
    
    # Test 2: Market Preis (Public API)
    print("\n2. Testing Market Price (Public API)...")
    price_data = api.get_market_price()
    if price_data['success']:
        print(f"[PASS] BTC Price: ${price_data['price']:.2f} ({price_data['change_24h']:+.2f}%)")
    else:
        print("[FAIL] Market Price test failed")
    
    # Test 3: Account Balance (Private API - DER WICHTIGE TEST)
    print("\n3. Testing Account Balance (Private API - Authentication Test)...")
    balance_result = api.get_account_balance()
    
    if balance_result['success']:
        balances = balance_result['balances']
        print("[PASS] Account Balance Retrieved Successfully!")
        print("Available Balances:")
        for coin, amount in balances.items():
            if coin == 'USDT':
                print(f"  {coin}: {amount:.2f}")
            else:
                print(f"  {coin}: {amount:.8f}")
    else:
        print("[FAIL] Account Balance test failed")
        print(f"Error: {balance_result.get('error', 'Unknown')}")
        if 'response' in balance_result:
            print(f"Full Response: {balance_result['response']}")
    
    # Test 4: Conditional Order Test
    if balance_result.get('success'):
        usdt_balance = balance_result.get('balances', {}).get('USDT', 0)
        if usdt_balance > 10:  # Nur wenn mindestens 10 USDT verfügbar
            print(f"\n4. Testing Order Placement (Balance: {usdt_balance:.2f} USDT)...")
            print("[WARNING] This will place a REAL small order on Testnet!")
            
            confirm = input("Place test order of 0.0001 BTC? (y/N): ").lower()
            if confirm == 'y':
                order_result = api.place_spot_order(
                    symbol='BTCUSDT',
                    side='Buy',
                    order_type='Market',
                    qty='0.0001'
                )
                
                if order_result['success']:
                    print(f"[PASS] Test Order Placed! Order ID: {order_result['order_id']}")
                else:
                    print(f"[FAIL] Test Order Failed: {order_result['error']}")
            else:
                print("Test Order skipped by user.")
        else:
            print(f"\n4. Skipping Order Test (Balance too low: {usdt_balance:.2f} USDT)")
    else:
        print("\n4. Skipping Order Test (Balance check failed)")
    
    print("\n" + "=" * 70)
    print("API TEST COMPLETED")
    
    if balance_result.get('success'):
        print("RESULT: API AUTHENTICATION WORKING!")
        print("Your trading bot can now make real trades.")
    else:
        print("RESULT: API AUTHENTICATION STILL FAILING")
        print("Need to debug signature generation further.")
    
    print("=" * 70)

if __name__ == "__main__":
    comprehensive_api_test()
