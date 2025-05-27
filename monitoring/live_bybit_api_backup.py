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
        position_data = self.check_open_positions()
        kline_data = self.get_kline_data()
        
        # Bot Status prüfen (Dateipfad und Process ID)
        bot_status = self.check_bot_status()
        
        if (balance_data['success'] and price_data['success'] and 
            live_ticker_data['success'] and order_book_data['success'] and 
            kline_data['success'] and position_data['success']):
            
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
                'open_positions': position_data['open_positions'],
                'positions': position_data['positions'] if position_data['open_positions'] else [],
                'bot_status': bot_status,
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
                'position_error': position_data.get('error', 'N/A') if not position_data['success'] else 'None',
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

    def check_open_positions(self):
        """Überprüft, ob Positionen geöffnet sind"""
        try:
            result = self.make_request("GET", "/v5/position/list", "category=linear")
            
            if result['success'] and result['data'].get('retCode') == 0:
                positions = result['data']['result']['list']
                open_positions = [pos for pos in positions if float(pos['size']) > 0]
                
                if open_positions:
                    return {
                        'success': True,
                        'open_positions': True,
                        'positions': open_positions
                    }
                else:
                    return {
                        'success': True,
                        'open_positions': False,
                        'positions': []
                    }
            else:
                return {'success': False, 'error': 'Failed to fetch positions'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def check_bot_status(self):
        """Überprüft den Status des Trading Bots"""
        try:
            import os
            import psutil
            
            bot_status = {
                'running': False,
                'process_id': None,
                'uptime': None,
                'market_regime': None,
                'last_signal': None
            }
            
            # Prüfen ob der Bot-Prozess läuft
            bot_files = [
                'enhanced_live_bot.py', 
                'enhanced_live_trading_bot.py',
                'live_trading_bot.py'
            ]
            
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
                try:
                    cmdline = proc.info['cmdline']
                    if cmdline and len(cmdline) > 1:
                        for bot_file in bot_files:
                            if bot_file in ' '.join(cmdline):
                                bot_status['running'] = True
                                bot_status['process_id'] = proc.info['pid']
                                # Uptime berechnen
                                uptime_seconds = time.time() - proc.info['create_time']
                                hours, remainder = divmod(uptime_seconds, 3600)
                                minutes, seconds = divmod(remainder, 60)
                                bot_status['uptime'] = f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
                                break
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            
            # Prüfen ob Logfile mit Market Regime existiert
            log_paths = [
                'live_trading_bot.log', 
                'live_trading.log',
                'enhanced_live_bot.log'
            ]
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
            for log_path in log_paths:
                full_path = os.path.join(base_dir, log_path)
                if os.path.exists(full_path):
                    try:
                        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                            # Die letzten 50 Zeilen lesen
                            lines = f.readlines()[-50:]
                            for line in reversed(lines):
                                if "Market Regime:" in line:
                                    if "BULL" in line:
                                        bot_status['market_regime'] = 'BULL'
                                    elif "BEAR" in line:
                                        bot_status['market_regime'] = 'BEAR'
                                    elif "SIDEWAYS" in line:
                                        bot_status['market_regime'] = 'SIDEWAYS'
                                    break
                                
                                if "SIGNAL:" in line and ("BUY" in line or "SELL" in line):
                                    if "BUY" in line:
                                        bot_status['last_signal'] = 'BUY'
                                    elif "SELL" in line:
                                        bot_status['last_signal'] = 'SELL'
                                    break
                    except Exception as e:
                        print(f"Error reading log file {log_path}: {str(e)}")
                        pass
            
            return bot_status
        except Exception as e:
            print(f"Error in check_bot_status: {str(e)}")
            return {
                'running': False,
                'process_id': None,
                'uptime': None,
                'market_regime': None,
                'last_signal': None,
                'error': str(e)
            }
        
    def emergency_stop_bot(self):
        """Stoppt den Trading Bot im Notfall"""
        import os
        import psutil
        import signal
        
        result = {
            'success': False,
            'message': 'Kein aktiver Bot gefunden'
        }
        
        # Bot-Prozess finden
        bot_files = [
            'enhanced_live_bot.py', 
            'enhanced_live_trading_bot.py',
            'live_trading_bot.py'
        ]
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info['cmdline']
                if cmdline and len(cmdline) > 1:
                    for bot_file in bot_files:
                        if bot_file in ' '.join(cmdline):
                            # Stoppe den Prozess
                            try:
                                os.kill(proc.info['pid'], signal.SIGTERM)
                                result['success'] = True
                                result['message'] = f"Bot gestoppt (PID: {proc.info['pid']})"
                                return result
                            except Exception as e:
                                result['message'] = f"Fehler beim Stoppen: {str(e)}"
                                return result
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        # Erstelle Emergency-Stop-Datei als Alternative
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            with open(os.path.join(base_dir, 'EMERGENCY_STOP'), 'w') as f:
                f.write(f"EMERGENCY STOP REQUESTED at {datetime.now()}")
            result['success'] = True
            result['message'] = "Emergency-Stop-Datei erstellt. Bot wird bei nächster Iteration stoppen."
        except Exception as e:
            result['message'] = f"Fehler beim Erstellen der Emergency-Stop-Datei: {str(e)}"
        
        return result
        
    def place_manual_trade(self, side, symbol, quantity, price=None, stop_loss=None, take_profit=None):
        """Platziert manuell einen Trade"""
        try:
            # Für Market Order
            if price is None:
                order_type = "Market"
                params = {
                    "category": "spot",
                    "symbol": symbol,
                    "side": side,
                    "orderType": order_type,
                    "qty": str(quantity)
                }
            else:
                # Für Limit Order
                order_type = "Limit"
                params = {
                    "category": "spot",
                    "symbol": symbol,
                    "side": side,
                    "orderType": order_type,
                    "qty": str(quantity),
                    "price": str(price),
                    "timeInForce": "GoodTillCancel"
                }
            
            # Stop Loss / Take Profit als separate Orders
            orders = []
            
            # Hauptorder
            result = self.make_request("POST", "/v5/order/create", "", json_data=params)
            orders.append(result)
            
            # Erfolgreich?
            if result['success'] and result['data'].get('retCode') == 0:
                order_id = result['data']['result']['orderId']
                
                # Stop Loss für SPOT ist etwas komplexer - wir müssen OCO Orders oder separate Conditional Orders verwenden
                # Hier implementieren wir einfache Limit Orders für TP und Market für SL
                
                # Für einfaches Stop-Loss bei Market Orders (Buy) müssen wir eine Sell Order platzieren
                if stop_loss is not None and side == "Buy":
                    try:
                        sl_params = {
                            "category": "spot",
                            "symbol": symbol,
                            "side": "Sell",
                            "orderType": "Limit",
                            "price": str(stop_loss),
                            "qty": str(quantity),
                            "timeInForce": "GoodTillCancel",
                            "orderLinkId": f"SL-{order_id}"
                        }
                        sl_result = self.make_request("POST", "/v5/order/create", "", json_data=sl_params)
                        orders.append(sl_result)
                    except Exception as sl_error:
                        print(f"Stop-Loss Order Error: {str(sl_error)}")
                
                # Take Profit (ähnlich wie Stop Loss, aber zu höherem Preis für Buy)
                if take_profit is not None and side == "Buy":
                    try:
                        tp_params = {
                            "category": "spot",
                            "symbol": symbol,
                            "side": "Sell",
                            "orderType": "Limit",
                            "price": str(take_profit),
                            "qty": str(quantity),
                            "timeInForce": "GoodTillCancel",
                            "orderLinkId": f"TP-{order_id}"
                        }
                        tp_result = self.make_request("POST", "/v5/order/create", "", json_data=tp_params)
                        orders.append(tp_result)
                    except Exception as tp_error:
                        print(f"Take-Profit Order Error: {str(tp_error)}")
                
                # Erfolgreich zurückgeben
                return {
                    'success': True,
                    'order_id': order_id,
                    'orders': orders,
                    'message': f"{side} Order für {quantity} {symbol} platziert"
                }
            else:
                # Fehler im Hauptorder
                error_data = result.get('data', {})
                error_code = error_data.get('retCode', 'Unknown')
                error_msg = error_data.get('retMsg', 'Unknown error')
                return {
                    'success': False,
                    'orders': orders,
                    'error': f"Order fehlgeschlagen: [{error_code}] {error_msg}"
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

if __name__ == "__main__":
    api = LiveBybitAPI()
    print("Testing Live Bybit API...")
    
    # Balance testen
    balance = api.get_wallet_balance()
    if balance['success']:
        print(f"Balance: {balance['balances']}")
    else:
        print(f"Balance Error: {balance.get('error')}")