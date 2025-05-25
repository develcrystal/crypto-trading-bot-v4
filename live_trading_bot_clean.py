#!/usr/bin/env python
"""
LIVE BYBIT TRADING BOT - ENHANCED SMART MONEY STRATEGY
Mit ECHTEN API Credentials und MAINNET TRADING
"""

import requests
import time
import hashlib
import hmac
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Environment laden
load_dotenv()

# API Configuration 
api_key = os.getenv('BYBIT_API_KEY')
secret_key = os.getenv('BYBIT_API_SECRET')
testnet = os.getenv('TESTNET', 'true').lower() == 'true'

if testnet:
    base_url = "https://api-testnet.bybit.com"
    print("MODE: TESTNET")
else:
    base_url = "https://api.bybit.com"
    print("MODE: MAINNET - REAL MONEY!")

recv_window = str(5000)

class LiveBybitTradingBot:
    """Enhanced Smart Money Trading Bot mit echtem Bybit Account"""
    
    def __init__(self):
        self.api_key = api_key
        self.secret_key = secret_key
        self.running = False
        self.trades_made = 0
        self.total_profit = 0.0
        
        print("LIVE BYBIT TRADING BOT INITIALISIERT")
        print(f"API Key: {self.api_key}")
        print(f"Testnet: {testnet}")
        
    def generate_signature(self, timestamp, payload):
        """Generiert korrekte Bybit V5 Signature"""
        param_str = str(timestamp) + self.api_key + recv_window + payload
        hash_obj = hmac.new(bytes(self.secret_key, "utf-8"), param_str.encode("utf-8"), hashlib.sha256)
        return hash_obj.hexdigest()
    
    def make_request(self, method, endpoint, payload="", json_data=None):
        """Macht authentifizierten API Request"""
        timestamp = str(int(time.time() * 1000))
        
        if json_data:
            payload = json.dumps(json_data, separators=(',', ':'))
        
        signature = self.generate_signature(timestamp, payload)
        
        headers = {
            'X-BAPI-API-KEY': self.api_key,
            'X-BAPI-SIGN': signature,
            'X-BAPI-SIGN-TYPE': '2',
            'X-BAPI-TIMESTAMP': timestamp,
            'X-BAPI-RECV-WINDOW': recv_window,
            'Content-Type': 'application/json'
        }
        
        url = f"{base_url}{endpoint}"
        
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
        result = self.make_request("GET", "/v5/account/wallet-balance", "accountType=UNIFIED")
        
        if result and result.get('retCode') == 0:
            account = result['result']['list'][0]
            coins = account['coin']
            
            balances = {}
            for coin in coins:
                balance = float(coin['walletBalance'])
                if balance > 0:
                    balances[coin['coin']] = balance
            
            return balances
        return {}
    
    def get_btc_price(self):
        """Holt aktuellen BTC Preis"""
        try:
            url = f"{base_url}/v5/market/tickers"
            params = {'category': 'spot', 'symbol': 'BTCUSDT'}
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('retCode') == 0:
                    ticker = data['result']['list'][0]
                    return {
                        'price': float(ticker['lastPrice']),
                        'change_24h': float(ticker['price24hPcnt']) * 100
                    }
            return None
        except Exception as e:
            print(f"Price Error: {e}")
            return None
    
    def place_order(self, symbol, side, order_type, qty, price=None):
        """Platziert echte Order auf Bybit"""
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
        
        result = self.make_request("POST", "/v5/order/create", json_data=order_data)
        
        if result and result.get('retCode') == 0:
            order_id = result['result']['orderId']
            print(f"ORDER EXECUTED: {side} {qty} {symbol} | Order ID: {order_id}")
            self.trades_made += 1
            return {'success': True, 'order_id': order_id}
        else:
            error_msg = result.get('retMsg', 'Unknown error') if result else 'No response'
            print(f"ORDER FAILED: {error_msg}")
            return {'success': False, 'error': error_msg}
    
    def enhanced_smart_money_analysis(self, price_data):
        """Enhanced Smart Money Strategy Analysis"""
        if not price_data:
            return None
        
        current_price = price_data['price']
        change_24h = price_data['change_24h']
        
        # Enhanced Smart Money Signals
        signal = None
        confidence = 0
        
        # Strong Bullish Signal
        if change_24h > 2.0:  # BTC steigt stark
            signal = 'BUY'
            confidence = min(change_24h * 0.3, 1.0)  # Max confidence 1.0
        
        # Strong Bearish Signal
        elif change_24h < -2.0:  # BTC fällt stark
            signal = 'SELL'
            confidence = min(abs(change_24h) * 0.3, 1.0)
        
        # Moderate Signals
        elif change_24h > 1.0:
            signal = 'BUY'
            confidence = 0.4
        elif change_24h < -1.0:
            signal = 'SELL'
            confidence = 0.4
        
        if signal:
            print(f"Smart Money Signal: {signal} (Confidence: {confidence:.2f})")
            print(f"   Price: ${current_price:.2f} | 24h Change: {change_24h:+.2f}%")
        
        return {'signal': signal, 'confidence': confidence} if signal else None
    
    def execute_trade(self, signal_data, balances):
        """Führt Trade basierend auf Smart Money Signal aus"""
        signal = signal_data['signal']
        confidence = signal_data['confidence']
        
        usdt_balance = balances.get('USDT', 0)
        btc_balance = balances.get('BTC', 0)
        
        # Minimum confidence für Trading
        if confidence < 0.5:
            print(f"Signal too weak (Confidence: {confidence:.2f}) - Skipping trade")
            return
        
        if signal == 'BUY' and usdt_balance > 10:
            # BUY BTC mit USDT (50EUR = ~50 USDT)
            trade_amount = min(10, usdt_balance * 0.2)  # 20% oder max $10
            btc_qty = trade_amount / self.get_btc_price()['price']
            
            print(f"EXECUTING BUY: ${trade_amount:.2f} worth of BTC ({btc_qty:.6f} BTC)")
            result = self.place_order('BTCUSDT', 'Buy', 'Market', btc_qty)
            
            if result['success']:
                print(f"BUY ORDER SUCCESSFUL!")
        
        elif signal == 'SELL' and btc_balance > 0.0001:
            # SELL BTC für USDT
            sell_qty = min(0.001, btc_balance * 0.2)  # 20% oder max 0.001 BTC
            
            print(f"EXECUTING SELL: {sell_qty:.6f} BTC")
            result = self.place_order('BTCUSDT', 'Sell', 'Market', sell_qty)
            
            if result['success']:
                print(f"SELL ORDER SUCCESSFUL!")
    
    def run_live_trading(self, duration_minutes=60):
        """Startet Live Trading Session"""
        print("=" * 70)
        print("ENHANCED SMART MONEY LIVE TRADING GESTARTET")
        print("=" * 70)
        print(f"Dauer: {duration_minutes} Minuten")
        mode_text = "LIVE TESTNET TRADING" if testnet else "LIVE MAINNET TRADING - REAL MONEY!"
        print(f"Modus: {mode_text}")
        print(f"API: Voll funktionsfähig")
        print("=" * 70)
        
        # Initial Balance Check
        balances = self.get_account_balance()
        print(f"Starting Balance:")
        for coin, amount in balances.items():
            if coin == 'USDT':
                print(f"   {coin}: {amount:.2f}")
            else:
                print(f"   {coin}: {amount:.6f}")
        
        self.running = True
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        print(f"\nLIVE TRADING LOOP GESTARTET...")
        
        try:
            while self.running and time.time() < end_time:
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Analyzing market...")
                
                # 1. Get current price
                price_data = self.get_btc_price()
                if not price_data:
                    print("Could not get price data")
                    time.sleep(30)
                    continue
                
                # 2. Get current balances
                balances = self.get_account_balance()
                
                # 3. Enhanced Smart Money Analysis
                signal_data = self.enhanced_smart_money_analysis(price_data)
                
                # 4. Execute trade if signal found
                if signal_data:
                    self.execute_trade(signal_data, balances)
                else:
                    print("No strong signal - HOLDING")
                
                # 5. Wait before next analysis
                print("Waiting 2 minutes for next analysis...")
                time.sleep(120)  # 2 minutes between analyses
                
        except KeyboardInterrupt:
            print("\nTrading stopped by user (Ctrl+C)")
        except Exception as e:
            print(f"\nError in trading loop: {e}")
        
        finally:
            self.generate_final_report(balances)
    
    def generate_final_report(self, initial_balances):
        """Generiert finalen Trading Report"""
        print("\n" + "=" * 70)
        print("LIVE TRADING SESSION COMPLETED")
        print("=" * 70)
        
        # Final balances
        final_balances = self.get_account_balance()
        
        print("FINAL BALANCES:")
        for coin, amount in final_balances.items():
            if coin == 'USDT':
                print(f"   {coin}: {amount:.2f}")
            else:
                print(f"   {coin}: {amount:.6f}")
        
        print(f"\nTRADING STATISTICS:")
        print(f"   Total Trades: {self.trades_made}")
        print(f"   Strategy: Enhanced Smart Money")
        mode_text = "LIVE TESTNET" if testnet else "LIVE MAINNET"
        print(f"   Account Status: {mode_text}")
        
        if testnet:
            print("\nCheck your Bybit Testnet account for detailed order history!")
        else:
            print("\nCheck your Bybit MAINNET account for detailed order history!")
        print("=" * 70)

def main():
    """Startet Live Trading Bot"""
    if not api_key or not secret_key:
        print("API credentials not found in .env file!")
        return
    
    print("ENHANCED SMART MONEY LIVE TRADING BOT")
    print("=" * 70)
    if testnet:
        print("This bot will make trades on your Bybit TESTNET account!")
    else:
        print("WARNING: This bot will make REAL trades on your Bybit MAINNET account!")
        print("Your 50 EUR balance will be used for actual trading.")
    print("=" * 70)
    
    # Initialize bot
    bot = LiveBybitTradingBot()
    
    # Test API connection first
    balances = bot.get_account_balance()
    if balances:
        print("API Connection successful!")
        print("Available balance:")
        for coin, amount in balances.items():
            if coin == 'USDT':
                print(f"   {coin}: {amount:.2f}")
    else:
        print("API Connection failed!")
        return
    
    # Auto-start with 8 hours (480 minutes)
    duration = 480
    print(f"Auto-starting {duration}-minute LIVE trading session...")
    if not testnet:
        print("WARNING: This will place REAL orders on your Bybit MAINNET account!")
    
    # Auto-confirm for live trading
    print("AUTO-CONFIRMING LIVE TRADING!")
    confirm = 'y'
    if confirm != 'y':
        print("Trading cancelled by user.")
        return
    
    try:
        # Start live trading
        bot.run_live_trading(duration_minutes=duration)
        
    except KeyboardInterrupt:
        print("\nTrading stopped by user (Ctrl+C)")
    except Exception as e:
        print(f"\nCritical error: {e}")

if __name__ == "__main__":
    main()
