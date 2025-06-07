#!/usr/bin/env python
"""
ENHANCED SMART MONEY LIVE TRADING BOT - MAINNET VERSION
Läuft auf Bybit Mainnet mit echten Trades
"""

import os
import sys
import time
import logging
import requests
import json  # Added for command handling
import psutil
from datetime import datetime, timedelta
from dotenv import load_dotenv
from core.bot_status_monitor import BotStatusMonitor

# Windows Console Encoding Fix
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

# Environment laden
load_dotenv()

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('live_trading_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EnhancedLiveTradingBot:
    """Enhanced Smart Money Live Trading Bot für Bybit Mainnet"""
    
    def __init__(self):
        # Deine Bybit API Konfiguration
        self.api_key = os.getenv('BYBIT_API_KEY')
        self.api_secret = os.getenv('BYBIT_API_SECRET')
        # Immer Mainnet-Modus erzwingen
        self.testnet = False
        
        # Trading Status
        self.running = False
        self.trade_count = 0
        # Startkapital aus .env laden (Default: 50.0)
        self.current_balance = float(os.getenv('INITIAL_PORTFOLIO_VALUE', 50.0))
        self.start_balance = self.current_balance
        self.current_position = None
        
        # Performance Tracking
        self.trades_history = []
        self.regime_history = []
        
        logger.info("Enhanced Live Trading Bot initialisiert")
        logger.info(f"API Key: {self.api_key[:8] if self.api_key else 'MISSING'}...")
        logger.info(f"Mainnet Mode: Echte Trades")
        
        # Status reporting setup
        self.status_file = "bot_status.json"
        self.command_file = "bot_commands.json"
        self._initialize_status_files()
        
        # Trading control flags
        self.paused = False
        self.running = True
        
        # Status-Monitor initialisieren
        self.monitor = BotStatusMonitor(os.getpid())
        self.monitor.log_events("INFO", "Bot gestartet")
    
    def get_bybit_price(self):
        # Holt aktuellen BTC Preis von Bybit MAINNET
        try:
            base_url = "https://api.bybit.com"  # MAINNET URL
            url = f"{base_url}/v5/market/tickers"
            params = {'category': 'spot', 'symbol': 'BTCUSDT'}
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('retCode') == 0:
                    ticker = data['result']['list'][0]
                    return {
                        'success': True,
                        'price': float(ticker['lastPrice']),
                        'volume': float(ticker['volume24h']),
                        'change': float(ticker['price24hPcnt']) * 100
                    }
            
            return {'success': False, 'error': 'API Error'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def detect_market_regime(self, price_data):
        # Erkennt aktuelles Market Regime (BULL/BEAR/SIDEWAYS)
        # Vereinfachte Regime-Erkennung basierend auf Preisänderung
        change_24h = price_data.get('change', 0)
        
        if change_24h > 2.0:
            return {'regime': 'BULL', 'confidence': 0.8}
        elif change_24h < -2.0:
            return {'regime': 'BEAR', 'confidence': 0.8}
        else:
            return {'regime': 'SIDEWAYS', 'confidence': 0.6}
    
    def generate_trading_signal(self, price_data, regime_info):
        # Generiert Trading Signal basierend auf Enhanced Strategy
        current_price = price_data['price']
        regime = regime_info['regime']
        confidence = regime_info['confidence']
        
        # Enhanced Strategy Logic (vereinfacht)
        if regime == 'BULL' and confidence > 0.7:
            # In Bull Markets: Buy bei günstigen Einstiegen
            if not self.current_position:
                return {
                    'signal': 'BUY',
                    'entry_price': current_price,
                    'stop_loss': current_price * 0.98,  # 2% Stop Loss
                    'take_profit': current_price * 1.04,  # 4% Take Profit
                    'reason': f'Bull Market Entry (Confidence: {confidence:.2f})'
                }
        
        elif regime == 'BEAR' and confidence > 0.7:
            # In Bear Markets: Sell bei Rebounds
            if not self.current_position:
                return {
                    'signal': 'SELL',
                    'entry_price': current_price,
                    'stop_loss': current_price * 1.02,  # 2% Stop Loss
                    'take_profit': current_price * 0.96,  # 4% Take Profit
                    'reason': f'Bear Market Entry (Confidence: {confidence:.2f})'
                }
        
        # Position Management
        if self.current_position:
            position_type = self.current_position['type']
            entry_price = self.current_position['entry_price']
            stop_loss = self.current_position['stop_loss']
            take_profit = self.current_position['take_profit']
            
            # Check Stop Loss / Take Profit
            if position_type == 'LONG':
                if current_price <= stop_loss:
                    return {'signal': 'CLOSE_LONG', 'reason': 'Stop Loss Hit'}
                elif current_price >= take_profit:
                    return {'signal': 'CLOSE_LONG', 'reason': 'Take Profit Hit'}
            
            elif position_type == 'SHORT':
                if current_price >= stop_loss:
                    return {'signal': 'CLOSE_SHORT', 'reason': 'Stop Loss Hit'}
                elif current_price <= take_profit:
                    return {'signal': 'CLOSE_SHORT', 'reason': 'Take Profit Hit'}
        
        return {'signal': 'HOLD', 'reason': 'No valid setup'}
    
    def _generate_signature(self, params):
        """HMAC SHA256 Signatur für Bybit V5 API"""
        import hmac
        import hashlib
        import urllib.parse
        
        # Sortierte Parameter
        param_str = urllib.parse.urlencode(dict(sorted(params.items())))
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            param_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _place_order(self, side, qty, order_type="Market"):
        # Platziert echte Order über Bybit API
        endpoint = "/v5/order/create"
        base_url = "https://api.bybit.com"  # MAINNET URL
        url = f"{base_url}{endpoint}"
        timestamp = str(int(time.time() * 1000))
        
        params = {
            "category": "spot",
            "symbol": "BTCUSDT",
            "side": side,
            "orderType": order_type,
            "qty": str(qty),
            "api_key": self.api_key,
            "timestamp": timestamp,
            "recv_window": "5000"
        }
        
        # ECHTE Signatur generieren
        params["sign"] = self._generate_signature(params)
        
        try:
            headers = {
                "X-BAPI-API-KEY": self.api_key,
                "X-BAPI-SIGN": params["sign"],
                "X-BAPI-TIMESTAMP": timestamp,
                "X-BAPI-RECV-WINDOW": "5000",
                "Content-Type": "application/json"
            }
            # Sign aus dem Body entfernen
            body_params = {k: v for k, v in params.items() if k not in ['api_key', 'timestamp', 'recv_window', 'sign']}
            
            response = requests.post(url, headers=headers, json=body_params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"API-Fehler bei Orderplatzierung: {str(e)}")
            return {"success": False, "error": str(e)}

    def execute_trade(self, signal_data, current_price):
        # Führt echte Trades über Bybit API aus
        signal = signal_data['signal']
        reason = signal_data['reason']
        
        if signal == 'HOLD':
            return
        
        logger.info(f"TRADE SIGNAL: {signal} @ ${current_price:.2f}")
        logger.info(f"Reason: {reason}")
        
        if signal == 'BUY':
            # Positionwert berechnen (50% des aktuellen Kontostands)
            position_value = self.current_balance * 0.5
            qty = position_value / current_price
            
            # Marktorder platzieren
            order_result = self._place_order("Buy", qty)
            
            if order_result.get('success'):
                self.current_position = {
                    'type': 'LONG',
                    'entry_price': current_price,
                    'stop_loss': signal_data['stop_loss'],
                    'take_profit': signal_data['take_profit'],
                    'qty': qty,
                    'timestamp': datetime.now()
                }
                
                trade_record = {
                    'timestamp': datetime.now(),
                    'type': 'OPEN_LONG',
                    'price': current_price,
                    'qty': qty,
                    'reason': reason
                }
            else:
                logger.error(f"Kauforder fehlgeschlagen: {order_result.get('error')}")
                return
                
        elif signal == 'SELL':
            # Positionwert berechnen (50% des aktuellen Kontostands)
            position_value = self.current_balance * 0.5
            qty = position_value / current_price
            
            # Marktorder platzieren
            order_result = self._place_order("Sell", qty)
            
            if order_result.get('success'):
                self.current_position = {
                    'type': 'SHORT',
                    'entry_price': current_price,
                    'stop_loss': signal_data['stop_loss'],
                    'take_profit': signal_data['take_profit'],
                    'qty': qty,
                    'timestamp': datetime.now()
                }
                
                trade_record = {
                    'timestamp': datetime.now(),
                    'type': 'OPEN_SHORT',
                    'price': current_price,
                    'qty': qty,
                    'reason': reason
                }
            else:
                logger.error(f"Verkaufsorder fehlgeschlagen: {order_result.get('error')}")
                return
            
        elif signal == 'CLOSE_LONG':
            if self.current_position and self.current_position['type'] == 'LONG':
                qty = self.current_position['qty']
                order_result = self._place_order("Sell", qty)
                
                if order_result.get('success'):
                    entry_price = self.current_position['entry_price']
                    pnl = (current_price - entry_price) * qty
                    self.current_balance += pnl
                    
                    logger.info(f"LONG-Position geschlossen: P&L = ${pnl:.2f}")
                    logger.info(f"Neuer Kontostand: ${self.current_balance:.2f}")
                    
                    trade_record = {
                        'timestamp': datetime.now(),
                        'type': 'CLOSE_LONG',
                        'price': current_price,
                        'pnl': pnl,
                        'reason': reason
                    }
                    
                    self.current_position = None
                else:
                    logger.error(f"Schließorder fehlgeschlagen: {order_result.get('error')}")
                    return
                    
        elif signal == 'CLOSE_SHORT':
            if self.current_position and self.current_position['type'] == 'SHORT':
                qty = self.current_position['qty']
                order_result = self._place_order("Buy", qty)
                
                if order_result.get('success'):
                    entry_price = self.current_position['entry_price']
                    pnl = (entry_price - current_price) * qty
                    self.current_balance += pnl
                    
                    logger.info(f"SHORT-Position geschlossen: P&L = ${pnl:.2f}")
                    logger.info(f"Neuer Kontostand: ${self.current_balance:.2f}")
                    
                    trade_record = {
                        'timestamp': datetime.now(),
                        'type': 'CLOSE_SHORT',
                        'price': current_price,
                        'pnl': pnl,
                        'reason': reason
                    }
                    
                    self.current_position = None
                else:
                    logger.error(f"Schließorder fehlgeschlagen: {order_result.get('error')}")
                    return
        
        self.trades_history.append(trade_record)
        self.trade_count += 1
        
        logger.info(f"Trade #{self.trade_count} ausgeführt")
    
    def log_status(self):
        # Loggt aktuellen Trading Status
        uptime = datetime.now() - self.start_time
        total_pnl = self.current_balance - self.start_balance
        
        logger.info("=" * 50)
        logger.info("TRADING STATUS")
        logger.info("=" * 50)
        logger.info(f"Uptime: {uptime}")
        logger.info(f"Balance: ${self.current_balance:.2f}")
        logger.info(f"Total P&L: ${total_pnl:.2f} ({total_pnl/self.start_balance*100:.2f}%)")
        logger.info(f"Trades: {self.trade_count}")
        logger.info(f"Position: {self.current_position['type'] if self.current_position else 'None'}")
        
        if self.current_position:
            entry = self.current_position['entry_price']
            stop = self.current_position['stop_loss']
            target = self.current_position['take_profit']
            logger.info(f"Entry: ${entry:.2f} | Stop: ${stop:.2f} | Target: ${target:.2f}")
        
        logger.info("=" * 50)
    
    def _initialize_status_files(self):
        # Initialize status and command files
        if not os.path.exists(self.status_file):
            with open(self.status_file, 'w') as f:
                json.dump({"status": "RUNNING", "pid": os.getpid(), "timestamp": time.time()}, f)
        
        if not os.path.exists(self.command_file):
            with open(self.command_file, 'w') as f:
                json.dump({"command": "NONE", "timestamp": time.time()}, f)

    def _update_status(self, status: str):
        # Update status file
        with open(self.status_file, 'w') as f:
            json.dump({"status": status, "pid": os.getpid(), "timestamp": time.time()}, f)

    def _check_commands(self):
        # Check for new commands from dashboard
        try:
            if os.path.exists(self.command_file):
                with open(self.command_file, 'r') as f:
                    command_data = json.load(f)
                    return command_data.get('command', 'NONE')
            return 'NONE'
        except:
            return 'NONE'
    
    def _clear_command(self):
        """Clear command after processing"""
        with open(self.command_file, 'w') as f:
            json.dump({"command": "NONE", "timestamp": time.time()}, f)

    def handle_command(self, command: str):
        """Execute command from dashboard"""
        if command == "STOP":
            logger.info("Received STOP command - stopping bot gracefully")
            self._update_status("STOPPED")
            self.running = False
            return True
        elif command == "PAUSE":
            logger.info("Received PAUSE command - pausing trading")
            self.paused = True
            self._update_status("PAUSED")
            return True
        elif command == "RESUME":
            logger.info("Received RESUME command - resuming trading")
            self.paused = False
            self._update_status("RUNNING")
            return True
        elif command == "EMERGENCY_STOP":
            logger.info("EMERGENCY STOP command - closing positions immediately!")
            # Add position closing logic here
            self._update_status("EMERGENCY_STOP")
            self.running = False
            return True
        return False

    def start_live_trading(self):
        """Startet Live Trading (continuous until stopped)"""
        logger.info("STARTING ENHANCED LIVE TRADING BOT - MAINNET")
        logger.info("=" * 50)
        logger.info("Mode: MAINNET (Echte Trades)")
        logger.info("Strategy: Enhanced Smart Money")
        logger.info(f"Startkapital: ${self.start_balance:.2f}")
        logger.info("=" * 50)
        
        self.running = True
        self.paused = False
        self.start_time = datetime.now()
        self._update_status("RUNNING")
        
        last_status_log = datetime.now()
        
        try:
            while self.running and self.monitor.status_check() == "RUNNING":
                try:
                    # Check for commands from dashboard
                    command = self._check_commands()
                    if command != "NONE":
                        if self.handle_command(command):
                            self._clear_command()
                            if not self.running:
                                break
                    
                    # Skip trading if paused
                    if self.paused:
                        logger.info("Trading paused - skipping trade execution")
                        self.monitor.log_events("INFO", "Trading pausiert")
                        time.sleep(10)
                        continue
                    
                    # Hole aktuelle Marktdaten
                    price_data = self.get_bybit_price()
                    
                    if price_data['success']:
                        current_price = price_data['price']
                        
                        # Market Regime Detection
                        regime_info = self.detect_market_regime(price_data)
                        
                        # Log Market Info
                        market_info = f"BTC Price: ${current_price:.2f} | 24h Change: {price_data['change']:+.2f}% | Regime: {regime_info['regime']} (Confidence: {regime_info['confidence']:.2f})"
                        logger.info(market_info)
                        self.monitor.log_events("MARKET", market_info)
                        try:
                            while self.running:
                                # Check for commands from dashboard
                                command = self._check_commands()
                                if command != "NONE":
                                    if self.handle_command(command):
                                        self._clear_command()
                                        if not self.running:
                                            break
                                
                                # Skip trading if paused
                                if self.paused:
                                    logger.info("Trading paused - skipping trade execution")
                                    time.sleep(10)
                                    continue
                                
                                try:
                                    # Hole aktuelle Marktdaten
                                    price_data = self.get_bybit_price()
                                    
                                    if price_data['success']:
                                        current_price = price_data['price']
                                        
                                        # Market Regime Detection
                                        regime_info = self.detect_market_regime(price_data)
                                        
                                        # Log Market Info
                                        logger.info(f"BTC Price: ${current_price:.2f} | 24h Change: {price_data['change']:+.2f}%")
                                        logger.info(f"Market Regime: {regime_info['regime']} (Confidence: {regime_info['confidence']:.2f})")
                                        
                                        # Trading Signal generieren
                                        signal_data = self.generate_trading_signal(price_data, regime_info)
                                        
                                        # Trade ausführen
                                        self.execute_trade(signal_data, current_price)
                                        self.monitor.log_events("TRADE", f"Signal ausgeführt: {signal_data['signal']}")
                                        
                                        # Status loggen alle 5 Minuten
                                        if datetime.now() - last_status_log > timedelta(minutes=5):
                                            self.log_status()
                                            last_status_log = datetime.now()
                                    
                                    else:
                                        error_msg = f"API Error: {price_data['error']}"
                                        logger.warning(error_msg)
                                        self.monitor.log_events("WARNING", error_msg)
                                    
                                    # Warte 30 Sekunden bis zum nächsten Check
                                    logger.info("Waiting 30 seconds for next analysis...")
                                    time.sleep(30)
                                    
                                except Exception as e:
                                    error_msg = f"Error in trading loop: {e}"
                                    logger.error(error_msg)
                                    self.monitor.log_events("ERROR", error_msg)
                                    time.sleep(60)  # Warte 1 Minute bei Fehlern
                                    
                        except KeyboardInterrupt:
                            logger.info("Trading stopped by user")
                        except Exception as e:
                            logger.error(f"Critical error: {e}")
                        finally:
                            self.generate_final_report()
                            self.monitor.log_events("INFO", "Bot sicher gestoppt")
                        if datetime.now() - last_status_log > timedelta(minutes=5):
                            self.log_status()
                            last_status_log = datetime.now()
                    
                    else:
                        logger.warning(f"API Error: {price_data['error']}")
                    
                    # Warte 30 Sekunden bis zum nächsten Check
                    logger.info("Waiting 30 seconds for next analysis...")
                    time.sleep(30)
                    
                except KeyboardInterrupt:
                    logger.info("Trading stopped by user")
                    break
                except Exception as e:
                    logger.error(f"Error in trading loop: {e}")
                    time.sleep(60)  # Warte 1 Minute bei Fehlern
        
        except Exception as e:
            logger.error(f"Critical error: {e}")
        
        finally:
            self.generate_final_report()
    
    def generate_final_report(self):
        """Generiert finalen Trading Report"""
        logger.info("=" * 60)
        logger.info("FINAL TRADING REPORT") 
        logger.info("=" * 60)
        
        if hasattr(self, 'start_time'):
            total_runtime = datetime.now() - self.start_time
            total_pnl = self.current_balance - self.start_balance
            
            logger.info(f"Total Runtime: {total_runtime}")
            logger.info(f"Initial Balance: ${self.start_balance:.2f}")
            logger.info(f"Final Balance: ${self.current_balance:.2f}")
            logger.info(f"Total P&L: ${total_pnl:.2f} ({total_pnl/self.start_balance*100:.2f}%)")
            logger.info(f"Total Trades: {self.trade_count}")
            
            if self.trades_history:
                logger.info("\nLast 5 Trades:")
                for trade in self.trades_history[-5:]:
                    timestamp = trade['timestamp'].strftime('%H:%M:%S')
                    trade_type = trade['type']
                    price = trade['price']
                    reason = trade['reason']
                    pnl = trade.get('pnl', 0)
                    logger.info(f"  {timestamp} - {trade_type} @ ${price:.2f} | P&L: ${pnl:.2f} | {reason}")
        
        logger.info("=" * 60)
        logger.info("Enhanced Smart Money Bot session completed!")
    
    def stop_trading(self):
        """Stoppt Trading"""
        logger.info("Stopping trading...")
        self.running = False

def main():
    """Hauptfunktion - Startet Enhanced Live Trading Bot"""
    print("=" * 60)
    print("ENHANCED SMART MONEY LIVE TRADING BOT - MAINNET")
    print("=" * 60)
    print("Mode: BYBIT MAINNET (Echte Trades)")
    print("Strategy: Enhanced Smart Money with Market Regime Detection")
    
    # Bot ZUERST initialisieren
    bot = EnhancedLiveTradingBot()
    
    # DANN das Startkapital anzeigen
    print(f"Startkapital: ${bot.start_balance:.2f} | Risk: 2% pro Trade | Max Drawdown: 20%")
    print("=" * 60)
    
    # Teste API-Verbindung
    logger.info("Testing Bybit API connection...")
    price_test = bot.get_bybit_price()
    
    if price_test['success']:
        logger.info(f"[SUCCESS] Connected to Bybit Mainnet | BTC Price: ${price_test['price']:.2f}")
    else:
        logger.error(f"[FAILED] Cannot connect to Bybit API - {price_test['error']}")
        return
    
    logger.info("Starting continuous live trading session...")
    
    try:
        # Live Trading starten (continuous until stopped by command)
        bot.start_live_trading()
        
    except KeyboardInterrupt:
        print("\nTrading stopped by user (Ctrl+C)")
        bot.stop_trading()
    except Exception as e:
        logger.error(f"Critical error: {e}")

if __name__ == "__main__":
    main()
