#!/usr/bin/env python
"""
REAL BYBIT ACCOUNT TRADING BOT
Arbeitet mit deinem echten Bybit Testnet Account (583.38 USDT)
"""

import os
import sys
import time
import logging
import requests
import hmac
import hashlib
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Environment laden
load_dotenv()

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('real_bybit_trading.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RealBybitTradingBot:
    """Trading Bot der mit deinem echten Bybit Testnet Account arbeitet"""
    
    def __init__(self):
        # Deine echten Bybit API Konfiguration
        self.api_key = os.getenv('BYBIT_API_KEY')
        self.api_secret = os.getenv('BYBIT_API_SECRET')
        self.base_url = "https://api-testnet.bybit.com"
        
        # Trading Status
        self.running = False
        self.trade_count = 0
        self.real_balance = 0.0
        self.initial_balance = 0.0
        self.current_position = None
        
        logger.info("Real Bybit Account Trading Bot initialisiert")
        logger.info(f"API Key: {self.api_key[:8] if self.api_key else 'MISSING'}...")
    
    def generate_signature(self, params):
        """Generiert HMAC SHA256 Signatur für authentifizierte API Calls"""
        # Parameter sortieren und als Query String formatieren
        sorted_params = '&'.join([f"{k}={v}" for k, v in sorted(params.items())])
        
        # HMAC SHA256 Signatur erstellen
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            sorted_params.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def make_authenticated_request(self, endpoint, params=None):
        """Macht authentifizierten API Call zu Bybit"""
        if params is None:
            params = {}
        
        # Timestamp und recv_window hinzufügen
        timestamp = str(int(time.time() * 1000))
        params['api_key'] = self.api_key
        params['timestamp'] = timestamp
        params['recv_window'] = '5000'
        
        # Signatur generieren
        signature = self.generate_signature(params)
        params['sign'] = signature
        
        # API Call machen
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"API Error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Request Error: {e}")
            return None
    
    def get_real_account_balance(self):
        """Holt deinen echten Bybit Testnet Account Balance"""
        try:
            # Wallet Balance API Call
            endpoint = "/v5/account/wallet-balance"
            params = {'accountType': 'UNIFIED'}
            
            response = self.make_authenticated_request(endpoint, params)
            
            if response and response.get('retCode') == 0:
                result = response.get('result', {})
                account_list = result.get('list', [])
                
                if account_list:
                    account = account_list[0]
                    coins = account.get('coin', [])
                    
                    usdt_balance = 0.0
                    btc_balance = 0.0
                    
                    for coin in coins:
                        if coin.get('coin') == 'USDT':
                            usdt_balance = float(coin.get('walletBalance', 0))
                        elif coin.get('coin') == 'BTC':
                            btc_balance = float(coin.get('walletBalance', 0))
                    
                    logger.info(f"REAL ACCOUNT: {usdt_balance:.2f} USDT + {btc_balance:.6f} BTC")
                    return {'usdt': usdt_balance, 'btc': btc_balance, 'success': True}
            
            logger.warning("Could not get account balance")
            return {'success': False}
            
        except Exception as e:
            logger.error(f"Error getting account balance: {e}")
            return {'success': False}
    
    def get_market_price(self):
        """Holt aktuellen BTC Preis (ohne Authentifizierung)"""
        try:
            url = "https://api-testnet.bybit.com/v5/market/tickers"
            params = {'category': 'spot', 'symbol': 'BTCUSDT'}
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('retCode') == 0:
                    ticker = data['result']['list'][0]
                    return {
                        'success': True,
                        'price': float(ticker['lastPrice']),
                        'change': float(ticker['price24hPcnt']) * 100
                    }
            
            return {'success': False}
            
        except Exception as e:
            logger.error(f"Error getting price: {e}")
            return {'success': False}
    
    def place_real_order(self, side, quantity, price=None):
        """Platziert echte Order auf deinem Bybit Account"""
        try:
            endpoint = "/v5/order/create"
            
            params = {
                'category': 'spot',
                'symbol': 'BTCUSDT',
                'side': side,  # 'Buy' or 'Sell'
                'orderType': 'Market',  # Market Order für schnelle Ausführung
                'qty': str(quantity)
            }
            
            if price:
                params['orderType'] = 'Limit'
                params['price'] = str(price)
                params['timeInForce'] = 'GTC'
            
            response = self.make_authenticated_request(endpoint, params)
            
            if response and response.get('retCode') == 0:
                order_id = response.get('result', {}).get('orderId')
                logger.info(f"ORDER PLACED: {side} {quantity} BTC @ Market Price | Order ID: {order_id}")
                return {'success': True, 'order_id': order_id}
            else:
                error_msg = response.get('retMsg', 'Unknown error') if response else 'No response'
                logger.error(f"Order failed: {error_msg}")
                return {'success': False, 'error': error_msg}
                
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            return {'success': False, 'error': str(e)}
    
    def analyze_and_trade(self):
        """Analysiert Markt und führt echte Trades aus"""
        # Hole aktuellen Preis
        price_data = self.get_market_price()
        if not price_data['success']:
            return
        
        current_price = price_data['price']
        change_24h = price_data['change']
        
        # Hole echten Account Balance
        balance_data = self.get_real_account_balance()
        if not balance_data['success']:
            return
        
        usdt_balance = balance_data['usdt']
        btc_balance = balance_data['btc']
        
        logger.info(f"Price: ${current_price:.2f} | 24h Change: {change_24h:+.2f}%")
        logger.info(f"Account: {usdt_balance:.2f} USDT + {btc_balance:.6f} BTC")
        
        # Trading Logic - Vereinfacht aber ECHT
        if change_24h > 1.0 and usdt_balance > 50:  # Wenn BTC steigt >1% und genug USDT vorhanden
            # BUY Signal
            buy_amount_usd = min(100, usdt_balance * 0.1)  # 10% des USDT Saldos, max $100
            btc_quantity = buy_amount_usd / current_price
            
            logger.info(f"BUY SIGNAL: Buying {btc_quantity:.6f} BTC for ~${buy_amount_usd:.2f}")
            
            # ECHTER TRADE
            order_result = self.place_real_order('Buy', btc_quantity)
            if order_result['success']:
                self.trade_count += 1
                logger.info(f"REAL TRADE #{self.trade_count} EXECUTED!")
        
        elif change_24h < -1.0 and btc_balance > 0.001:  # Wenn BTC fällt >1% und genug BTC vorhanden
            # SELL Signal
            sell_quantity = min(0.01, btc_balance * 0.1)  # 10% des BTC Saldos, max 0.01 BTC
            
            logger.info(f"SELL SIGNAL: Selling {sell_quantity:.6f} BTC at ${current_price:.2f}")
            
            # ECHTER TRADE
            order_result = self.place_real_order('Sell', sell_quantity)
            if order_result['success']:
                self.trade_count += 1
                logger.info(f"REAL TRADE #{self.trade_count} EXECUTED!")
        
        else:
            logger.info("HOLD - No strong signal or insufficient balance")
    
    def start_real_trading(self, duration_minutes=30):
        """Startet echtes Trading mit deinem Bybit Account"""
        logger.info("=" * 60)
        logger.info("STARTING REAL BYBIT ACCOUNT TRADING")
        logger.info("=" * 60)
        logger.info(f"Duration: {duration_minutes} minutes")
        logger.info("Mode: REAL BYBIT TESTNET ACCOUNT")
        logger.info("Trades: REAL ORDERS on your account")
        logger.info("=" * 60)
        
        # Teste API Verbindung
        balance_test = self.get_real_account_balance()
        if not balance_test['success']:
            logger.error("FAILED: Cannot connect to your Bybit account!")
            return
        
        logger.info(f"SUCCESS: Connected to your account - {balance_test['usdt']:.2f} USDT available")
        
        self.running = True
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        try:
            while self.running and datetime.now() < end_time:
                try:
                    # Analysiere und handle
                    self.analyze_and_trade()
                    
                    # Warte 60 Sekunden (weniger frequent für echte Trades)
                    logger.info("Waiting 60 seconds for next analysis...")
                    time.sleep(60)
                    
                except KeyboardInterrupt:
                    logger.info("Trading stopped by user")
                    break
                except Exception as e:
                    logger.error(f"Error in trading loop: {e}")
                    time.sleep(60)
        
        except Exception as e:
            logger.error(f"Critical error: {e}")
        
        finally:
            self.generate_final_report()
    
    def generate_final_report(self):
        """Generiert finalen Report mit echten Balances"""
        logger.info("=" * 60)
        logger.info("REAL TRADING SESSION COMPLETED")
        logger.info("=" * 60)
        
        # Hole finale Balance
        final_balance = self.get_real_account_balance()
        if final_balance['success']:
            logger.info(f"Final Balance: {final_balance['usdt']:.2f} USDT + {final_balance['btc']:.6f} BTC")
        
        logger.info(f"Total Real Trades Executed: {self.trade_count}")
        logger.info("Check your Bybit Testnet account for order history!")
        logger.info("=" * 60)

def main():
    """Startet echten Bybit Account Trading Bot"""
    print("=" * 60)
    print("REAL BYBIT ACCOUNT TRADING BOT")
    print("=" * 60)
    print("This bot trades with your REAL Bybit Testnet account!")
    print("Your current balance will be used for actual trades.")
    print("=" * 60)
    
    # Bot initialisieren
    bot = RealBybitTradingBot()
    
    # Teste Account-Zugriff
    balance_test = bot.get_real_account_balance()
    if balance_test['success']:
        print(f"✅ Connected to your account: {balance_test['usdt']:.2f} USDT + {balance_test['btc']:.6f} BTC")
    else:
        print("❌ Cannot access your Bybit account - check API keys!")
        return
    
    # Frage nach Trading-Dauer
    try:
        duration = int(input("\nEnter trading duration in minutes (default: 30): ") or "30")
    except ValueError:
        duration = 30
    
    print(f"\n🚀 Starting {duration}-minute REAL trading session...")
    print("⚠️  This will place REAL orders on your Bybit Testnet account!")
    
    confirm = input("Continue? (y/N): ").lower()
    if confirm != 'y':
        print("Trading cancelled.")
        return
    
    try:
        # Echtes Trading starten
        bot.start_real_trading(duration_minutes=duration)
        
    except KeyboardInterrupt:
        print("\nTrading stopped by user (Ctrl+C)")
    except Exception as e:
        logger.error(f"Critical error: {e}")

if __name__ == "__main__":
    main()
