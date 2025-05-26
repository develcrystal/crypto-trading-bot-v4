#!/usr/bin/env python3
"""
🚀 CORRECTED LIVE BYBIT API INTEGRATION
Fixed for Unified Trading Account with proper error handling
"""

import requests
import hashlib
import hmac
import time
import os
from datetime import datetime
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

class LiveBybitAPI:
    """Corrected Live Bybit API Integration"""
    
    def __init__(self):
        self.api_key = os.getenv('BYBIT_API_KEY')
        self.api_secret = os.getenv('BYBIT_API_SECRET')
        self.testnet = os.getenv('TESTNET', 'false').lower() == 'true'
        
        if self.testnet:
            self.base_url = "https://api-testnet.bybit.com"
        else:
            self.base_url = "https://api.bybit.com"
    
    def create_signature(self, params_str):
        """Create HMAC SHA256 signature"""
        return hmac.new(
            self.api_secret.encode('utf-8'),
            params_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    def make_authenticated_request(self, method, endpoint, params=None):
        """Make authenticated request to Bybit API"""
        if params is None:
            params = {}
        
        timestamp = str(int(time.time() * 1000))
        params['api_key'] = self.api_key
        params['timestamp'] = timestamp
        
        # Create signature
        param_str = '&'.join([f"{k}={v}" for k, v in sorted(params.items())])
        params['sign'] = self.create_signature(param_str)
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == 'GET':
                response = requests.get(url, params=params, timeout=10)
            else:
                response = requests.post(url, json=params, timeout=10)
            
            if response.status_code == 200:
                return {'success': True, 'data': response.json()}
            else:
                return {'success': False, 'error': f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_btc_price(self):
        """Get current BTC price (public API)"""
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
                        'volume_24h': float(ticker['turnover24h']),
                        'success': True
                    }
            
            return {'success': False, 'error': 'Price API failed'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_live_ticker(self, symbol='BTCUSDT'):
        """Get live ticker with bid/ask"""
        try:
            url = f"{self.base_url}/v5/market/tickers"
            params = {'category': 'spot', 'symbol': symbol}
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('retCode') == 0:
                    ticker = data['result']['list'][0]
                    return {
                        'bid': float(ticker['bid1Price']),
                        'ask': float(ticker['ask1Price']),
                        'success': True
                    }
            
            return {'success': False, 'error': 'Ticker API failed'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_order_book(self, symbol='BTCUSDT', limit=10):
        """Get order book data"""
        try:
            url = f"{self.base_url}/v5/market/orderbook"
            params = {'category': 'spot', 'symbol': symbol, 'limit': limit}
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('retCode') == 0:
                    result = data['result']
                    return {
                        'bids': [[float(price), float(size)] for price, size in result['b'][:limit]],
                        'asks': [[float(price), float(size)] for price, size in result['a'][:limit]],
                        'success': True
                    }
            
            return {'success': False, 'error': 'Order book API failed'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_wallet_balance(self):
        """Get wallet balance (authenticated)"""
        try:
            result = self.make_authenticated_request("GET", "/v5/account/wallet-balance", 
                                                   {"accountType": "UNIFIED"})
            
            if result['success'] and result['data'].get('retCode') == 0:
                account = result['data']['result']['list'][0]
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
                            btc_price_data = self.get_btc_price()
                            if btc_price_data.get('success'):
                                total_usdt_value += balance * btc_price_data['price']
                
                return {
                    'balances': balances,
                    'total_usdt_value': total_usdt_value,
                    'success': True
                }
            else:
                return {'success': False, 'error': 'Balance API failed'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_kline_data(self, symbol='BTCUSDT', interval='1', limit=100):
        """Get candlestick/kline data"""
        try:
            url = f"{self.base_url}/v5/market/kline"
            params = {
                'category': 'spot',
                'symbol': symbol,
                'interval': interval,
                'limit': limit
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('retCode') == 0:
                    klines = data['result']['list']
                    
                    # Convert to DataFrame
                    df = pd.DataFrame(klines, columns=[
                        'timestamp', 'open', 'high', 'low', 'close', 'volume', 'turnover'
                    ])
                    
                    # Convert types
                    for col in ['open', 'high', 'low', 'close', 'volume', 'turnover']:
                        df[col] = pd.to_numeric(df[col])
                    
                    df['timestamp'] = pd.to_datetime(df['timestamp'].astype(int), unit='ms')
                    
                    return {
                        'data': df.to_dict('records'),
                        'success': True
                    }
            
            return {'success': False, 'error': 'Kline API failed'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_all_dashboard_data(self):
        """Get all data needed for dashboard"""
        try:
            # Get all data
            price_data = self.get_btc_price()
            balance_data = self.get_wallet_balance()
            ticker_data = self.get_live_ticker()
            order_book_data = self.get_order_book()
            kline_data = self.get_kline_data()
            
            # Check if all successful
            all_success = all([
                price_data.get('success', False),
                balance_data.get('success', False),
                ticker_data.get('success', False),
                order_book_data.get('success', False),
                kline_data.get('success', False)
            ])
            
            if all_success:
                return {
                    'portfolio_value': balance_data['total_usdt_value'],
                    'balances': balance_data['balances'],
                    'btc_price': price_data['price'],
                    'btc_change_24h': price_data['change_24h'],
                    'btc_high_24h': price_data['high_24h'],
                    'btc_low_24h': price_data['low_24h'],
                    'btc_volume_24h': price_data['volume_24h'],
                    'bid': ticker_data['bid'],
                    'ask': ticker_data['ask'],
                    'order_book_bids': order_book_data['bids'],
                    'order_book_asks': order_book_data['asks'],
                    'kline_data': kline_data['data'],
                    'api_status': 'CONNECTED',
                    'last_update': datetime.now().strftime('%H:%M:%S'),
                    'success': True
                }
            else:
                # Return partial data with errors
                errors = []
                if not price_data.get('success'): errors.append(f"Market Data: {price_data.get('error', 'Unknown error')}")
                if not balance_data.get('success'): errors.append(f"Account Data: {balance_data.get('error', 'Unknown error')}")
                if not ticker_data.get('success'): errors.append(f"Ticker Data: {ticker_data.get('error', 'Unknown error')}")
                if not order_book_data.get('success'): errors.append(f"Order Book: {order_book_data.get('error', 'Unknown error')}")
                if not kline_data.get('success'): errors.append(f"Chart Data: {kline_data.get('error', 'Unknown error')}")
                
                return {
                    'success': False,
                    'error': '; '.join(errors),
                    'partial_data': {
                        'price_data': price_data,
                        'balance_data': balance_data,
                        'ticker_data': ticker_data
                    }
                }
                
        except Exception as e:
            return {'success': False, 'error': f"Dashboard data error: {str(e)}"}

# Test function
if __name__ == "__main__":
    api = LiveBybitAPI()
    
    print("Testing corrected API...")
    
    # Test price
    price_data = api.get_btc_price()
    print(f"Price data: {price_data}")
    
    # Test balance
    balance_data = api.get_wallet_balance()
    print(f"Balance data: {balance_data}")
    
    # Test all data
    all_data = api.get_all_dashboard_data()
    print(f"All data success: {all_data.get('success', False)}")
