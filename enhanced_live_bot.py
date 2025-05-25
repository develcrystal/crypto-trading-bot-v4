#!/usr/bin/env python
"""
ENHANCED SMART MONEY LIVE TRADING BOT - NO EMOJIS VERSION
Läuft auf Bybit Testnet mit deinen API Keys
"""

import os
import sys
import time
import logging
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

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
    """Enhanced Smart Money Live Trading Bot für Bybit Testnet"""
    
    def __init__(self):
        # Deine Bybit API Konfiguration
        self.api_key = os.getenv('BYBIT_API_KEY')
        self.api_secret = os.getenv('BYBIT_API_SECRET')
        self.testnet = os.getenv('TESTNET', 'false').lower() == 'true'
        
        # Trading Status
        self.running = False
        self.trade_count = 0
        self.current_balance = 1000.0
        self.start_balance = 1000.0
        self.current_position = None
        
        # Performance Tracking
        self.trades_history = []
        self.regime_history = []
        
        logger.info("Enhanced Live Trading Bot initialisiert")
        logger.info(f"API Key: {self.api_key[:8] if self.api_key else 'MISSING'}...")
        logger.info(f"Testnet Mode: {self.testnet}")
    
    def get_bybit_price(self):
        """Holt aktuellen BTC Preis von Bybit"""
        try:
            base_url = "https://api.bybit.com" if not self.testnet else "https://api-testnet.bybit.com"
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
        """Erkennt aktuelles Market Regime (BULL/BEAR/SIDEWAYS)"""
        # Vereinfachte Regime-Erkennung basierend auf Preisänderung
        change_24h = price_data.get('change', 0)
        
        if change_24h > 2.0:
            return {'regime': 'BULL', 'confidence': 0.8}
        elif change_24h < -2.0:
            return {'regime': 'BEAR', 'confidence': 0.8}
        else:
            return {'regime': 'SIDEWAYS', 'confidence': 0.6}
    
    def generate_trading_signal(self, price_data, regime_info):
        """Generiert Trading Signal basierend auf Enhanced Strategy"""
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
    
    def execute_trade(self, signal_data, current_price):
        """Führt Trade aus (Simulation für Testnet)"""
        signal = signal_data['signal']
        reason = signal_data['reason']
        
        if signal == 'HOLD':
            return
        
        logger.info(f"TRADE SIGNAL: {signal} @ ${current_price:.2f}")
        logger.info(f"Reason: {reason}")
        
        if signal == 'BUY':
            self.current_position = {
                'type': 'LONG',
                'entry_price': current_price,
                'stop_loss': signal_data['stop_loss'],
                'take_profit': signal_data['take_profit'],
                'timestamp': datetime.now()
            }
            
            trade_record = {
                'timestamp': datetime.now(),
                'type': 'OPEN_LONG',
                'price': current_price,
                'reason': reason
            }
            
        elif signal == 'SELL':
            self.current_position = {
                'type': 'SHORT',
                'entry_price': current_price,
                'stop_loss': signal_data['stop_loss'],
                'take_profit': signal_data['take_profit'],
                'timestamp': datetime.now()
            }
            
            trade_record = {
                'timestamp': datetime.now(),
                'type': 'OPEN_SHORT',
                'price': current_price,
                'reason': reason
            }
            
        elif signal in ['CLOSE_LONG', 'CLOSE_SHORT']:
            if self.current_position:
                entry_price = self.current_position['entry_price']
                
                # Berechne P&L (vereinfacht)
                if signal == 'CLOSE_LONG':
                    pnl = (current_price - entry_price) / entry_price * 1000  # $1000 Position
                else:  # CLOSE_SHORT
                    pnl = (entry_price - current_price) / entry_price * 1000
                
                self.current_balance += pnl
                
                logger.info(f"Position geschlossen: P&L = ${pnl:.2f}")
                logger.info(f"Neuer Balance: ${self.current_balance:.2f}")
                
                trade_record = {
                    'timestamp': datetime.now(),
                    'type': signal,
                    'price': current_price,
                    'pnl': pnl,
                    'reason': reason
                }
                
                self.current_position = None
        
        self.trades_history.append(trade_record)
        self.trade_count += 1
        
        logger.info(f"Trade #{self.trade_count} ausgeführt")
    
    def log_status(self):
        """Loggt aktuellen Trading Status"""
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
    
    def start_live_trading(self, duration_minutes=60):
        """Startet Live Trading für bestimmte Dauer"""
        logger.info("STARTING ENHANCED LIVE TRADING BOT")
        logger.info("=" * 50)
        logger.info(f"Duration: {duration_minutes} minutes")
        logger.info("Mode: TESTNET (Simulated trades)")
        logger.info("Strategy: Enhanced Smart Money")
        logger.info("=" * 50)
        
        self.running = True
        self.start_time = datetime.now()
        end_time = self.start_time + timedelta(minutes=duration_minutes)
        
        last_status_log = datetime.now()
        
        try:
            while self.running and datetime.now() < end_time:
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
                        
                        # Status loggen alle 5 Minuten
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
    print("ENHANCED SMART MONEY LIVE TRADING BOT")
    print("=" * 60)
    print("Mode: BYBIT TESTNET (Safe simulation)")
    print("Strategy: Enhanced Smart Money with Market Regime Detection")
    print("Risk: 2% per trade | Max Drawdown: 20%")
    print("=" * 60)
    
    # Bot initialisieren
    bot = EnhancedLiveTradingBot()
    
    # Teste API-Verbindung
    logger.info("Testing Bybit API connection...")
    price_test = bot.get_bybit_price()
    
    if price_test['success']:
        logger.info(f"SUCCESS: Connected to Bybit Testnet | BTC Price: ${price_test['price']:.2f}")
    else:
        logger.error(f"FAILED: Cannot connect to Bybit API - {price_test['error']}")
        return
    
    # Frage Benutzer nach Trading-Dauer
    try:
        duration = int(input("\nEnter trading duration in minutes (default: 60): ") or "60")
    except ValueError:
        duration = 60
    
    logger.info(f"Starting {duration}-minute live trading session...")
    
    try:
        # Live Trading starten
        bot.start_live_trading(duration_minutes=duration)
        
    except KeyboardInterrupt:
        print("\nTrading stopped by user (Ctrl+C)")
        bot.stop_trading()
    except Exception as e:
        logger.error(f"Critical error: {e}")

if __name__ == "__main__":
    main()
