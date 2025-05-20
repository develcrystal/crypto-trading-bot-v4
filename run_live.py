#!/usr/bin/env python
"""
Live-Trading-Script für den Crypto Trading Bot V2.

Dieses Skript führt den Trading-Bot im Echtzeit-Modus aus und handelt 
basierend auf der gewählten Strategie.
"""

import os
import argparse
import logging
import time
import signal
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Lokale Module importieren
from data.data_handler import DataHandler
from exchange.bybit_api import BybitAPI
from risk.risk_manager import RiskManager
from utils.logging import setup_logging
from config.config import config

# Strategien importieren
from strategies.bollinger_bands import BollingerBandsStrategy
from strategies.moving_average import MovingAverageStrategy
from strategies.macd import MACDStrategy
from strategies.multi_timeframe import MultiTimeframeStrategy

# Initialisiere Konfiguration
load_dotenv()

# Konfiguriere Logging
log_level = os.environ.get('LOG_LEVEL', 'INFO')
log_file = os.environ.get('LOG_FILE', 'trading_bot.log')

logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Flag für graceful shutdown
running = True

def signal_handler(sig, frame):
    """Signal-Handler für graceful shutdown."""
    global running
    logger.info("Shutdown-Signal erhalten, beende Bot nach aktuellem Zyklus...")
    running = False

def parse_args():
    """Verarbeitet Kommandozeilenargumente."""
    parser = argparse.ArgumentParser(description="Crypto Trading Bot V2 - Live Trading")
    
    # Allgemeine Parameter
    parser.add_argument('--symbol', type=str, default='BTCUSDT',
                        help='Trading-Symbol (z.B. BTCUSDT)')
    parser.add_argument('--timeframe', type=str, default='1h',
                        help='Zeitrahmen (z.B. 1h, 4h, 1d)')
    
    # Trading-Parameter
    parser.add_argument('--risk-per-trade', type=float, default=0.02,
                        help='Risiko pro Trade (0.02 = 2%)')
    parser.add_argument('--max-open-trades', type=int, default=3,
                        help='Maximale Anzahl offener Trades')
    parser.add_argument('--testnet', action='store_true', default=True,
                        help='Testnet verwenden (Standard: True)')
    
    # Strategie-Parameter
    parser.add_argument('--strategy', type=str, default='bollinger_bands',
                        choices=['bollinger_bands', 'moving_average', 'macd', 'multi_timeframe'],
                        help='Zu verwendende Handelsstrategie')
    
    # Bollinger Bands Parameter
    parser.add_argument('--bb-period', type=int, default=20,
                        help='Bollinger Bands Periode')
    parser.add_argument('--bb-std-dev', type=float, default=2.0,
                        help='Bollinger Bands Standardabweichungen')
    
    # Moving Average Parameter
    parser.add_argument('--ma-fast', type=int, default=10,
                        help='Schneller Gleitender Durchschnitt Periode')
    parser.add_argument('--ma-slow', type=int, default=30,
                        help='Langsamer Gleitender Durchschnitt Periode')
    
    # MACD Parameter
    parser.add_argument('--macd-fast', type=int, default=12,
                        help='MACD Fast Periode')
    parser.add_argument('--macd-slow', type=int, default=26,
                        help='MACD Slow Periode')
    parser.add_argument('--macd-signal', type=int, default=9,
                        help='MACD Signal Periode')
    
    # Betriebsparameter
    parser.add_argument('--interval', type=int, default=60,
                        help='Intervall zwischen Trading-Zyklen in Sekunden')
    parser.add_argument('--log-dir', type=str, default='logs',
                        help='Verzeichnis für Log-Dateien')
    
    return parser.parse_args()

def get_strategy(args):
    """Erstellt die Strategie-Instanz basierend auf den Argumenten."""
    strategy_name = args.strategy.lower()
    
    if strategy_name == 'bollinger_bands':
        return BollingerBandsStrategy(
            period=args.bb_period,
            std_dev=args.bb_std_dev
        )
    elif strategy_name == 'moving_average':
        return MovingAverageStrategy(
            fast_period=args.ma_fast,
            slow_period=args.ma_slow
        )
    elif strategy_name == 'macd':
        return MACDStrategy(
            fast_period=args.macd_fast,
            slow_period=args.macd_slow,
            signal_period=args.macd_signal
        )
    elif strategy_name == 'multi_timeframe':
        return MultiTimeframeStrategy()
    else:
        logger.error(f"Unbekannte Strategie: {strategy_name}")
        raise ValueError(f"Unbekannte Strategie: {strategy_name}")

def run_trading_cycle(exchange_api, data_handler, strategy, risk_manager, symbol, timeframe):
    """Führt einen einzelnen Trading-Zyklus aus."""
    try:
        logger.info("Starte Trading-Zyklus...")
        
        # Aktuelle Marktdaten abrufen
        market_data = data_handler.get_latest_data(symbol=symbol, timeframe=timeframe, limit=100)
        if market_data is None or market_data.empty:
            logger.error("Keine Marktdaten verfügbar")
            return
        
        # Generiere Signale basierend auf der Strategie
        signals_df = strategy.generate_signals(market_data)
        latest_signal = signals_df.iloc[-1]
        
        # Aktuelle offene Positionen abrufen
        positions = exchange_api.get_positions(symbol)
        
        # Bestimme aktuelle Position
        current_position = 'none'
        position_size = 0
        
        if positions:
            for pos in positions:
                if pos['symbol'] == symbol:
                    if pos['side'] == 'Buy' and pos['size'] > 0:
                        current_position = 'long'
                        position_size = pos['size']
                    elif pos['side'] == 'Sell' and pos['size'] > 0:
                        current_position = 'short'
                        position_size = pos['size']
        
        # Aktuelle Orders abrufen
        open_orders = exchange_api.get_open_orders(symbol)
        
        # Handelssignal auswerten
        signal = latest_signal['signal'] if 'signal' in latest_signal else 0
        
        if signal != 0:
            # Aktuelle Preise
            current_price = latest_signal['close']
            
            # Bestimme Handelsaktion
            action = None
            
            if signal > 0 and current_position != 'long':  # Long-Signal
                action = 'buy'
                side = 'Buy'
                logger.info(f"Long-Signal erkannt bei {current_price}")
                
                # Aktuelle Short-Position schließen, falls vorhanden
                if current_position == 'short':
                    logger.info(f"Schließe bestehende Short-Position: {position_size}")
                    exchange_api.close_position(symbol, 'short')
                
                # Stop-Loss und Take-Profit berechnen
                stop_loss = latest_signal['stop_loss'] if 'stop_loss' in latest_signal else None
                take_profit = latest_signal['take_profit'] if 'take_profit' in latest_signal else None
                
                if stop_loss is None or take_profit is None:
                    # Berechne SL und TP basierend auf ATR oder festen Prozentsätzen
                    atr = signals_df['atr'].iloc[-1] if 'atr' in signals_df.columns else (current_price * 0.02)
                    stop_loss = current_price - (atr * 1.5)
                    take_profit = current_price + (atr * 3.0)
                
                # Positionsgröße berechnen
                account_info = exchange_api.get_account_info()
                balance = account_info.get('balance', 10000)  # Fallback auf 10000, falls nicht verfügbar
                
                # Risikobetrag berechnen (% des Guthabens)
                risk_amount = balance * risk_manager.risk_percentage
                
                # Berechne Positionsgröße basierend auf Stop-Loss
                risk_per_unit = current_price - stop_loss
                size = risk_amount / risk_per_unit if risk_per_unit > 0 else 0
                
                # Positionsgröße begrenzen
                size = risk_manager.calculate_position_size(
                    price=current_price,
                    stop_loss=stop_loss,
                    balance=balance
                )
                
                if size > 0:
                    # Order platzieren
                    order_result = exchange_api.place_order(
                        symbol=symbol,
                        side=side,
                        order_type='Market',
                        qty=size,
                        price=current_price,
                        stop_loss=stop_loss,
                        take_profit=take_profit
                    )
                    
                    if order_result and 'id' in order_result:
                        logger.info(f"Long-Order platziert: {size} @ {current_price}, "
                                   f"SL: {stop_loss}, TP: {take_profit}")
                    else:
                        logger.error(f"Fehler beim Platzieren der Long-Order: {order_result}")
                else:
                    logger.warning(f"Berechnete Positionsgröße zu klein: {size}")
                
            elif signal < 0 and current_position != 'short':  # Short-Signal
                action = 'sell'
                side = 'Sell'
                logger.info(f"Short-Signal erkannt bei {current_price}")
                
                # Aktuelle Long-Position schließen, falls vorhanden
                if current_position == 'long':
                    logger.info(f"Schließe bestehende Long-Position: {position_size}")
                    exchange_api.close_position(symbol, 'long')
                
                # Stop-Loss und Take-Profit berechnen
                stop_loss = latest_signal['stop_loss'] if 'stop_loss' in latest_signal else None
                take_profit = latest_signal['take_profit'] if 'take_profit' in latest_signal else None
                
                if stop_loss is None or take_profit is None:
                    # Berechne SL und TP basierend auf ATR oder festen Prozentsätzen
                    atr = signals_df['atr'].iloc[-1] if 'atr' in signals_df.columns else (current_price * 0.02)
                    stop_loss = current_price + (atr * 1.5)
                    take_profit = current_price - (atr * 3.0)
                
                # Positionsgröße berechnen
                account_info = exchange_api.get_account_info()
                balance = account_info.get('balance', 10000)  # Fallback auf 10000, falls nicht verfügbar
                
                # Risikobetrag berechnen (% des Guthabens)
                risk_amount = balance * risk_manager.risk_percentage
                
                # Berechne Positionsgröße basierend auf Stop-Loss
                risk_per_unit = stop_loss - current_price
                size = risk_amount / risk_per_unit if risk_per_unit > 0 else 0
                
                # Positionsgröße begrenzen
                size = risk_manager.calculate_position_size(
                    price=current_price,
                    stop_loss=stop_loss,
                    balance=balance
                )
                
                if size > 0:
                    # Order platzieren
                    order_result = exchange_api.place_order(
                        symbol=symbol,
                        side=side,
                        order_type='Market',
                        qty=size,
                        price=current_price,
                        stop_loss=stop_loss,
                        take_profit=take_profit
                    )
                    
                    if order_result and 'id' in order_result:
                        logger.info(f"Short-Order platziert: {size} @ {current_price}, "
                                   f"SL: {stop_loss}, TP: {take_profit}")
                    else:
                        logger.error(f"Fehler beim Platzieren der Short-Order: {order_result}")
                else:
                    logger.warning(f"Berechnete Positionsgröße zu klein: {size}")
        
        else:
            logger.info("Kein Handelssignal erkannt")
            
        # Trading-Statistiken loggen
        account_info = exchange_api.get_account_info()
        balance = account_info.get('balance', 0)
        open_positions = exchange_api.get_positions(symbol)
        
        logger.info(f"Aktuelles Guthaben: ${balance:.2f}")
        logger.info(f"Offene Positionen: {len(open_positions)}")
        
        for pos in open_positions:
            entry_price = pos.get('entry_price', 0)
            current_price = pos.get('mark_price', 0)
            size = pos.get('size', 0)
            side = pos.get('side', '')
            unrealized_pnl = pos.get('unrealized_pnl', 0)
            
            logger.info(f"Position: {side} {size} @ {entry_price:.2f}, "
                       f"Aktueller Preis: {current_price:.2f}, "
                       f"Unrealisierter PnL: ${unrealized_pnl:.2f}")
        
    except Exception as e:
        logger.exception(f"Fehler im Trading-Zyklus: {e}")

def main():
    """Hauptfunktion für den Live-Trading-Betrieb."""
    # Signal-Handler für graceful shutdown registrieren
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Kommandozeilenargumente parsen
    args = parse_args()
    
    # API-Schlüssel aus Umgebungsvariablen laden
    api_key = os.environ.get('BYBIT_API_KEY')
    api_secret = os.environ.get('BYBIT_API_SECRET')
    
    if not api_key or not api_secret:
        logger.error("API-Schlüssel nicht in Umgebungsvariablen gefunden. "
                    "Setze BYBIT_API_KEY und BYBIT_API_SECRET.")
        return 1
    
    try:
        # Exchange-API initialisieren
        exchange_api = BybitAPI(
            api_key=api_key,
            api_secret=api_secret,
            testnet=args.testnet
        )
        
        # Initialisiere DataHandler
        data_handler = DataHandler(exchange_api)
        
        # Initialisiere Strategie
        strategy = get_strategy(args)
        logger.info(f"Strategie initialisiert: {args.strategy}")
        
        # Initialisiere RiskManager
        risk_manager = RiskManager(
            risk_percentage=args.risk_per_trade,
            max_open_trades=args.max_open_trades
        )
        logger.info(f"Risk Manager initialisiert: Risiko pro Trade: {args.risk_per_trade*100}%, "
                   f"Max. offene Trades: {args.max_open_trades}")
        
        # Überprüfe Verbindung zur Börse
        account_info = exchange_api.get_account_info()
        if not account_info:
            logger.error("Fehler beim Verbinden mit der Börse. Überprüfe API-Schlüssel und Internetverbindung.")
            return 1
            
        balance = account_info.get('balance', 0)
        logger.info(f"Erfolgreich verbunden mit Bybit {'Testnet' if args.testnet else 'Mainnet'}")
        logger.info(f"Aktuelles Guthaben: ${balance:.2f}")
        
        # Hauptschleife des Bots
        logger.info(f"Starte Trading-Bot für {args.symbol} mit {args.timeframe} Timeframe")
        logger.info(f"Intervall zwischen Zyklen: {args.interval} Sekunden")
        logger.info("Drücke Ctrl+C zum Beenden")
        
        cycle_count = 0
        
        # Trading-Hauptschleife
        while running:
            cycle_start_time = time.time()
            cycle_count += 1
            
            logger.info(f"=== Trading-Zyklus #{cycle_count} ===")
            
            # Führe Trading-Zyklus aus
            run_trading_cycle(
                exchange_api=exchange_api,
                data_handler=data_handler,
                strategy=strategy,
                risk_manager=risk_manager,
                symbol=args.symbol,
                timeframe=args.timeframe
            )
            
            # Berechne Zeit bis zum nächsten Zyklus
            elapsed_time = time.time() - cycle_start_time
            sleep_time = max(1, args.interval - elapsed_time)
            
            logger.info(f"Zyklus abgeschlossen in {elapsed_time:.2f} Sekunden")
            logger.info(f"Warte {sleep_time:.2f} Sekunden bis zum nächsten Zyklus")
            
            # Warte bis zum nächsten Zyklus
            for _ in range(int(sleep_time)):
                if not running:
                    break
                time.sleep(1)
            
            # Schlafe die restliche Zeit (weniger als 1 Sekunde)
            if running and sleep_time % 1 > 0:
                time.sleep(sleep_time % 1)
        
        logger.info("Trading-Bot wird beendet...")
        
        return 0
        
    except Exception as e:
        logger.exception(f"Unerwarteter Fehler: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
