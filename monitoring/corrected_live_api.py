#!/usr/bin/env python3
"""
🚀 CORRECTED BYBIT API INTEGRATION FÜR DASHBOARD
Fehlerbehebung für Spot-Trading API-Endpunkte und Position-Tracking
"""

import requests
import hashlib
import hmac
import time
import os
from datetime import datetime
from dotenv import load_dotenv
import pandas as pd
import psutil
import signal

load_dotenv()

class LiveBybitAPI:
    """Live Bybit API Integration für Dashboard mit Fixed Spot Trading Support"""
    
    def __init__(self):
        self.api_key = os.getenv('BYBIT_API_KEY')
        self.secret_key = os.getenv('BYBIT_API_SECRET')
        self.testnet = os.getenv('TESTNET', 'true').lower() == 'true'
        
        if self.testnet:
            self.base_url = "https://api-testnet.bybit.com"
        else:
            self.base_url = "https://api.bybit.com"
        
        self.recv_window = str(5000)
        self.log_patterns = {
            'signal': r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] SIGNAL: (BUY|SELL) at (\d+\.\d+) USDT',
            'trade': r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] TRADE: (BUY|SELL) executed at (\d+\.\d+) USDT, P&L: (-?\d+\.\d+) USDT',
            'order': r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] ORDER: (BUY|SELL) order placed at (\d+\.\d+) USDT, size: (\d+\.\d+) BTC'
        }
    
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
            error_msg = "Connection Error: Unable to connect to the Bybit API."
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

    def parse_log_file(self, log_path):
        """Parses trading logs for signals and trades"""
        signals = []
        trades = []
        
        try:
            with open(log_path, 'r') as f:
                lines = f.readlines()
                
                for line in lines:
                    # Parse signals
                    signal_match = re.search(self.log_patterns['signal'], line)
                    if signal_match:
                        timestamp, signal_type, price = signal_match.groups()
                        signals.append({
                            'timestamp': datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S'),
                            'type': signal_type,
                            'price': float(price),
                            'status': 'OPEN'
                        })
                    
                    # Parse trades
                    trade_match = re.search(self.log_patterns['trade'], line)
                    if trade_match:
                        timestamp, side, price, pnl = trade_match.groups()
                        trades.append({
                            'entry_time': datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S'),
                            'side': side,
                            'entry_price': float(price),
                            'pnl': float(pnl),
                            'status': 'CLOSED'
                        })
                    
                    # Parse orders
                    order_match = re.search(self.log_patterns['order'], line)
                    if order_match:
                        timestamp, side, price, size = order_match.groups()
                        # Store order information if needed
                        pass
                
        except Exception as e:
            print(f"Error parsing log file: {str(e)}")
            
        return {'signals': signals, 'trades': trades}

    def get_dashboard_data(self):
        """Holt alle notwendigen Dashboard-Daten"""
        data = {}
        
        # Get balance
        balance_data = self.get_wallet_balance()
        if balance_data['success']:
            data.update(balance_data)
            
        # Get BTC price
        btc_data = self.get_btc_price()
        if btc_data['success']:
            data.update(btc_data)
            
        # Parse logs
        try:
            log_data = self.parse_log_file('trading.log')
            data.update(log_data)
        except Exception as e:
            print(f"Error getting log data: {str(e)}")
            
        return data
    
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
            print(f"Fetching kline data for {symbol}, interval {interval}, limit {limit}")
            
            # Direkte API-Anfrage ohne make_request für schnellere Ergebnisse
            url = f"{self.base_url}/v5/market/kline"
            
            # Parameter für die Anfrage
            params = {
                'category': 'spot',
                'symbol': symbol,
                'interval': interval,
                'limit': str(limit)
            }
            
            # Debug-Ausgabe
            print(f"Request URL: {url}")
            print(f"Request params: {params}")
            
            # Anfrage senden
            response = requests.get(url, params=params, timeout=15)
            
            # Debug-Ausgabe
            print(f"Response status code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Debug-Ausgabe
                print(f"Response retCode: {data.get('retCode')}")
                
                if data.get('retCode') == 0 and 'result' in data and 'list' in data['result']:
                    klines = data['result']['list']
                    
                    # Prüfen ob Daten vorhanden sind
                    if not klines:
                        print("No kline data returned from API")
                        return {'success': False, 'error': 'No kline data available'}
                    
                    print(f"Received {len(klines)} kline records")
                    
                    # DataFrame erstellen
                    df = pd.DataFrame(klines, columns=[
                        'timestamp', 'open', 'high', 'low', 'close', 'volume', 'turnover'
                    ])
                    
                    # Datentypen konvertieren
                    df['timestamp'] = pd.to_datetime(df['timestamp'].astype(int), unit='ms')
                    for col in ['open', 'high', 'low', 'close', 'volume', 'turnover']:
                        df[col] = df[col].astype(float)
                    
                    # Sortieren und Index zurücksetzen
                    df = df.sort_values('timestamp').reset_index(drop=True)
                    
                    print(f"Successfully processed {len(df)} kline records for {symbol}")
                    
                    # Erste und letzte Zeile zur Überprüfung ausgeben
                    if not df.empty:
                        print(f"First row: {df.iloc[0]['timestamp']} - Open: {df.iloc[0]['open']}, Close: {df.iloc[0]['close']}")
                        print(f"Last row: {df.iloc[-1]['timestamp']} - Open: {df.iloc[-1]['open']}, Close: {df.iloc[-1]['close']}")
                    
                    return {'success': True, 'data': df}
                else:
                    error_msg = data.get('retMsg', 'Unknown API error')
                    print(f"API Error: {error_msg}")
                    return {'success': False, 'error': error_msg}
            else:
                print(f"HTTP Error: {response.status_code}")
                print(f"Response content: {response.text[:200]}")
                return {'success': False, 'error': f'HTTP Error: {response.status_code}'}
            
        except requests.exceptions.Timeout:
            print("Timeout while fetching kline data")
            return {'success': False, 'error': 'Request timeout'}
        except Exception as e:
            print(f"Exception while getting kline data: {str(e)}")
            return {'success': False, 'error': str(e)}

    def check_open_positions(self):
        """Überprüft, ob Positionen oder offene Orders für Spot vorhanden sind - FIXED VERSION"""
        try:
            # FIX: Korrigierter Endpoint für Spot Trading Orders
            orders_result = self.make_request("GET", "/v5/order/realtime", "category=spot")
            
            if not orders_result['success']:
                print(f"Order API Error: {orders_result.get('error', 'Unknown error')}")
                # Alternative Methode versuchen - history orders
                orders_result = self.make_request("GET", "/v5/order/history", "category=spot&limit=50")
            
            if orders_result['success'] and orders_result['data'].get('retCode') == 0:
                orders = orders_result['data']['result']['list']
                # Für Spot Trading betrachten wir offene Orders
                open_orders = [order for order in orders if order.get('orderStatus', '') in ['New', 'PartiallyFilled', 'Active', 'Created']]
                
                # Get account balance
                balance_result = self.get_wallet_balance()
                
                if balance_result['success']:
                    balances = balance_result['balances']
                    
                    # Combine orders and balance information
                    # Für Spot Trading betrachten wir Assets, die nicht USDT sind, als "Positionen"
                    non_usdt_assets = {k: v for k, v in balances.items() if k != 'USDT' and v > 0}
                    
                    positions = {
                        'open_orders': open_orders,
                        'balances': balances,
                        'total_usdt': balance_result['total_usdt_value'],
                        'non_usdt_assets': non_usdt_assets
                    }
                    
                    # Wir haben eine Position, wenn entweder offene Orders oder non-USDT Assets existieren
                    has_position = bool(open_orders) or bool(non_usdt_assets)
                    
                    return {
                        'success': True,
                        'open_positions': has_position,
                        'positions': positions
                    }
                else:
                    return {'success': False, 'error': f"Failed to fetch balance: {balance_result.get('error', 'Unknown error')}"}
            else:
                error_code = orders_result.get('data', {}).get('retCode', 'Unknown')
                error_msg = orders_result.get('data', {}).get('retMsg', orders_result.get('error', 'Unknown error'))
                return {'success': False, 'error': f"Failed to fetch orders: [{error_code}] {error_msg}"}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def check_bot_status(self):
        """Überprüft den Status des Trading Bots"""
        try:
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
            
            # Hauptorder
            result = self.make_request("POST", "/v5/order/create", "", json_data=params)
            
            # Erfolgreich?
            if result['success'] and result['data'].get('retCode') == 0:
                order_id = result['data']['result']['orderId']
                
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
                        self.make_request("POST", "/v5/order/create", "", json_data=sl_params)
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
                        self.make_request("POST", "/v5/order/create", "", json_data=tp_params)
                    except Exception as tp_error:
                        print(f"Take-Profit Order Error: {str(tp_error)}")
                
                # Erfolgreich zurückgeben
                return {
                    'success': True,
                    'order_id': order_id,
                    'message': f"{side} Order für {quantity} {symbol} platziert"
                }
            else:
                # Fehler im Hauptorder
                error_data = result.get('data', {})
                error_code = error_data.get('retCode', 'Unknown')
                error_msg = error_data.get('retMsg', 'Unknown error')
                return {
                    'success': False,
                    'error': f"Order fehlgeschlagen: [{error_code}] {error_msg}"
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def get_dashboard_data(self):
        """Kombinierte Daten für Dashboard"""
        balance_data = self.get_wallet_balance()
        price_data = self.get_btc_price()
        live_ticker_data = self.get_live_ticker()
        order_book_data = self.get_order_book()
        position_data = self.check_open_positions()
        
        # Explizit Kline-Daten holen
        kline_data = self.get_kline_data(symbol='BTCUSDT', interval='5', limit=100)
        
        # Bot Status prüfen (Dateipfad und Process ID)
        bot_status = self.check_bot_status()
        
        # Erfolgreiche API-Verbindung prüfen
        api_success = balance_data['success'] and price_data['success']
        
        if api_success:
            # Auch wenn einige andere Daten fehlen, geben wir die Hauptdaten zurück
            response = {
                'portfolio_value': balance_data.get('total_usdt_value', 0),
                'balances': balance_data.get('balances', {}),
                'btc_price': price_data.get('price', 0),
                'btc_change_24h': price_data.get('change_24h', 0),
                'btc_high_24h': price_data.get('high_24h', 0),
                'btc_low_24h': price_data.get('low_24h', 0),
                'bot_status': bot_status,
                'api_status': 'CONNECTED',
                'account_type': 'TESTNET' if self.testnet else 'MAINNET',
                'success': True
            }
            
            # Kline-Daten hinzufügen
            if kline_data.get('success', False):
                response['kline_data'] = kline_data.get('data', None)
            
            # Zusätzliche Daten, falls verfügbar
            if live_ticker_data.get('success', False):
                response.update({
                    'bid': live_ticker_data.get('bid', 0),
                    'ask': live_ticker_data.get('ask', 0),
                    'btc_volume_24h': live_ticker_data.get('volume_24h', 0),
                })
                
            if order_book_data.get('success', False):
                response.update({
                    'order_book_bids': order_book_data.get('bids', []),
                    'order_book_asks': order_book_data.get('asks', []),
                })
                
            if position_data.get('success', False):
                response.update({
                    'open_positions': position_data.get('open_positions', False),
                    'positions': position_data.get('positions', {}),
                })
                
            return response
            
        else:
            error_details = {
                'balance_error': balance_data.get('error', 'N/A') if not balance_data.get('success', False) else 'None',
                'price_error': price_data.get('error', 'N/A') if not price_data.get('success', False) else 'None',
            }
            print(f"Dashboard Data Fetch Error Details: {error_details}")
            return {
                'success': False,
                'api_status': 'ERROR',
                'error': f"Failed to fetch all dashboard data: {error_details}"
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
        print(f"Portfolio Value: ${result.get('portfolio_value', 0):.2f}")
        print(f"BTC Price: ${result.get('btc_price', 0):,.2f}")
        print(f"24h Change: {result.get('btc_change_24h', 0):+.2f}%")
        print(f"Account: {result.get('account_type', 'Unknown')}")
        
        print("\nBalances:")
        for coin, amount in result.get('balances', {}).items():
            if coin == 'USDT':
                print(f"   {coin}: {amount:.2f}")
            else:
                print(f"   {coin}: {amount:.6f}")
        
        if 'bid' in result and 'ask' in result:
            print("\nLive Ticker Data:")
            print(f"  Bid: {result.get('bid', 0):.2f}")
            print(f"  Ask: {result.get('ask', 0):.2f}")
        
        if 'order_book_bids' in result:
            print("\nOrder Book Bids (first 5):")
            for bid in result.get('order_book_bids', [])[:5]:
                print(f"  Price: {bid[0]:.2f}, Size: {bid[1]:.4f}")
            
        if 'order_book_asks' in result:
            print("\nOrder Book Asks (first 5):")
            for ask in result.get('order_book_asks', [])[:5]:
                print(f"  Price: {ask[0]:.2f}, Size: {ask[1]:.4f}")
            
        if 'kline_data' in result and not result['kline_data'].empty:
            print("\nKline Data (last 5 rows):")
            print(result['kline_data'].tail())

        if 'open_positions' in result:
            print(f"\nOpen Positions: {result['open_positions']}")
            
    else:
        print("\nAPI Connection Failed!")
        print(f"Error: {result.get('error', 'Unknown error')}")


if __name__ == "__main__":
    test_api()
