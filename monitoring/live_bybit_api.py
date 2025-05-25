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
from datetime import datetime
from dotenv import load_dotenv
import pandas as pd

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
                return {'success': True, 'data': response.json()}
            else:
                error_msg = f"API Error: {response.status_code} - {response.text}"
                print(error_msg)
                return {'success': False, 'error': error_msg}
                
        except requests.exceptions.Timeout:
            error_msg = "Request Timeout: The API request took too long to respond."
            print(error_msg)
            return {'success': False, 'error': error_msg}
        except requests.exceptions.ConnectionError:
            error_msg = "Connection Error: Unable to connect to the Bybit API. Check your internet connection or Bybit server status."
            print(error_msg)
            return {'success': False, 'error': error_msg}
        except Exception as e:
            error_msg = f"Request Error: {e}"
            print(error_msg)
            return {'success': False, 'error': error_msg}
    
    def get_wallet_balance(self):
        """Holt echte Account Balance"""
        try:
            result = self.make_request("GET", "/v5/account/wallet-balance", "accountType=UNIFIED")
            
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
    
    def get_live_ticker(self, symbol='BTCUSDT'):
        """Get live ticker data with bid/ask"""
        try:
            url = f"{self.base_url}/v5/market/tickers"
            params = {'category': 'spot', 'symbol': symbol}
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('retCode') == 0 and 'result' in data:
                    ticker_list = data['result']['list']
                    if ticker_list:
                        ticker = ticker_list[0]
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
            
            return {'success': False, 'error': f'HTTP {response.status_code}'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_order_book(self, symbol='BTCUSDT', limit=10):
        """Get live order book data"""
        try:
            url = f"{self.base_url}/v5/market/orderbook"
            params = {'category': 'spot', 'symbol': symbol, 'limit': limit}
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('retCode') == 0 and 'result' in data:
                    book = data['result']
                    return {
                        'success': True,
                        'bids': [[float(x[0]), float(x[1])] for x in book.get('b', [])],
                        'asks': [[float(x[0]), float(x[1])] for x in book.get('a', [])],
                        'timestamp': datetime.now()
                    }
            
            return {'success': False, 'error': f'HTTP {response.status_code}'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_kline_data(self, symbol='BTCUSDT', interval='5', limit=100):
        """Get candlestick data for charts"""
        try:
            params = {
                'category': 'spot',
                'symbol': symbol,
                'interval': interval,
                'limit': limit
            }
            
            result = self.make_request("GET", "/v5/market/kline", payload=f"category=spot&symbol={symbol}&interval={interval}&limit={limit}")
            
            if result['success'] and result['data'].get('retCode') == 0:
                klines = result['data']['result']['list']
                df = pd.DataFrame(klines, columns=[
                    'timestamp', 'open', 'high', 'low', 'close', 'volume', 'turnover'
                ])
                df['timestamp'] = pd.to_datetime(df['timestamp'].astype(int), unit='ms')
                for col in ['open', 'high', 'low', 'close', 'volume']:
                    df[col] = df[col].astype(float)
                df = df.sort_values('timestamp').reset_index(drop=True)
                return {'success': True, 'data': df}
            
            return {'success': False, 'error': result.get('error', 'Failed to fetch kline data')}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_dashboard_data(self):
        """Kombinierte Daten für Dashboard"""
        balance_data = self.get_wallet_balance()
        price_data = self.get_btc_price()
        live_ticker_data = self.get_live_ticker()
        order_book_data = self.get_order_book()
        
        kline_data = self.get_kline_data()
        
        if balance_data['success'] and price_data['success'] and live_ticker_data['success'] and order_book_data['success'] and kline_data['success']:
            return {
                'portfolio_value': balance_data['total_usdt_value'],
                'balances': balance_data['balances'],
                'btc_price': price_data['price'],
                'btc_change_24h': price_data['change_24h'],
                'btc_high_24h': price_data['high_24h'],
                'btc_low_24h': price_data['low_24h'],
                'btc_volume_24h': price_data['volume_24h'],
                'bid': live_ticker_data['bid'],
                'ask': live_ticker_data['ask'],
                'order_book_bids': order_book_data['bids'],
                'order_book_asks': order_book_data['asks'],
                'kline_data': kline_data['data'],
                'api_status': 'CONNECTED',
                'account_type': 'TESTNET' if self.testnet else 'MAINNET',
                'success': True
            }
        else:
            error_details = {
                'balance_error': balance_data.get('error', 'N/A') if not balance_data['success'] else 'None',
                'price_error': price_data.get('error', 'N/A') if not price_data['success'] else 'None',
                'live_ticker_error': live_ticker_data.get('error', 'N/A') if not live_ticker_data['success'] else 'None',
                'order_book_error': order_book_data.get('error', 'N/A') if not order_book_data['success'] else 'None',
                'kline_error': kline_data.get('error', 'N/A') if not kline_data['success'] else 'None'
            }
            print(f"Dashboard Data Fetch Error Details: {error_details}")
            return {
                'success': False,
                'api_status': 'ERROR',
                'error': f"Failed to fetch all dashboard data. Details: {error_details}"
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
        
        print("\nLive Ticker Data:")
        print(f"  Bid: {result['bid']:.2f}")
        print(f"  Ask: {result['ask']:.2f}")
        
        print("\nOrder Book Bids (first 5):")
        for bid in result['order_book_bids'][:5]:
            print(f"  Price: {bid[0]:.2f}, Size: {bid[1]:.4f}")
            
        print("\nOrder Book Asks (first 5):")
        for ask in result['order_book_asks'][:5]:
            print(f"  Price: {ask[0]:.2f}, Size: {ask[1]:.4f}")
            
        print("\nKline Data (last 5 rows):")
        print(result['kline_data'].tail())
        
    else:
        print("\nAPI Connection Failed!")
        print(f"Balance Error: {result.get('balance_error', 'N/A')}")
        print(f"Price Error: {result.get('price_error', 'N/A')}")
        print(f"Live Ticker Error: {result.get('live_ticker_error', 'N/A')}")
        print(f"Order Book Error: {result.get('order_book_error', 'N/A')}")
        print(f"Kline Error: {result.get('kline_error', 'N/A')}")

if __name__ == "__main__":
    test_api()