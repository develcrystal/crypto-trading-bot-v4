#!/usr/bin/env python
"""
🚀 ENHANCED SMART MONEY LIVE TRADING BOT V2
Mit Market Regime Detection und Adaptive Trading Strategy
"""

import os
import time
import logging
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Union
from dotenv import load_dotenv

# Eigene Module importieren
from core.api_client import BybitAPI
from strategies.enhanced_smart_money import EnhancedSmartMoneyStrategy

# Environment laden
load_dotenv()

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("EnhancedLiveBot")

class EnhancedLiveTradingBot:
    """
    Enhanced Smart Money Trading Bot mit Market Regime Detection
    und direkter Bybit Trading API Integration.
    """
    
    def __init__(self, config: Dict = None):
        """
        Initialisiert den Enhanced Live Trading Bot.
        
        Args:
            config: Trading-Konfiguration (optional)
        """
        self.config = config or self.load_default_config()
        
        # API Client initialisieren
        self.api = BybitAPI(
            api_key=os.getenv('BYBIT_API_KEY'),
            api_secret=os.getenv('BYBIT_API_SECRET')
        )
        
        # Trading Strategy initialisieren
        self.strategy = EnhancedSmartMoneyStrategy(self.config)
        
        # Trading Status
        self.running = False
        self.trades_made = 0
        self.total_profit = 0.0
        self.current_position = None
        
        # Trading Symbol und Timeframe
        self.symbol = self.config.get('SYMBOL', 'BTCUSDT')
        self.timeframe = self.config.get('TIMEFRAME', '5')  # 5-Minuten Candles
        
        logger.info("Enhanced Smart Money Live Trading Bot initialisiert")
        logger.info(f"Symbol: {self.symbol} | Timeframe: {self.timeframe}m")
        logger.info(f"Testnet: {'AKTIV' if self.api.testnet else 'DEAKTIVIERT'}")
    
    def load_default_config(self) -> Dict:
        """
        Lädt die Standard-Konfiguration für die Trading-Strategie.
        
        Returns:
            Konfiguration als Dictionary
        """
        return {
            'SYMBOL': 'BTCUSDT',
            'TIMEFRAME': '5',  # 5-Minuten Candles
            'RISK_PERCENTAGE': 2.0,  # 2% Risiko pro Trade
            'MAX_DRAWDOWN': 15.0,  # 15% maximaler Drawdown
            'POSITION_SIZE': 0.01,  # Basis-Positionsgröße
            'MIN_TRADE_SIZE': 5.0,  # Minimum 5€ pro Trade
            'MAX_CONCURRENT_TRADES': 2,  # Maximal 2 offene Positionen
            'DAILY_RISK_LIMIT': 5.0,  # Max 5€ Verlust pro Tag
            
            # Smart Money Strategie Parameter
            'LIQUIDITY_FACTOR': 1.0,
            'MIN_LIQUIDITY_THRESHOLD': 1000,
            'VOLUME_THRESHOLD': 100000,  # Optimierter Wert
            'USE_VOLUME_FILTER': True,
            'USE_KEY_LEVELS': True,
            'USE_PATTERN_RECOGNITION': True,
            'USE_ORDER_FLOW': False,
            'USE_LIQUIDITY_SWEEP': False,
            
            # Enhanced Strategy Parameter
            'TREND_LOOKBACK': 50,
            'VOLATILITY_LOOKBACK': 20,
            'SIDEWAYS_THRESHOLD': 0.02,
            'MARKET_MULTIPLIERS': {
                'bull': {
                    'volume_threshold_multiplier': 0.8,
                    'risk_reward_multiplier': 1.2,
                    'liquidity_factor_multiplier': 1.1
                },
                'bear': {
                    'volume_threshold_multiplier': 1.2,
                    'risk_reward_multiplier': 0.9,
                    'liquidity_factor_multiplier': 1.3
                },
                'sideways': {
                    'volume_threshold_multiplier': 1.5,
                    'risk_reward_multiplier': 1.0,
                    'liquidity_factor_multiplier': 1.0
                }
            }
        }
    
    def get_current_position(self) -> Optional[Dict]:
        """
        Ermittelt die aktuelle offene Position für das Trading-Symbol.
        
        Returns:
            Positions-Informationen oder None, wenn keine Position offen ist
        """
        orders = self.api.get_open_orders(self.symbol)
        
        if orders['success'] and orders['orders']:
            # Es gibt offene Orders
            for order in orders['orders']:
                if order['symbol'] == self.symbol:
                    return {
                        'symbol': order['symbol'],
                        'side': order['side'],
                        'qty': float(order['qty']),
                        'order_id': order['orderId'],
                        'status': order['orderStatus']
                    }
        
        # Keine offene Position gefunden
        return None
    
    def calculate_position_size(self, entry_price: float, stop_loss: float) -> Tuple[float, float]:
        """
        Berechnet die optimale Positionsgröße basierend auf Risikomanagement.
        
        Args:
            entry_price: Einstiegspreis
            stop_loss: Stop-Loss-Preis
            
        Returns:
            Tuple mit (btc_qty, usdt_value)
        """
        # Wallet Balance holen
        balance = self.api.get_wallet_balance()
        if not balance['success']:
            logger.error(f"Konnte Wallet Balance nicht abrufen: {balance.get('error')}")
            return 0.0, 0.0
        
        # USDT Balance verwenden
        usdt_balance = balance['balances'].get('USDT', 0.0)
        
        # Risikobetrag berechnen (2% des Portfolios)
        risk_amount = usdt_balance * (self.config['RISK_PERCENTAGE'] / 100.0)
        
        # Minimaler Handelsbetrag
        min_trade = self.config.get('MIN_TRADE_SIZE', 5.0)
        
        # Stop-Loss Distanz in Prozent
        if stop_loss > 0:
            if entry_price > stop_loss:  # Long Position
                sl_distance_pct = (entry_price - stop_loss) / entry_price
            else:  # Short Position
                sl_distance_pct = (stop_loss - entry_price) / entry_price
            
            # Position basierend auf Risiko berechnen
            position_value = risk_amount / sl_distance_pct
        else:
            # Fallback: 10% des verfügbaren USDT
            position_value = usdt_balance * 0.1
        
        # Sicherstellen, dass wir über dem Minimum und unter 20% des Portfolios liegen
        position_value = max(min_trade, min(position_value, usdt_balance * 0.2))
        
        # BTC-Menge berechnen
        btc_qty = position_value / entry_price
        
        # 8 Dezimalstellen Genauigkeit
        btc_qty = round(btc_qty, 8)
        
        logger.info(f"Positionsgrößenberechnung: {btc_qty:.8f} BTC (${position_value:.2f} USDT)")
        logger.info(f"Basierend auf: Entry=${entry_price:.2f}, Stop=${stop_loss:.2f}, Risk={self.config['RISK_PERCENTAGE']}%")
        
        return btc_qty, position_value
    
    def execute_signal(self, signal: str, entry_price: float, stop_loss: float, metadata: Dict) -> Dict:
        """
        Führt ein Trading-Signal aus.
        
        Args:
            signal: Trading-Signal ("BUY", "SELL", "HOLD")
            entry_price: Einstiegspreis
            stop_loss: Stop-Loss-Preis
            metadata: Zusätzliche Informationen zum Signal
            
        Returns:
            Ausführungsergebnis
        """
        if signal not in ["BUY", "SELL"]:
            logger.info(f"Kein Trade: Signal ist {signal}")
            return {
                'success': False,
                'executed': False,
                'message': f"Kein Trade - Signal ist {signal}"
            }
        
        # Aktuelle Position prüfen
        current_position = self.get_current_position()
        
        # Position Size berechnen
        qty, usdt_value = self.calculate_position_size(entry_price, stop_loss)
        
        if qty <= 0 or usdt_value < self.config.get('MIN_TRADE_SIZE', 5.0):
            logger.warning(f"Position zu klein: {qty:.8f} BTC (${usdt_value:.2f})")
            return {
                'success': False,
                'executed': False,
                'message': f"Position zu klein: ${usdt_value:.2f}"
            }
        
        # Order ausführen
        side = signal  # "BUY" oder "SELL"
        
        # Market Order ausführen
        result = self.api.place_order(
            symbol=self.symbol,
            side=side,
            order_type='Market',
            qty=qty
        )
        
        if result['success']:
            logger.info(f"✅ {side} ORDER EXECUTED: {qty:.8f} {self.symbol}")
            logger.info(f"   Order ID: {result['order_id']} | Price: {entry_price:.2f}")
            
            # Trade-Zähler inkrementieren
            self.trades_made += 1
            
            # Aktuelle Position aktualisieren
            self.current_position = {
                'side': side,
                'qty': qty,
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'order_id': result['order_id'],
                'market_regime': metadata.get('market_regime', 'unknown')
            }
            
            return {
                'success': True,
                'executed': True,
                'order_id': result['order_id'],
                'side': side,
                'qty': qty,
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'usdt_value': usdt_value,
                'metadata': metadata
            }
        else:
            logger.error(f"❌ ORDER FAILED: {result.get('error', 'Unknown error')}")
            return {
                'success': False,
                'executed': False,
                'message': result.get('error', 'Order execution failed')
            }
    
    def analyze_market(self) -> Tuple[str, float, float, Dict]:
        """
        Analysiert den Markt mit der Enhanced Smart Money Strategy.
        
        Returns:
            Tuple mit (signal, entry_price, stop_loss, metadata)
        """
        # Marktdaten abrufen
        kline_result = self.api.get_kline_data(
            symbol=self.symbol,
            interval=self.timeframe,
            limit=100  # Ausreichend für technische Analyse
        )
        
        if not kline_result['success']:
            logger.error(f"Konnte keine Marktdaten abrufen: {kline_result.get('error')}")
            return "ERROR", 0.0, 0.0, {'error': 'Keine Marktdaten verfügbar'}
        
        # Daten in DataFrame umwandeln
        df = kline_result['data']
        
        if df.empty:
            logger.error("Leere Daten erhalten")
            return "ERROR", 0.0, 0.0, {'error': 'Leere Daten erhalten'}
        
        # Technische Analyse durchführen
        df_with_indicators = self.strategy.calculate_indicators(df)
        
        # Trading Signal generieren
        signal, entry_price, stop_loss, metadata = self.strategy.generate_signal(
            df_with_indicators, self.current_position
        )
        
        # Market Regime Information extrahieren
        latest_candle = df_with_indicators.iloc[-1]
        market_regime = latest_candle.get('market_regime', 'unknown')
        regime_confidence = latest_candle.get('regime_confidence', 0.0)
        
        # Aktuelle Preise aus letzter Kerze
        current_price = latest_candle['close']
        
        # Market Regime Logging
        logger.info(f"Markt-Regime: {market_regime.upper()} (Konfidenz: {regime_confidence:.2f})")
        logger.info(f"Angepasste Parameter:")
        logger.info(f"  - Volume Schwelle: {latest_candle.get('adjusted_volume_threshold', 'N/A')}")
        logger.info(f"  - Risk/Reward: {latest_candle.get('adjusted_risk_reward_ratio', 'N/A'):.2f}")
        
        # Signal Logging
        if signal in ['BUY', 'SELL']:
            logger.info(f"📊 Signal: {signal} bei ${entry_price:.2f}")
            logger.info(f"   Stop-Loss: ${stop_loss:.2f}")
            
            # Zusätzliche Metadata extrahieren
            filters_passed = []
            filters_failed = []
            
            if signal == 'BUY':
                filter_results = metadata.get('buy_filters_passed', {})
            else:
                filter_results = metadata.get('sell_filters_passed', {})
            
            for filter_name, passed in filter_results.items():
                if passed:
                    filters_passed.append(filter_name)
                else:
                    filters_failed.append(filter_name)
            
            logger.info(f"   Filter bestanden: {', '.join(filters_passed)}")
            if filters_failed:
                logger.info(f"   Filter nicht bestanden: {', '.join(filters_failed)}")
        else:
            logger.info(f"📊 Kein Signal: HOLD")
            
            # Grund für fehlendes Signal extrahieren
            if 'regime_filter' in metadata:
                logger.info(f"   Grund: {metadata['regime_filter']}")
            elif 'filter_results' in metadata:
                logger.info(f"   Grund: Mindestens ein Filter nicht bestanden")
        
        return signal, entry_price, stop_loss, metadata
    
    def run_live_trading(self, duration_minutes: int = 60):
        """
        Startet eine Live-Trading-Session.
        
        Args:
            duration_minutes: Dauer der Session in Minuten
        """
        logger.info("=" * 70)
        logger.info("ENHANCED SMART MONEY LIVE TRADING GESTARTET")
        logger.info("=" * 70)
        logger.info(f"⏱️ Dauer: {duration_minutes} Minuten")
        logger.info(f"💼 Symbol: {self.symbol}")
        logger.info(f"⏲️ Timeframe: {self.timeframe}m")
        logger.info(f"🔑 API: {'TESTNET' if self.api.testnet else 'MAINNET'}")
        logger.info("=" * 70)
        
        # Initial Balance Check
        balance_result = self.api.get_wallet_balance()
        if balance_result['success']:
            balances = balance_result['balances']
            logger.info(f"💰 Starting Balance:")
            for coin, amount in balances.items():
                if coin == 'USDT':
                    logger.info(f"   {coin}: {amount:.2f}")
                else:
                    logger.info(f"   {coin}: {amount:.8f}")
        else:
            logger.error(f"Konnte Wallet Balance nicht abrufen: {balance_result.get('error')}")
        
        # Trading Loop starten
        self.running = True
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        logger.info(f"\n🔄 LIVE TRADING LOOP GESTARTET...")
        
        try:
            while self.running and time.time() < end_time:
                # Aktuelle Zeit ausgeben
                current_time = datetime.now().strftime('%H:%M:%S')
                logger.info(f"\n[{current_time}] Analyzing market...")
                
                # 1. Markt analysieren
                signal, entry_price, stop_loss, metadata = self.analyze_market()
                
                # 2. Signal ausführen
                if signal in ['BUY', 'SELL']:
                    execution_result = self.execute_signal(signal, entry_price, stop_loss, metadata)
                    
                    if execution_result['success']:
                        logger.info(f"Trade erfolgreich ausgeführt")
                    else:
                        logger.warning(f"Trade konnte nicht ausgeführt werden: {execution_result.get('message')}")
                
                # 3. Auf nächste Analyse warten
                wait_time = 120  # 2 Minuten zwischen Analysen
                logger.info(f"⏳ Warte {wait_time} Sekunden bis zur nächsten Analyse...")
                time.sleep(wait_time)
                
        except KeyboardInterrupt:
            logger.info("\n⏹️ Trading gestoppt durch Benutzer (Ctrl+C)")
        except Exception as e:
            logger.error(f"\n❌ Fehler im Trading Loop: {str(e)}", exc_info=True)
        
        finally:
            self.running = False
            self.generate_final_report()
    
    def generate_final_report(self):
        """Generiert einen finalen Trading-Bericht."""
        logger.info("\n" + "=" * 70)
        logger.info("📊 LIVE TRADING SESSION BEENDET")
        logger.info("=" * 70)
        
        # Final balances
        balance_result = self.api.get_wallet_balance()
        
        if balance_result['success']:
            balances = balance_result['balances']
            logger.info("💰 FINAL BALANCES:")
            for coin, amount in balances.items():
                if coin == 'USDT':
                    logger.info(f"   {coin}: {amount:.2f}")
                else:
                    logger.info(f"   {coin}: {amount:.8f}")
        
        logger.info(f"\n📈 TRADING STATISTIKEN:")
        logger.info(f"   Durchgeführte Trades: {self.trades_made}")
        logger.info(f"   Strategy: Enhanced Smart Money mit Market Regime Detection")
        logger.info(f"   Account Status: {'TESTNET' if self.api.testnet else 'MAINNET'}")
        
        logger.info("\n🔗 Überprüfe dein Bybit Account für detaillierte Order-Historie!")
        logger.info("=" * 70)

def main():
    """Startet den Enhanced Live Trading Bot."""
    print("ENHANCED SMART MONEY LIVE TRADING BOT V2")
    print("=" * 70)
    print(f"API Mode: {'TESTNET' if os.getenv('TESTNET', 'true').lower() in ('true', '1', 'yes') else 'MAINNET'}")
    print("WARNING: Dieser Bot wird ECHTE Trades auf deinem Bybit Account ausführen!")
    print("=" * 70)
    
    # Bot initialisieren
    bot = EnhancedLiveTradingBot()
    
    # API-Verbindung testen
    balance_result = bot.api.get_wallet_balance()
    if balance_result['success']:
        print("API-Verbindung erfolgreich!")
        print("Verfügbares Guthaben:")
        for coin, amount in balance_result['balances'].items():
            if coin == 'USDT':
                print(f"   {coin}: {amount:.2f}")
            else:
                print(f"   {coin}: {amount:.8f}")
    else:
        print(f"API-Verbindung fehlgeschlagen: {balance_result.get('error', 'Unbekannter Fehler')}")
        return
    
    # Trading-Dauer abfragen
    try:
        duration = int(input(f"\nTrading-Dauer in Minuten eingeben (Standard: 60): ") or "60")
    except ValueError:
        duration = 60
    
    print(f"\nStarte {duration}-minütige LIVE Trading-Session...")
    print(f"WARNING: Dies wird ECHTE Orders auf deinem Bybit {'Testnet' if bot.api.testnet else 'Mainnet'} Account platzieren!")
    
    confirm = input("Mit Live-Trading fortfahren? (j/N): ").lower()
    if confirm != 'j':
        print("Trading abgebrochen.")
        return
    
    try:
        # Live-Trading starten
        bot.run_live_trading(duration_minutes=duration)
        
    except KeyboardInterrupt:
        print("\n⏹️ Trading gestoppt durch Benutzer (Ctrl+C)")
    except Exception as e:
        print(f"\n❌ Kritischer Fehler: {str(e)}")
        raise

if __name__ == "__main__":
    main()
