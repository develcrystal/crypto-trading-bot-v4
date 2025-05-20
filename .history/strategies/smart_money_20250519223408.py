def _calculate_base_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
    """
    Berechnet Basisindikatoren für die Strategie.

    Args:
        df: Ein Pandas DataFrame mit Marktdaten.

    Returns:
        DataFrame mit Basisindikatoren.
    """
    # Überprüfen, ob genügend Daten für die Berechnung vorhanden sind
    if len(df) < max(self.rsi_period, self.macd_slow, self.atr_period):
        logging.warning(f"Nicht genügend Daten für Indikatorberechnung: {len(df)} Datenpunkte vorhanden.")
        # Füge Dummy-Werte für die Ergebnis-Spalten hinzu
        df['rsi'] = np.nan
        df['ema_fast'] = np.nan
        df['ema_slow'] = np.nan
        df['macd'] = np.nan
        df['macd_signal'] = np.nan
        df['macd_histogram'] = np.nan
        df['atr'] = np.nan
        df['volume_sma'] = np.nan
        df['above_avg_volume'] = False
        return df

    # RSI (Relative Strength Index) berechnen
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.ewm(com=self.rsi_period - 1, adjust=False).mean()
    avg_loss = loss.ewm(com=self.rsi_period - 1, adjust=False).mean()

    rs = avg_gain / avg_loss.replace(0, np.finfo(float).eps)  # Vermeide Division durch Null
    df['rsi'] = 100 - (100 / (1 + rs))

    # MACD berechnen
    df['ema_fast'] = df['close'].ewm(span=self.macd_fast, adjust=False).mean()
    df['ema_slow'] = df['close'].ewm(span=self.macd_slow, adjust=False).mean()
    df['macd'] = df['ema_fast'] - df['ema_slow']
    df['macd_signal'] = df['macd'].ewm(span=self.macd_signal, adjust=False).mean()
    df['macd_histogram'] = df['macd'] - df['macd_signal']

    # Speichere vorherige Werte für Trend-Bestimmung
    df['macd_histogram_1'] = df['macd_histogram'].shift(1)

    # ATR (Average True Range) für Volatilität berechnen
    high_low = df['high'] - df['low']
    high_close = np.abs(df['high'] - df['close'].shift())
    low_close = np.abs(df['low'] - df['close'].shift())
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df['atr'] = tr.ewm(span=self.atr_period, adjust=False).mean()

    # Volume Profile (einfach)
    df['volume_sma'] = df['volume'].rolling(window=20).mean()
    df['above_avg_volume'] = df['volume'] > df['volume_sma']

    return df
        return df

    def _add_pattern_recognition(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Erkennt wichtige Chartmuster wie Engulfing, Dojis, etc.
        
        Args:
            df: Ein Pandas DataFrame mit Marktdaten.
            
        Returns:
            DataFrame mit erkannten Mustern.
        """
        if len(df) < 3:
            logging.warning("Nicht genügend Daten für Pattern-Erkennung.")
            # Füge Dummy-Werte für die Ergebnis-Spalten hinzu
            df['bullish_engulfing'] = False
            df['bearish_engulfing'] = False
            df['doji'] = False
            df['shooting_star'] = False
            df['hammer'] = False
            df['evening_star'] = False
            df['morning_star'] = False
            df['bullish_pattern'] = False
            df['bearish_pattern'] = False
            return df
        
        # Initialisierung der Muster-Spalten
        df['bullish_engulfing'] = False
        df['bearish_engulfing'] = False
        df['doji'] = False
        df['shooting_star'] = False
        df['hammer'] = False
        df['evening_star'] = False
        df['morning_star'] = False
        
        # Body und Schatten berechnen
        df['body'] = abs(df['close'] - df['open'])
        df['upper_shadow'] = df['high'] - df[['open', 'close']].max(axis=1)
        df['lower_shadow'] = df[['open', 'close']].min(axis=1) - df['low']
        df['body_to_range'] = df['body'] / (df['high'] - df['low']).clip(lower=0.0001)
        
        # 1. Bullish Engulfing Pattern
        df['bullish_engulfing'] = (
            (df['open'].shift(1) > df['close'].shift(1)) &  # Vorheriger Candle ist bearish
            (df['close'] > df['open']) &  # Aktueller Candle ist bullish
            (df['open'] <= df['close'].shift(1)) &  # Öffnung unter dem Vorgänger-Schluss
            (df['close'] > df['open'].shift(1))  # Schluss über dem Vorgänger-Öffnung
        )
        
        # 2. Bearish Engulfing Pattern
        df['bearish_engulfing'] = (
            (df['close'].shift(1) > df['open'].shift(1)) &  # Vorheriger Candle ist bullish
            (df['open'] > df['close']) &  # Aktueller Candle ist bearish
            (df['open'] >= df['close'].shift(1)) &  # Öffnung über dem Vorgänger-Schluss
            (df['close'] < df['open'].shift(1))  # Schluss unter dem Vorgänger-Öffnung
        )
        
        # 3. Doji (sehr kleiner Body)
        small_body_threshold = 0.1  # Body ist weniger als 10% des Gesamtbereichs
        df['doji'] = df['body_to_range'] < small_body_threshold
        
        # 4. Shooting Star (kleiner Body oben, langer oberer Schatten, kleiner unterer Schatten)
        df['shooting_star'] = (
            (df['body_to_range'] < 0.3) &  # Kleiner Body
            (df['upper_shadow'] > df['body'] * 2) &  # Langer oberer Schatten
            (df['lower_shadow'] < df['body'])  # Kleiner unterer Schatten
        )
        
        # 5. Hammer (kleiner Body unten, langer unterer Schatten, kleiner oberer Schatten)
        df['hammer'] = (
            (df['body_to_range'] < 0.3) &  # Kleiner Body
            (df['lower_shadow'] > df['body'] * 2) &  # Langer unterer Schatten
            (df['upper_shadow'] < df['body'])  # Kleiner oberer Schatten
        )"""
Smart Money Strategie für den Crypto Trading Bot V2.

Diese Strategie basiert auf den Konzepten des "Smart Money" Trading und
erkennt Handelsmöglichkeiten basierend auf Liquiditätspools, Market Structure,
Order Flow und Musteranalyse.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Tuple, Optional, Union

# Konfiguriere das Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SmartMoneyStrategy:
    """
    Eine fortschrittliche Smart Money Strategie für den Kryptohandel.
    
    Diese Strategie basiert auf Smart Money Konzepten wie:
    - Liquiditätszonen-Erkennung
    - Order Flow Analyse
    - Schlüssellevel-Identifikation
    - Musterkennung
    - Liquiditäts-Sweep-Detektion
    
    Die Strategie kombiniert diese Komponenten, um hochwertige Handelssignale
    zu generieren, die die Aktivitäten institutioneller Händler (Smart Money) nachahmen.
    """
    
    def __init__(self, config: Dict):
        """
        Initialisiert die SmartMoneyStrategy mit Konfigurationsparametern.
        
        Args:
            config: Ein Dictionary mit Konfigurationsparametern.
        """
        self.config = config
        self.name = "SmartMoneyStrategy"
        
        # Lade Parameter aus der Konfiguration mit Standardwerten
        self.liquidity_factor = config.get('LIQUIDITY_FACTOR', 1.0)
        self.min_liquidity_threshold = config.get('MIN_LIQUIDITY_THRESHOLD', 1000)
        self.session_multipliers = config.get('SESSION_MULTIPLIER', {
            'asian': 0.8, 
            'london': 1.2, 
            'new_york': 1.5
        })
        
        # Technische Indikator-Parameter
        self.rsi_period = config.get('RSI_PERIOD', 14)
        self.rsi_overbought = config.get('RSI_OVERBOUGHT', 70)
        self.rsi_oversold = config.get('RSI_OVERSOLD', 30)
        self.macd_fast = config.get('MACD_FAST', 9)
        self.macd_slow = config.get('MACD_SLOW', 21)
        self.macd_signal = config.get('MACD_SIGNAL', 9)
        self.atr_period = config.get('ATR_PERIOD', 14)
        self.volatility_threshold = config.get('VOLATILITY_THRESHOLD', 0.03)
        self.sr_lookback = config.get('SR_LOOKBACK', 14)
        
        # Risikomanagement-Parameter
        self.risk_reward_ratio = config.get('RISK_REWARD_RATIO', 1.5)
        self.position_size = config.get('POSITION_SIZE', 0.01)
        self.max_risk_per_trade = config.get('RISK_PERCENTAGE', 2.0) / 100  # Konvertiere zu Dezimal
        
        # Filter-Aktivierungsstatus
        self.use_volume_filter = config.get('USE_VOLUME_FILTER', True)
        self.use_key_levels = config.get('USE_KEY_LEVELS', True)
        self.use_pattern_recognition = config.get('USE_PATTERN_RECOGNITION', True)
        self.use_order_flow = config.get('USE_ORDER_FLOW', True)
        self.use_liquidity_sweep = config.get('USE_LIQUIDITY_SWEEP', True)
        
        # Volumen-Schwellen
        self.volume_threshold = config.get('VOLUME_THRESHOLD', 100000)
        
        # Für Backtest-Optimierung
        self.current_trade = None
        self.metrics = {
            'win_rate': 0,
            'profit_factor': 0,
            'avg_win': 0,
            'avg_loss': 0,
            'max_drawdown': 0,
            'sharpe_ratio': 0,
        }
        
        logging.info("SmartMoneyStrategy initialisiert mit Parametern: %s", {
            'liquidity_factor': self.liquidity_factor,
            'min_liquidity_threshold': self.min_liquidity_threshold,
            'volume_threshold': self.volume_threshold,
            'filter_status': {
                'volume': self.use_volume_filter,
                'key_levels': self.use_key_levels,
                'pattern': self.use_pattern_recognition,
                'order_flow': self.use_order_flow,
                'liquidity_sweep': self.use_liquidity_sweep
            }
        })
def generate_signal(self, data: pd.DataFrame, current_position: str = None) -> Tuple[str, float, float, Dict]:
    """
    Generiert Handelssignale basierend auf den berechneten Indikatoren und aktivierten Filtern.

    Args:
        data: Ein Pandas DataFrame mit Marktdaten und berechneten Indikatoren.
        current_position: Aktuelle Position ("LONG", "SHORT" oder None).

    Returns:
        Ein Tuple mit (signal, entry_price, stop_loss, metadata):
            - signal: "BUY", "SELL", "HOLD", "CLOSE_LONG", oder "CLOSE_SHORT"
            - entry_price: Vorgeschlagener Eintrittspreis
            - stop_loss: Vorgeschlagener Stop-Loss-Preis
            - metadata: Zusätzliche Informationen zum Signal
    """
    signal = 'HOLD'
    entry_price = np.nan
    stop_loss = np.nan
    metadata = {}

    if data.empty:
        logging.warning("Leerer DataFrame in generate_signal erhalten.")
        return signal, entry_price, stop_loss, metadata

    # Stelle sicher, dass die Indikatoren berechnet wurden
    if 'volume_change' not in data.columns:
         data = self.calculate_indicators(data)

    latest_candle = data.iloc[-1]

    # Wende Filter basierend auf der Konfiguration an
    buy_conditions_met = []
    sell_conditions_met = []
    buy_filters_passed = {}
    sell_filters_passed = {}

    # 1. Volumen-Filter
    if self.use_volume_filter:
        volume_condition = latest_candle['volume'] > self.volume_threshold
        buy_conditions_met.append(volume_condition)
        sell_conditions_met.append(volume_condition)
        buy_filters_passed['volume'] = volume_condition
        sell_filters_passed['volume'] = volume_condition

    # 2. Key Levels Filter
    if self.use_key_levels:
        # Beispiel: Kaufe nahe Support, Verkaufe nahe Resistance
        buy_key_level_condition = latest_candle['near_support'] # and latest_candle['distance_to_support'] < 1.0 # Beispiel-Schwelle
        sell_key_level_condition = latest_candle['near_resistance'] # and latest_candle['distance_to_resistance'] < 1.0 # Beispiel-Schwelle
        buy_conditions_met.append(buy_key_level_condition)
        sell_conditions_met.append(sell_key_level_condition)
        buy_filters_passed['key_levels'] = buy_key_level_condition
        sell_filters_passed['key_levels'] = sell_key_level_condition

    # 3. Pattern Recognition Filter
    if self.use_pattern_recognition:
        buy_pattern_condition = latest_candle['bullish_pattern']
        sell_pattern_condition = latest_candle['bearish_pattern']
        buy_conditions_met.append(buy_pattern_condition)
        sell_conditions_met.append(sell_pattern_condition)
        buy_filters_passed['pattern'] = buy_pattern_condition
        sell_filters_passed['pattern'] = sell_pattern_condition

    # 4. Order Flow Filter
    if self.use_order_flow:
        buy_order_flow_condition = latest_candle['bullish_order_flow'] or latest_candle['smart_money_absorption']
        sell_order_flow_condition = latest_candle['bearish_order_flow']
        buy_conditions_met.append(buy_order_flow_condition)
        sell_conditions_met.append(sell_order_flow_condition)
        buy_filters_passed['order_flow'] = buy_order_flow_condition
        sell_filters_passed['order_flow'] = sell_order_flow_condition

    # 5. Liquiditäts-Sweep-Filter
    if self.use_liquidity_sweep:
        buy_sweep_condition = latest_candle['support_sweep'] and latest_candle['liquidity_hunted']
        sell_sweep_condition = latest_candle['resistance_sweep'] and latest_candle['liquidity_hunted']
        buy_conditions_met.append(buy_sweep_condition)
        sell_conditions_met.append(sell_sweep_condition)
        buy_filters_passed['liquidity_sweep'] = buy_sweep_condition
        sell_filters_passed['liquidity_sweep'] = sell_sweep_condition

    # Überprüfe, ob alle aktivierten Filter für KAUFEN bestanden sind
    all_buy_filters_passed = all(buy_conditions_met) if buy_conditions_met else False

    # Überprüfe, ob alle aktivierten Filter für VERKAUFEN bestanden sind
    all_sell_filters_passed = all(sell_conditions_met) if sell_conditions_met else False

    metadata['buy_filters_passed'] = buy_filters_passed
    metadata['sell_filters_passed'] = sell_filters_passed

    # Generiere Signal basierend auf Filtern und aktueller Position
    if current_position is None:
        if all_buy_filters_passed:
            signal = 'BUY'
            entry_price = latest_candle['close']
            # Berechne Stop-Loss für Long-Position (z.B. unter dem letzten Support oder basierend auf ATR)
            if not np.isnan(latest_candle['support_level']):
                stop_loss = latest_candle['support_level'] * (1 - self.config.get('STOP_LOSS_BUFFER', 0.001)) # Beispiel: 0.1% unter Support
            elif 'atr' in latest_candle:
                 stop_loss = latest_candle['close'] - (latest_candle['atr'] * self.config.get('STOP_LOSS_ATR_MULTIPLIER', 1.5)) # Beispiel: 1.5 * ATR unter Close
            else:
                 stop_loss = latest_candle['close'] * (1 - self.config.get('DEFAULT_STOP_LOSS_PERCENT', 0.01)) # Beispiel: 1% unter Close
            logging.info(f"BUY Signal generiert. Entry: {entry_price}, SL: {stop_loss}")

        elif all_sell_filters_passed:
            signal = 'SELL'
            entry_price = latest_candle['close']
            # Berechne Stop-Loss für Short-Position (z.B. über dem letzten Resistance oder basierend auf ATR)
            if not np.isnan(latest_candle['resistance_level']):
                stop_loss = latest_candle['resistance_level'] * (1 + self.config.get('STOP_LOSS_BUFFER', 0.001)) # Beispiel: 0.1% über Resistance
            elif 'atr' in latest_candle:
                 stop_loss = latest_candle['close'] + (latest_candle['atr'] * self.config.get('STOP_LOSS_ATR_MULTIPLIER', 1.5)) # Beispiel: 1.5 * ATR über Close
            else:
                 stop_loss = latest_candle['close'] * (1 + self.config.get('DEFAULT_STOP_LOSS_PERCENT', 0.01)) # Beispiel: 1% über Close
            logging.info(f"SELL Signal generiert. Entry: {entry_price}, SL: {stop_loss}")

    elif current_position == 'LONG' and all_sell_filters_passed:
        signal = 'CLOSE_LONG'
        entry_price = latest_candle['close'] # Ausstiegspreis
        logging.info(f"CLOSE_LONG Signal generiert. Exit: {entry_price}")

    elif current_position == 'SHORT' and all_buy_filters_passed:
        signal = 'CLOSE_SHORT'
        entry_price = latest_candle['close'] # Ausstiegspreis
        logging.info(f"CLOSE_SHORT Signal generiert. Exit: {entry_price}")

    return signal, entry_price, stop_loss, metadata

def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
    """
    Berechnet alle für die Smart Money Strategie notwendigen Indikatoren.

    Args:
        data: Ein Pandas DataFrame mit Marktdaten (OHLCV).

    Returns:
        Ein erweitertes DataFrame mit allen berechneten Indikatoren.
    """
    if data.empty:
        logging.warning("Leerer DataFrame in calculate_indicators erhalten.")
        return data

    # Kopie des DataFrames erstellen, um das Original nicht zu verändern
    df = data.copy()

    # Grundlegende Berechnungen für Preisbewegung
    df['price_change'] = df['close'].pct_change()
    df['volatility'] = df['high'] - df['low']
    df['volume_change'] = df['volume'].pct_change()

    # 1. Basisindikatoren berechnen
    df = self._calculate_base_indicators(df)

    # 2. Schlüssellevel hinzufügen, wenn aktiviert
    if self.use_key_levels:
        df = self._add_key_levels(df)

    # 3. Musterkennung hinzufügen, wenn aktiviert
    if self.use_pattern_recognition:
        df = self._add_pattern_recognition(df)

    # 4. Order Flow Analyse hinzufügen, wenn aktiviert
    if self.use_order_flow:
        df = self._add_order_flow_analysis(df)

    # 5. Liquiditäts-Sweep-Detektion hinzufügen, wenn aktiviert
    if self.use_liquidity_sweep:
        df = self._add_liquidity_sweep_detection(df)

    # Handel-Sessions bestimmen und Multiplikatoren anwenden
    df['session'] = self._determine_session(df)
    df['session_multiplier'] = df['session'].map(self.session_multipliers)

    return df