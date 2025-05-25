#!/usr/bin/env python3
"""
🚀 LIVE BYBIT API INTEGRATION FÜR DASHBOARD
Echte Balance und Live Preise für das Dashboard
"""

import requests
import hashlib
import hmac
import time
import os
from dotenv import load_dotenv

load_dotenv()

class LiveBybitAPI:
    """Live Bybit API Integration für Dashboard"""
    
    def __init__(self):
        self.api_key = os.getenv('BYBIT_API_KEY')
        self.secret_key = os.getenv('BYBIT_API_SECRET')
        self.testnet = os.getenv('TESTNET', 'true').lower() == 'true'
        
        if self.testnet:
            self.base_url = "https://api-testnet.bybit.com"
        else:
            self.base_url = "https://api.bybit.com"
        
        self.recv_window = str(5000)
    
    def generate_signature(self, timestamp, payload):
        """Generiert Bybit V5 Signature"""
        param_str = str(timestamp) + self.api_key + self.recv_window + payload
        hash_obj = hmac.new(bytes(self.secret_key, "utf-8"), param_str.encode("utf-8"), hashlib.sha256)
        return hash_obj.hexdigest()
    
    def make_request(self, method, endpoint, payload="", json_data=None):
        """Macht authentifizierten API Request"""
        timestamp = str(int(time.time() * 1000))
        
        if json_data:
            import json
            payload = json.dumps(json_data, separators=(',', ':'))
        
        signature = self.generate_signature(timestamp, payload)
        
        headers = {
            'X-BAPI-API-KEY': self.api_key,
            'X-BAPI-SIGN': signature,
            'X-BAPI-SIGN-TYPE': '2',
            'X-BAPI-TIMESTAMP': timestamp,
            'X-BAPI-RECV-WINDOW': self.recv_window,
            'Content-Type': 'application/json'
        }
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == "GET":
                if payload:
                    url += f"?{payload}"
                response = requests.get(url, headers=headers, timeout=10)
            else:
                response = requests.post(url, headers=headers, data=payload, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"API Error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Request Error: {e}")
            return None
    
    def get_account_balance(self):
        """Holt echte Account Balance"""
        try:
            result = self.make_request("GET", "/v5/account/wallet-balance", "accountType=UNIFIED")
            
            if result and result.get('retCode') == 0:
                account = result['result']['list'][0]
                coins = account['coin']
                
                balances = {}
                total_usdt_value = 0
                
                for coin in coins:
                    balance = float(coin['walletBalance'])
                    if balance > 0:
                        balances[coin['coin']] = balance
                        
                        # Calculate USD value
                        if coin['coin'] == 'USDT':
                            total_usdt_value += balance
                        elif coin['coin'] == 'BTC':
                            btc_price = self.get_btc_price()
                            if btc_price:
                                total_usdt_value += balance * btc_price['price']
                
                return {
                    'balances': balances,
                    'total_usdt_value': total_usdt_value,
                    'success': True
                }
            
            return {'success': False, 'error': 'API call failed'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_btc_price(self):
        """Holt aktuellen BTC Preis"""
        try:
            url = f"{self.base_url}/v5/market/tickers"
            params = {'category': 'spot', 'symbol': 'BTCUSDT'}
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('retCode') == 0:
                    ticker = data['result']['list'][0]
                    return {
                        'price': float(ticker['lastPrice']),
                        'change_24h': float(ticker['price24hPcnt']) * 100,
                        'high_24h': float(ticker['highPrice24h']),
                        'low_24h': float(ticker['lowPrice24h']),
                        'volume_24h': float(ticker['volume24h']),
                        'success': True
                    }
            
            return {'success': False, 'error': 'Price API failed'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_dashboard_data(self):
        """Kombinierte Daten für Dashboard"""
        balance_data = self.get_account_balance()
        price_data = self.get_btc_price()
        
        if balance_data['success'] and price_data['success']:
            return {
                'portfolio_value': balance_data['total_usdt_value'],
                'balances': balance_data['balances'],
                'btc_price': price_data['price'],
                'btc_change_24h': price_data['change_24h'],
                'btc_high_24h': price_data['high_24h'],
                'btc_low_24h': price_data['low_24h'],
                'btc_volume_24h': price_data['volume_24h'],
                'api_status': 'CONNECTED',
                'account_type': 'TESTNET' if self.testnet else 'MAINNET',
                'success': True
            }
        else:
            return {
                'success': False,
                'api_status': 'ERROR',
                'balance_error': balance_data.get('error', ''),
                'price_error': price_data.get('error', '')
            }

# Test function
def test_api():
    """Testet die API-Verbindung"""
    api = LiveBybitAPI()
    
    print("Testing Live Bybit API...")
    print(f"API Base URL: {api.base_url}")
    print(f"Testnet Mode: {api.testnet}")
    
    # Test Dashboard Data
    result = api.get_dashboard_data()
    
    if result['success']:
        print("\nAPI Connection Successful!")
        print(f"Portfolio Value: ${result['portfolio_value']:.2f}")
        print(f"BTC Price: ${result['btc_price']:,.2f}")
        print(f"24h Change: {result['btc_change_24h']:+.2f}%")
        print(f"Account: {result['account_type']}")
        
        print("\nBalances:")
        for coin, amount in result['balances'].items():
            if coin == 'USDT':
                print(f"   {coin}: {amount:.2f}")
            else:
                print(f"   {coin}: {amount:.6f}")
    else:
        print("\nAPI Connection Failed!")
        print(f"Balance Error: {result.get('balance_error', 'N/A')}")
        print(f"Price Error: {result.get('price_error', 'N/A')}")

if __name__ == "__main__":
    test_api()
