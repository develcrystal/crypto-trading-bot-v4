#!/usr/bin/env python
"""
FIXED BYBIT V5 API - KORREKTE SIGNATURE IMPLEMENTIERUNG
Basierend auf offizieller Bybit V5 API Dokumentation
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
        logging.FileHandler('fixed_bybit_api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FixedBybitAPI:
    """Korrekte Bybit V5 API Implementation mit richtiger Signature"""
    
    def __init__(self):
        # API Credentials
        self.api_key = os.getenv('BYBIT_API_KEY')
        self.api_secret = os.getenv('BYBIT_API_SECRET')
        self.base_url = "https://api-testnet.bybit.com"
        self.recv_window = '5000'
        
        if not self.api_key or not self.api_secret:
            raise ValueError("API Key and Secret must be set in .env file")
        
        logger.info("Fixed Bybit API initialisiert")
        logger.info(f"API Key: {self.api_key[:8]}...")
        logger.info(f"API Secret: {self.api_secret[:8]}...")
    
    def generate_signature(self, timestamp, payload=""):
        """
        Generiert korrekte Bybit V5 API Signature
        Regel: timestamp + api_key + recv_window + payload
        """
        # String zum Signieren erstellen (genau wie in Bybit Docs)
        param_str = str(timestamp) + self.api_key + self.recv_window + payload
        
        logger.debug(f"String to sign: {param_str}")
        
        # HMAC SHA256 Signatur erstellen
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            param_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def make_request(self, method, endpoint, params=None, data=None):
        """
        Macht authentifizierten Request zu Bybit V5 API
        Verwendet korrekte Header-Format
        """
        # Timestamp generieren
        timestamp = str(int(time.time() * 1000))
        
        # URL zusammenbauen
        url = f"{self.base_url}{endpoint}"
        
        # Payload für Signature erstellen
        if method.upper() == 'GET':
            # Für GET: query string
            if params:
                query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
                payload = query_string
                url += f"?{query_string}"
            else:
                payload = ""
        else:
            # Für POST: JSON body string
            if data:
                payload = json.dumps(data, separators=(',', ':'))
            else:
                payload = ""
        
        # Signature generieren
        signature = self.generate_signature(timestamp, payload)
        
        # Korrekte V5 API Headers
        headers = {
            'X-BAPI-API-KEY': self.api_key,
            'X-BAPI-SIGN': signature,
            'X-BAPI-SIGN-TYPE': '2',
            'X-BAPI-TIMESTAMP': timestamp,
            'X-BAPI-RECV-WINDOW': self.recv_window,
            'Content-Type': 'application/json'
        }
        
        logger.info(f"Making {method} request to {endpoint}")
        logger.debug(f"Headers: {headers}")
        logger.debug(f"Payload: {payload}")
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, data=payload if payload else None, timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            logger.info(f"Response Status: {response.status_code}")
            logger.debug(f"Response Text: {response.text}")
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"API Error: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': response.text,
                    'status_code': response.status_code
                }
                
        except Exception as e:
            logger.error(f"Request Error: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_server_time(self):
        """Holt Bybit Server Zeit (ohne Authentication)"""
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
    
    def get_account_balance(self):
        """
        Holt Account Balance mit korrekter V5 API Signature
        """
        endpoint = "/v5/account/wallet-balance"
        params = {'accountType': 'UNIFIED'}
        
        response = self.make_request('GET', endpoint, params=params)
        
        if response and response.get('retCode') == 0:
            result = response.get('result', {})
            account_list = result.get('list', [])
            
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
        
        logger.error(f"Failed to get balance: {response}")
        return {'success': False, 'response': response}
    
    def get_market_price(self, symbol='BTCUSDT'):
        """Holt aktuellen Marktpreis (ohne Authentication)"""
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
    
    def place_order(self, category='spot', symbol='BTCUSDT', side='Buy', order_type='Market', qty='0.001', price=None):
        """
        Platziert Order mit korrekter V5 API Signature
        """
        endpoint = "/v5/order/create"
        
        order_data = {
            'category': category,
            'symbol': symbol,
            'side': side,
            'orderType': order_type,
            'qty': str(qty)
        }
        
        if price and order_type == 'Limit':
            order_data['price'] = str(price)
            order_data['timeInForce'] = 'GTC'
        
        response = self.make_request('POST', endpoint, data=order_data)
        
        if response and response.get('retCode') == 0:
            order_id = response.get('result', {}).get('orderId')
            logger.info(f"ORDER SUCCESS: {side} {qty} {symbol} | Order ID: {order_id}")
            return {'success': True, 'order_id': order_id, 'response': response}
        else:
            error_msg = response.get('retMsg', 'Unknown error') if response else 'No response'
            logger.error(f"ORDER FAILED: {error_msg}")
            return {'success': False, 'error': error_msg, 'response': response}

def test_api_connection():
    """Testet die API Verbindung mit allen wichtigen Funktionen"""
    print("=" * 60)
    print("BYBIT V5 API CONNECTION TEST")
    print("=" * 60)
    
    api = FixedBybitAPI()
    
    # Test 1: Server Zeit (ohne Authentication)
    print("\n1. Testing Server Time (Public API)...")
    server_time = api.get_server_time()
    if server_time['success']:
        print(f"[OK] Server Time: {datetime.fromtimestamp(server_time['time'])}")
    else:
        print("[FAIL] Server Time failed")
    
    # Test 2: Market Preis (ohne Authentication)
    print("\n2. Testing Market Price (Public API)...")
    price_data = api.get_market_price()
    if price_data['success']:
        print(f"[OK] BTC Price: ${price_data['price']:.2f} ({price_data['change_24h']:+.2f}%)")
    else:
        print("[FAIL] Market Price failed")
    
    # Test 3: Account Balance (mit Authentication)
    print("\n3. Testing Account Balance (Private API)...")
    balance_result = api.get_account_balance()
    if balance_result['success']:
        balances = balance_result['balances']
        print(f"[OK] Account Balance:")
        for coin, amount in balances.items():
            if coin == 'USDT':
                print(f"   [{coin}] {amount:.2f}")
            else:
                print(f"   [{coin}] {amount:.6f}")
    else:
        print("[FAIL] Account Balance failed")
        print(f"   Error: {balance_result.get('response', 'Unknown error')}")
    
    # Test 4: Kleine Test-Order (nur wenn Balance > 50 USDT)
    if balance_result.get('success') and balance_result.get('balances', {}).get('USDT', 0) > 50:
        print("\n4. Testing Small Order Placement...")
        print("[WARNING] This would place a REAL order on your Testnet account!")
        
        confirm = input("Place small test order? (y/N): ").lower()
        if confirm == 'y':
            # Sehr kleine Order für Test
            order_result = api.place_order(
                category='spot',
                symbol='BTCUSDT',
                side='Buy',
                order_type='Market',
                qty='0.0001'  # Sehr kleine Menge
            )
            
            if order_result['success']:
                print(f"[OK] Test Order Placed! Order ID: {order_result['order_id']}")
            else:
                print(f"[FAIL] Test Order Failed: {order_result['error']}")
        else:
            print("Test Order skipped.")
    else:
        print("\n4. Skipping Order Test (insufficient balance or balance check failed)")
    
    print("\n" + "=" * 60)
    print("API CONNECTION TEST COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    test_api_connection()
