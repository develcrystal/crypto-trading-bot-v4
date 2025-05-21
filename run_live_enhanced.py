#!/usr/bin/env python
"""
Live Trading Script mit Enhanced Smart Money Strategy für Testnet.

Dieses Script deployed die Enhanced Smart Money Strategy mit Market Regime Detection
auf Bybit Testnet für Live-Trading-Validierung.
"""

import os
import sys
import time
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
import signal
import threading
from dotenv import load_dotenv

# Lokale Module importieren
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data.data_handler import DataHandler
from exchange.bybit_api import BybitAPI
from strategies.enhanced_smart_money import EnhancedSmartMoneyStrategy
from risk.risk_manager import RiskManager
from config.config import config

# Environment laden
load_dotenv()

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('live_trading.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LiveTradingEngine:
    """
    Live Trading Engine für Enhanced Smart Money Strategy auf Testnet.
    """
    
    def __init__(self):
        """Initialisiert die Live Trading Engine."""
        self.running = False
        self.trade_count = 0
        self.start_time = datetime.now()
        self.current_position = None
        self.entry_price = 0.0
        self.stop_loss = 0.0
        self.take_profit = 0.0
        
        # Performance Tracking
        self.initial_balance = 0.0
        self.current_balance = 0.0
        self.trades_executed = []
        self.regime_history = []
        
        # Initialisiere Komponenten
        self._initialize_components()
        
        # Signal Handler für graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _initialize_components(self):
        """Initialisiert alle Trading-Komponenten."""
        logger.info("🔧 Initialisiere Live Trading Komponenten...")
        
        try:
            # API Connection
            self.exchange_api = BybitAPI(
                api_key=os.getenv('BYBIT_API_KEY'),
                api_secret=os.getenv('BYBIT_API_SECRET'),
                testnet=True  # WICHTIG: Testnet Mode
            )
            logger.info("✅ Bybit Testnet API verbunden")
            
            # Data Handler
            self.data_handler = DataHandler(self.exchange_api)
            logger.info("✅ Data Handler initialisiert")
            
            # Enhanced Strategy mit optimierter Konfiguration
            enhanced_config = self._prepare_enhanced_config()
            self.strategy = EnhancedSmartMoneyStrategy(enhanced_config)
            logger.info("✅ Enhanced Smart Money Strategy geladen")
            
            # Risk Manager
            self.risk_manager = RiskManager(
                account_balance=float(os.getenv('INITIAL_PORTFOLIO_VALUE', 1000)),
                risk_per_trade_pct=float(os.getenv('MAX_RISK_PER_TRADE', 0.02)) * 100,
                max_drawdown_pct=float(os.getenv('MAX_DRAWDOWN', 0.2)) * 100
            )
            logger.info("✅ Risk Manager initialisiert")
            
            # Initiales Balance Update
            self._update_account_balance()
            
        except Exception as e:
            logger.error(f"❌ Fehler bei Komponenten-Initialisierung: {e}")
            raise
    
    def _prepare_enhanced_config(self) -> Dict:
        """Bereitet optimierte Konfiguration für Enhanced Strategy vor."""
        enhanced_config = vars(config).copy()
        
        # Enhanced Strategy spezifische Parameter
        enhanced_config.update({
            # Market Regime Detection
            'TREND_LOOKBACK': 50,
            'VOLATILITY_LOOKBACK': 20,
            'SIDEWAYS_THRESHOLD': 0.02,
            
            # Optimierte Filter (aus vorheriger Studie)
            'USE_VOLUME_FILTER': True,
            'VOLUME_THRESHOLD': 100000,  # Optimiert
            'USE_KEY_LEVELS': True,
            'USE_PATTERN_RECOGNITION': True,
            'USE_ORDER_FLOW': False,  # Für Balance deaktiviert
            'USE_LIQUIDITY_SWEEP': False,  # Für Balance deaktiviert
            
            # Adaptive Multipliers
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
        })
        
        return enhanced_config
    
    def _update_account_balance(self):
        """Aktualisiert den Account Balance vom Exchange."""
        try:
            balance_info = self.exchange_api.get_wallet_balance()
            if balance_info:
                # Extrahiere USDT Balance
                usdt_balance = 0.0
                if 'list' in balance_info and balance_info['list']:
                    for account in balance_info['list']:
                        if 'coin' in account:
                            for coin_info in account['coin']:
                                if coin_info.get('coin') == 'USDT':
                                    usdt_balance = float(coin_info.get('walletBalance', 0))
                                    break
                
                if self.initial_balance == 0.0:
                    self.initial_balance = usdt_balance
                
                self.current_balance = usdt_balance
                self.risk_manager.update_account_balance(usdt_balance)
                
                logger.info(f"💰 Account Balance: ${usdt_balance:.2f} USDT (Testnet)")
            else:
                logger.warning("⚠️ Konnte Account Balance nicht abrufen")
                
        except Exception as e:
            logger.error(f"❌ Fehler beim Balance-Update: {e}")
    
    def _get_latest_market_data(self, symbol: str = 'BTCUSDT', timeframe: str = '1h', limit: int = 200) -> Optional[pd.DataFrame]:
        """Ruft aktuelle Marktdaten ab."""
        try:
            data = self.data_handler.get_latest_data(
                symbol=symbol,
                timeframe=timeframe,
                limit=limit
            )
            
            if data is not None and not data.empty:
                logger.debug(f"📊 Marktdaten abgerufen: {len(data)} Datenpunkte")
                return data
            else:
                logger.warning("⚠️ Keine Marktdaten verfügbar")
                return None
                
        except Exception as e:
            logger.error(f"❌ Fehler beim Datenabruf: {e}")
            return None
    
    def _analyze_market_and_generate_signal(self, data: pd.DataFrame) -> Dict:
        """Analysiert Markt und generiert Trading-Signal."""
        try:
            # Indikatoren berechnen
            data_with_indicators = self.strategy.calculate_indicators(data)
            
            # Signal generieren
            signal, entry_price, stop_loss, metadata = self.strategy.generate_signal(
                data_with_indicators, 
                self.current_position
            )
            
            # Regime-Information extrahieren
            latest_candle = data_with_indicators.iloc[-1]
            regime_info = {
                'market_regime': latest_candle.get('market_regime', 'unknown'),
                'regime_confidence': latest_candle.get('regime_confidence', 0.0),
                'adjusted_volume_threshold': latest_candle.get('adjusted_volume_threshold', 100000),
                'trend_strength': latest_candle.get('trend_strength', 0.0)
            }
            
            # Regime-History aktualisieren
            self.regime_history.append({
                'timestamp': datetime.now(),
                'regime': regime_info['market_regime'],
                'confidence': regime_info['regime_confidence'],
                'price': latest_candle['close']
            })
            
            # Nur letzte 100 Einträge behalten
            if len(self.regime_history) > 100:
                self.regime_history = self.regime_history[-100:]
            
            return {
                'signal': signal,
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'metadata': metadata,
                'regime_info': regime_info,
                'current_price': latest_candle['close'],
                'volume': latest_candle['volume']
            }
            
        except Exception as e:
            logger.error(f"❌ Fehler bei Signal-Generierung: {e}")
            return {
                'signal': 'HOLD',
                'entry_price': 0.0,
                'stop_loss': 0.0,
                'metadata': {},
                'regime_info': {},
                'current_price': 0.0,
                'volume': 0.0
            }
    
    def _execute_trade_signal(self, signal_data: Dict, symbol: str = 'BTCUSDT'):
        """Führt Trading-Signal aus (Simulation für Testnet)."""
        signal = signal_data['signal']
        entry_price = signal_data['entry_price']
        stop_loss = signal_data['stop_loss']
        regime_info = signal_data['regime_info']
        
        if signal == 'HOLD':
            return
        
        try:
            # Risk Management Validierung
            if signal in ['BUY', 'SELL']:
                validation = self.risk_manager.validate_trade(
                    entry_price=entry_price,
                    stop_loss=stop_loss,
                    symbol=symbol,
                    direction='long' if signal == 'BUY' else 'short'
                )
                
                if not validation['valid']:
                    logger.warning(f"⚠️ Trade gefiltert durch Risk Management: {validation['reasons']}")
                    return
                
                # Für Testnet: Trade simulieren statt echte Order
                logger.info(f"🎯 SIGNAL: {signal} bei ${entry_price:.2f}")
                logger.info(f"🧠 Market Regime: {regime_info.get('market_regime', 'unknown')} "
                          f"(Confidence: {regime_info.get('regime_confidence', 0):.2f})")
                logger.info(f"🛡️ Stop-Loss: ${stop_loss:.2f}")
                logger.info(f"💡 Metadata: {signal_data['metadata']}")
                
                # Trade zur Historie hinzufügen
                trade_record = {
                    'timestamp': datetime.now(),
                    'signal': signal,
                    'entry_price': entry_price,
                    'stop_loss': stop_loss,
                    'regime': regime_info.get('market_regime', 'unknown'),
                    'regime_confidence': regime_info.get('regime_confidence', 0),
                    'metadata': signal_data['metadata']
                }
                
                self.trades_executed.append(trade_record)
                self.trade_count += 1
                
                # Position tracking aktualisieren
                if signal in ['BUY', 'SELL']:
                    self.current_position = 'LONG' if signal == 'BUY' else 'SHORT'
                    self.entry_price = entry_price
                    self.stop_loss = stop_loss
                
                logger.info(f"📝 Trade #{self.trade_count} simuliert: {signal} @ ${entry_price:.2f}")
                
            elif signal in ['CLOSE_LONG', 'CLOSE_SHORT']:
                logger.info(f"🔚 Position geschlossen: {signal} @ ${entry_price:.2f}")
                self.current_position = None
                self.entry_price = 0.0
                self.stop_loss = 0.0
                
        except Exception as e:
            logger.error(f"❌ Fehler bei Trade-Ausführung: {e}")
    
    def _log_performance_status(self):
        """Loggt aktuellen Performance-Status."""
        uptime = datetime.now() - self.start_time
        
        logger.info("\n" + "="*60)
        logger.info("📊 LIVE TRADING STATUS")
        logger.info("="*60)
        logger.info(f"⏱️  Uptime: {uptime}")
        logger.info(f"💰 Balance: ${self.current_balance:.2f} (Start: ${self.initial_balance:.2f})")
        logger.info(f"📈 P&L: ${self.current_balance - self.initial_balance:.2f}")
        logger.info(f"🎯 Trades: {self.trade_count}")
        logger.info(f"📍 Position: {self.current_position or 'None'}")
        
        if self.current_position:
            logger.info(f"💸 Entry: ${self.entry_price:.2f}")
            logger.info(f"🛡️ Stop-Loss: ${self.stop_loss:.2f}")
        
        # Regime-History Summary
        if self.regime_history:
            latest_regime = self.regime_history[-1]
            logger.info(f"🧠 Current Regime: {latest_regime['regime']} "
                      f"(Confidence: {latest_regime['confidence']:.2f})")
        
        logger.info("="*60)
    
    def _signal_handler(self, signum, frame):
        """Behandelt Shutdown-Signale."""
        logger.info(f"🔴 Shutdown-Signal empfangen: {signum}")
        self.stop_trading()
    
    def start_trading(self, symbol: str = 'BTCUSDT', timeframe: str = '1h', 
                     check_interval: int = 300, duration_hours: int = 168):
        """
        Startet Live Trading.
        
        Args:
            symbol: Trading-Symbol
            timeframe: Zeitrahmen für Analyse
            check_interval: Prüfintervall in Sekunden
            duration_hours: Trading-Dauer in Stunden (Standard: 7 Tage)
        """
        logger.info("🚀 STARTE LIVE TRADING MIT ENHANCED SMART MONEY STRATEGY")
        logger.info("="*60)
        logger.info(f"📊 Symbol: {symbol}")
        logger.info(f"⏱️ Timeframe: {timeframe}")
        logger.info(f"🔄 Check Interval: {check_interval} Sekunden")
        logger.info(f"⏰ Duration: {duration_hours} Stunden")
        logger.info(f"🧪 TESTNET MODE: Simulierte Trades")
        logger.info("="*60)
        
        self.running = True
        end_time = datetime.now() + timedelta(hours=duration_hours)
        last_status_log = datetime.now()
        
        try:
            while self.running and datetime.now() < end_time:
                try:
                    # Account Balance aktualisieren
                    self._update_account_balance()
                    
                    # Marktdaten abrufen
                    market_data = self._get_latest_market_data(symbol, timeframe)
                    
                    if market_data is not None:
                        # Signal analysieren und generieren
                        signal_data = self._analyze_market_and_generate_signal(market_data)
                        
                        # Trade ausführen (simuliert)
                        self._execute_trade_signal(signal_data, symbol)
                        
                        # Status-Log alle 30 Minuten
                        if datetime.now() - last_status_log > timedelta(minutes=30):
                            self._log_performance_status()
                            last_status_log = datetime.now()
                    
                    # Warte bis zum nächsten Check
                    logger.debug(f"💤 Warte {check_interval} Sekunden...")
                    time.sleep(check_interval)
                    
                except KeyboardInterrupt:
                    logger.info("🔴 Keyboard Interrupt - Stoppe Trading...")
                    break
                except Exception as e:
                    logger.error(f"❌ Fehler im Trading-Loop: {e}")
                    time.sleep(60)  # Warte 1 Minute bei Fehlern
                    continue
            
            logger.info("🏁 Live Trading beendet")
            
        except Exception as e:
            logger.error(f"❌ Kritischer Fehler im Trading: {e}")
        finally:
            self._generate_final_report()
    
    def stop_trading(self):
        """Stoppt Live Trading."""
        logger.info("🔴 Stoppe Live Trading...")
        self.running = False
    
    def _generate_final_report(self):
        """Generiert finalen Trading-Report."""
        logger.info("\n" + "="*80)
        logger.info("📋 FINAL TRADING REPORT")
        logger.info("="*80)
        
        total_runtime = datetime.now() - self.start_time
        total_pnl = self.current_balance - self.initial_balance
        
        logger.info(f"⏱️ Total Runtime: {total_runtime}")
        logger.info(f"💰 Initial Balance: ${self.initial_balance:.2f}")
        logger.info(f"💰 Final Balance: ${self.current_balance:.2f}")
        logger.info(f"📈 Total P&L: ${total_pnl:.2f} ({total_pnl/self.initial_balance*100:.2f}%)")
        logger.info(f"🎯 Total Trades: {self.trade_count}")
        
        if self.trades_executed:
            logger.info(f"\n📊 Trade Summary:")
            for i, trade in enumerate(self.trades_executed[-5:], 1):  # Letzte 5 Trades
                logger.info(f"   {i}. {trade['timestamp'].strftime('%H:%M:%S')} - {trade['signal']} @ ${trade['entry_price']:.2f} "
                          f"(Regime: {trade['regime']})")
        
        # Regime-Analyse
        if self.regime_history:
            regimes = [r['regime'] for r in self.regime_history]
            regime_counts = {regime: regimes.count(regime) for regime in set(regimes)}
            logger.info(f"\n🧠 Regime Distribution:")
            for regime, count in regime_counts.items():
                percentage = count / len(regimes) * 100
                logger.info(f"   {regime}: {count} checks ({percentage:.1f}%)")
        
        # Speichere Report als JSON
        report_data = {
            'start_time': self.start_time.isoformat(),
            'end_time': datetime.now().isoformat(),
            'runtime_hours': total_runtime.total_seconds() / 3600,
            'initial_balance': self.initial_balance,
            'final_balance': self.current_balance,
            'total_pnl': total_pnl,
            'total_trades': self.trade_count,
            'trades_executed': [
                {**trade, 'timestamp': trade['timestamp'].isoformat()}
                for trade in self.trades_executed
            ],
            'regime_history': [
                {**regime, 'timestamp': regime['timestamp'].isoformat()}
                for regime in self.regime_history
            ]
        }
        
        report_file = f"live_trading_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(report_file, 'w') as f:
                json.dump(report_data, f, indent=2)
            logger.info(f"📄 Report gespeichert: {report_file}")
        except Exception as e:
            logger.error(f"❌ Fehler beim Speichern des Reports: {e}")
        
        logger.info("="*80)

def main():
    """Hauptfunktion für Live Trading."""
    print("🚀 ENHANCED SMART MONEY STRATEGY - LIVE TRADING")
    print("="*60)
    print("🧪 TESTNET MODE - Simulierte Trades")
    print("🧠 Market Regime Detection aktiviert")
    print("⚙️ Adaptive Parameter-Anpassung")
    print("="*60)
    
    # Trading Engine initialisieren
    try:
        engine = LiveTradingEngine()
        
        # Live Trading starten
        # Standard: 7 Tage (168 Stunden), Check alle 5 Minuten (300 Sekunden)
        engine.start_trading(
            symbol='BTCUSDT',
            timeframe='1h',
            check_interval=300,  # 5 Minuten
            duration_hours=168   # 7 Tage
        )
        
    except KeyboardInterrupt:
        print("\n🔴 Live Trading durch Benutzer gestoppt")
    except Exception as e:
        logger.error(f"❌ Kritischer Fehler: {e}")
        print(f"\n❌ Fehler beim Live Trading: {e}")

if __name__ == "__main__":
    main()
