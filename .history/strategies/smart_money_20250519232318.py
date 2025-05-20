"""
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
        # This check might be redundant if calculate_indicators is always called before generate_signal
        # but keeping it for safety based on the original code structure.
        if 'volume_change' not in data.columns:
             data = self.calculate_indicators(data)

        # Check if data is None after calculating indicators
        if data is None:
            logging.warning("calculate_indicators returned None.")
            return signal, entry_price, stop_loss, metadata

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
            # Ensure columns exist before accessing them
            buy_key_level_condition = latest_candle.get('near_support', False) # and latest_candle.get('distance_to_support', np.inf) < 1.0 # Beispiel-Schwelle
            sell_key_level_condition = latest_candle.get('near_resistance', False) # and latest_candle.get('distance_to_resistance', np.inf) < 1.0 # Beispiel-Schwelle
            buy_conditions_met.append(buy_key_level_condition)
            sell_conditions_met.append(sell_key_level_condition)
            buy_filters_passed['key_levels'] = buy_key_level_condition
            sell_filters_passed['key_levels'] = sell_key_level_condition

        # 3. Pattern Recognition Filter
        if self.use_pattern_recognition:
            # Ensure columns exist before accessing them
            buy_pattern_condition = latest_candle.get('bullish_pattern', False)
            sell_pattern_condition = latest_candle.get('bearish_pattern', False)
            buy_conditions_met.append(buy_pattern_condition)
            sell_conditions_met.append(sell_pattern_condition)
            buy_filters_passed['pattern'] = buy_pattern_condition
            sell_filters_passed['pattern'] = sell_pattern_condition

        # 4. Order Flow Filter
        if self.use_order_flow:
            # Ensure columns exist before accessing them
            buy_order_flow_condition = latest_candle.get('bullish_order_flow', False) or latest_candle.get('smart_money_absorption', False)
            sell_order_flow_condition = latest_candle.get('bearish_order_flow', False)
            buy_conditions_met.append(buy_order_flow_condition)
            sell_conditions_met.append(sell_order_flow_condition)
            buy_filters_passed['order_flow'] = buy_order_flow_condition
            sell_filters_passed['order_flow'] = sell_order_flow_condition

        # 5. Liquiditäts-Sweep-Filter
        if self.use_liquidity_sweep:
            # Ensure columns exist before accessing them
            buy_sweep_condition = latest_candle.get('support_sweep', False) and latest_candle.get('liquidity_hunted', False)
            sell_sweep_condition = latest_candle.get('resistance_sweep', False) and latest_candle.get('liquidity_hunted', False)
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
                if not np.isnan(latest_candle.get('support_level', np.nan)):
                    stop_loss = latest_candle['support_level'] * (1 - self.config.get('STOP_LOSS_BUFFER', 0.001)) # Beispiel: 0.1% unter Support
                elif 'atr' in latest_candle:
                     stop_loss = latest_candle['close'] - (latest_candle['atr'] * self.config.get('STOP_LOSS_ATR_MULTIPLIER', 1.5)) # Beispiel: 1.5 * ATR unter Close
                else:
                     stop_loss = latest_candle['close'] * (1 + self.config.get('DEFAULT_STOP_LOSS_PERCENT', 0.01)) # Beispiel: 1% unter Close
                logging.info(f"BUY Signal generiert. Entry: {entry_price}, SL: {stop_loss}")

            elif all_sell_filters_passed:
                signal = 'SELL'
                entry_price = latest_candle['close']
                # Berechne Stop-Loss für Short-Position (z.B. über dem letzten Resistance oder basierend auf ATR)
                if not np.isnan(latest_candle.get('resistance_level', np.nan)):
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
        if df is None: return None

        # 2. Schlüssellevel hinzufügen, wenn aktiviert
        if self.use_key_levels:
            df = self._add_key_levels(df)
            if df is None: return None
        
        # 3. Musterkennung hinzufügen, wenn aktiviert
        if self.use_pattern_recognition:
            df = self._add_pattern_recognition(df)
            if df is None: return None

        # 4. Order Flow Analyse hinzufügen, wenn aktiviert
        if self.use_order_flow:
            df = self._add_order_flow_analysis(df)
            if df is None: return None

        # 5. Liquiditäts-Sweep-Detektion hinzufügen, wenn aktiviert
        if self.use_liquidity_sweep:
            df = self._add_liquidity_sweep_detection(df)
            if df is None: return None

        # Handel-Sessions bestimmen und Multiplikatoren anwenden
        df = self._determine_session(df)
        if df is None: return None

        return df

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

        # 3. Doji (very small body)
        small_body_threshold = 0.1  # Body is less than 10% of the total range
        df['doji'] = df['body_to_range'] < small_body_threshold

        # 4. Shooting Star (small body at top, long upper shadow, small lower shadow)
        df['shooting_star'] = (
            (df['body_to_range'] < 0.3) &  # Kleiner Body
            (df['upper_shadow'] > df['body'] * 2) &  # Langer oberer Schatten
            (df['lower_shadow'] < df['body'])  # Kleiner unterer Schatten
        )

        # 5. Hammer (small body at bottom, long lower shadow, small upper shadow)
        df['hammer'] = (
            (df['body_to_range'] < 0.3) &  # Kleiner Body
            (df['lower_shadow'] > df['body'] * 2) &  # Langer unterer Schatten
            (df['upper_shadow'] < df['body'])  # Kleiner oberer Schatten
        )
        return df

    def _add_order_flow_analysis(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Analysiert den Order Flow, um Market Maker Aktivitäten zu identifizieren.

        Args:
            df: Ein Pandas DataFrame mit Marktdaten.

        Returns:
            DataFrame mit Order-Flow-Indikatoren.
        """
        if len(df) < 20:
            logging.warning("Nicht genügend Daten für Order-Flow-Analyse.")
            # Füge Dummy-Werte für die Ergebnis-Spalten hinzu
            df['buying_pressure'] = 0.0
            df['selling_pressure'] = 0.0
            df['absorption_ratio'] = 0.0
            df['delta_volume'] = 0.0
            df['market_facilitation_index'] = 0.0
            df['high_volume_node'] = False
            df['bullish_order_flow'] = False
            df['bearish_order_flow'] = False
            df['smart_money_absorption'] = False
            return df

        # Initialisierung der Order-Flow-Spalten
        df['buying_pressure'] = 0.0
        df['selling_pressure'] = 0.0
        df['absorption_ratio'] = 0.0
        df['delta_volume'] = 0.0
        df['market_facilitation_index'] = 0.0
        df['high_volume_node'] = False

        # Body-Größe für spätere Berechnungen
        if 'body' not in df.columns:
            df['body'] = abs(df['close'] - df['open'])

        # Delta-Volumen basierend auf Preisbewegung und Volumen berechnen
        # Positive Delta = Buying Pressure, Negative Delta = Selling Pressure
        df['delta_volume'] = np.where(
            df['close'] > df['open'],
            df['volume'],  # Buying Volume
            np.where(
                df['close'] < df['open'],
                -df['volume'],  # Selling Volume
                0  # Neutral Volume
            )
        )

        # Kumulativer Delta-Volumen (um Trends im Order Flow zu identifizieren)
        df['cumulative_delta'] = df['delta_volume'].cumsum()

        # Buying und Selling Pressure basierend auf Volumen und Preisbewegung
        df['buying_pressure'] = np.where(
            df['close'] > df['open'],
            df['volume'] * (df['close'] - df['open']) / (df['high'] - df['low']).clip(lower=0.0001),
            0
        )

        df['selling_pressure'] = np.where(
            df['close'] < df['open'],
            df['volume'] * (df['open'] - df['close']) / (df['high'] - df['low']).clip(lower=0.0001),
            0
        )

        # Absorption-Ratio: Wie gut absorbiert der Markt Volumen ohne signifikante Preisbewegung?
        df['absorption_ratio'] = df['volume'] / (df['high'] - df['low']).clip(lower=0.0001)

        # Market Facilitation Index (BW MFI): wie effizient der Markt Volumen in Preisbewegung umsetzt
        df['market_facilitation_index'] = (df['high'] - df['low']) / df['volume'].clip(lower=1)

        # Volumen-Cluster (High Volume Nodes) identifizieren
        volume_percentile = df['volume'].rolling(window=20).apply(
            lambda x: pd.Series(x).rank(pct=True).iloc[-1]
        )
        df['high_volume_node'] = volume_percentile > 0.8  # Obere 20% des Volumens

        # Order Flow Signale
        df['bullish_order_flow'] = (
            (df['buying_pressure'].rolling(3).mean() > df['selling_pressure'].rolling(20).mean() * 1.5) &
            (df['delta_volume'] > 0) &
            (df['cumulative_delta'].diff() > 0)
        )

        df['bearish_order_flow'] = (
            (df['selling_pressure'].rolling(3).mean() > df['buying_pressure'].rolling(20).mean() * 1.5) &
            (df['delta_volume'] < 0) &
            (df['cumulative_delta'].diff() < 0)
        )

        # Smart Money Absorption (hohe Absorption-Ratio bei niedriger Preisbewegung)
        df['smart_money_absorption'] = (
            (df['absorption_ratio'] > df['absorption_ratio'].rolling(20).mean() * 1.5) &
            (df['body'] < df['body'].rolling(20).mean() * 0.5)
        )

        logging.debug("Order-Flow-Analyse abgeschlossen.")
        return df

    def _add_liquidity_sweep_detection(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Erkennt Liquiditäts-Sweep-Ereignisse, bei denen Preise durch Schlüsselniveaus fegen.

        Args:
            df: Ein Pandas DataFrame mit Marktdaten und Key-Levels.

        Returns:
            DataFrame mit Liquiditäts-Sweep-Indikatoren.
        """
        if len(df) < 3 or 'support_level' not in df.columns or 'resistance_level' not in df.columns:
            logging.warning("Nicht genügend Daten oder fehlende Key-Levels für Liquiditäts-Sweep-Detektion.")
            # Füge Dummy-Werte hinzu, wenn die Spalten fehlen
            if 'support_level' not in df.columns:
                df['support_level'] = np.nan
            if 'resistance_level' not in df.columns:
                df['resistance_level'] = np.nan

            # Füge auch die Ergebnis-Spalten hinzu
            df['support_sweep'] = False
            df['resistance_sweep'] = False
            df['sweep_volume'] = 0.0
            df['liquidity_hunted'] = False

            return df

        # Initialisierung der Liquiditäts-Sweep-Spalten
        df['support_sweep'] = False
        df['resistance_sweep'] = False
        df['sweep_volume'] = 0.0
        df['liquidity_hunted'] = False

        # Support-Sweep: Preis fällt unter Support und erholt sich dann
        for i in range(2, len(df)):
            # Support-Sweep: Wenn der Low unter den Support geht aber der Close darüber schließt
            if not np.isnan(df['support_level'].iloc[i-1]) and (df['low'].iloc[i] < df['support_level'].iloc[i-1]) and (df['close'].iloc[i] > df['support_level'].iloc[i-1]):
                df.loc[df.index[i], 'support_sweep'] = True
                # Berechne Sweep-Volumen basierend auf dem Volumen und der Preisbewegung unter dem Support
                price_penetration = (df['support_level'].iloc[i-1] - df['low'].iloc[i]) / df['support_level'].iloc[i-1]
                df.loc[df.index[i], 'sweep_volume'] = df['volume'].iloc[i] * price_penetration

            # Resistance-Sweep: Wenn der High über die Resistance geht aber der Close darunter schließt
            if not np.isnan(df['resistance_level'].iloc[i-1]) and (df['high'].iloc[i] > df['resistance_level'].iloc[i-1]) and (df['close'].iloc[i] < df['resistance_level'].iloc[i-1]):
                df.loc[df.index[i], 'resistance_sweep'] = True
                # Berechne Sweep-Volumen basierend auf dem Volumen und der Preisbewegung über der Resistance
                price_penetration = (df['high'].iloc[i] - df['resistance_level'].iloc[i-1]) / df['resistance_level'].iloc[i-1]
                df.loc[df.index[i], 'sweep_volume'] = df['volume'].iloc[i] * price_penetration

        # Identifiziere "Liquidity Hunted" Ereignisse (signifikante Sweeps)
        volume_threshold = df['volume'].rolling(20).mean() * 1.2  # 20% über dem Durchschnittsvolumen
        df['liquidity_hunted'] = (
            ((df['support_sweep'] | df['resistance_sweep']) & (df['volume'] > volume_threshold))
        )

        # Schätze Liquiditätszonen basierend auf erkannten Sweeps
        sweep_zones = []
        for i in range(len(df)):
            if df['support_sweep'].iloc[i] or df['resistance_sweep'].iloc[i]:
                if df['support_sweep'].iloc[i]:
                    zone_price = df['support_level'].iloc[i]
                    zone_type = 'support'
                else:
                    zone_price = df['resistance_level'].iloc[i]
                    zone_type = 'resistance'

                sweep_zones.append({
                    'index': i,
                    'price': zone_price,
                    'type': zone_type,
                    'strength': df['sweep_volume'].iloc[i],
                    'liquidity_hunted'] = df['liquidity_hunted'].iloc[i]
                })

        # Speichere die letzten erkannten Liquiditätszonen
        self.last_liquidity_zones = sweep_zones[-5:] if sweep_zones else []

        logging.debug("Liquiditäts-Sweep-Detektion abgeschlossen.")
        return df

    def _add_key_levels(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Identifiziert und markiert Schlüssellevel wie Support/Resistance.

        Args:
            df: Ein Pandas DataFrame mit Marktdaten.

        Returns:
            DataFrame mit Key-Level-Indikatoren.
        """
        if len(df) < self.sr_lookback * 2:
            logging.warning("Nicht genügend Daten für Key-Level-Analyse.")
            # Füge Dummy-Werte für die Ergebnis-Spalten hinzu
            df['is_support'] = False
            df['is_resistance'] = False
            df['support_level'] = np.nan
            df['resistance_level'] = np.nan
            df['level_strength'] = 0
            df['distance_to_support'] = np.nan
            df['distance_to_resistance'] = np.nan
            df['near_support'] = False
            df['near_resistance'] = False
            return df

        # Initialisierung der Key-Level-Spalten
        df['is_support'] = False
        df['is_resistance'] = False
        df['support_level'] = np.nan
        df['resistance_level'] = np.nan
        df['level_strength'] = 0

        # Lokale Extrema finden (Tiefs und Hochs)
        for i in range(self.sr_lookback, len(df) - self.sr_lookback):
            # Support: Tiefs mit höheren Preisen auf beiden Seiten
            if all(df['low'].iloc[i] <= df['low'].iloc[i-j] for j in range(1, self.sr_lookback+1)) and \
               all(df['low'].iloc[i] <= df['low'].iloc[i+j] for j in range(1, self.sr_lookback+1)):
                df.loc[df.index[i], 'is_support'] = True
                df.loc[df.index[i], 'support_level'] = df['low'].iloc[i]

                # Stärke basierend auf Dauer und Preisabweichung berechnen
                price_deviation = min(
                    abs(df['low'].iloc[i-self.sr_lookback:i].min() - df['low'].iloc[i]),
                    abs(df['low'].iloc[i+1:i+self.sr_lookback+1].min() - df['low'].iloc[i])
                )
                df.loc[df.index[i], 'level_strength'] = price_deviation / df['low'].iloc[i] * 100

            # Resistance: Hochs mit niedrigeren Preisen auf beiden Seiten
            if all(df['high'].iloc[i] >= df['high'].iloc[i-j] for j in range(1, self.sr_lookback+1)) and \
               all(df['high'].iloc[i] >= df['high'].iloc[i+j] for j in range(1, self.sr_lookback+1)):
                df.loc[df.index[i], 'is_resistance'] = True
                df.loc[df.index[i], 'resistance_level'] = df['high'].iloc[i]

                # Stärke basierend auf Dauer und Preisabweichung berechnen
                price_deviation = min(
                    abs(df['high'].iloc[i] - df['high'].iloc[i-self.sr_lookback:i].max()),
                    abs(df['high'].iloc[i] - df['high'].iloc[i+1:i+self.sr_lookback+1].max())
                )
                df.loc[df.index[i], 'level_strength'] = price_deviation / df['high'].iloc[i] * 100

        # Horizontale Levels erstellen, indem die letzten bekannten Werte nach vorne gefüllt werden
        df['support_level'] = df['support_level'].fillna(method='ffill')
        df['resistance_level'] = df['resistance_level'].fillna(method='ffill')

        # Preis-zu-Level-Distanz berechnen
        df['distance_to_support'] = (df['close'] - df['support_level']) / df['close'] * 100
        df['distance_to_resistance'] = (df['resistance_level'] - df['close']) / df['close'] * 100

        # Identifizieren, ob der Preis in der Nähe eines Key-Levels ist
        support_threshold = 0.5  # 0.5% Distanz zum Support wird als "nahe" betrachtet
        resistance_threshold = 0.5 # 0.5% Distanz zur Resistance wird als "nahe" betrachtet

        df['near_support'] = (df['distance_to_support'] >= 0) & (df['distance_to_support'] <= support_threshold)
        df['near_resistance'] = (df['distance_to_resistance'] >= 0) & (df['distance_to_resistance'] <= resistance_threshold)

        logging.debug("Key-Level-Analyse abgeschlossen.")
        return df

    def _determine_session(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Bestimmt die Handels-Session (Asian, London, New York) für jeden Datenpunkt.

        Args:
            df: Ein Pandas DataFrame mit einem DatetimeIndex.

        Returns:
            Eine Pandas Series mit der Handels-Session für jeden Datenpunkt.
        """
        if not isinstance(df.index, pd.DatetimeIndex):
            logging.warning("DataFrame hat keinen DatetimeIndex für Session-Bestimmung.")
            # Füge Dummy-Spalten hinzu, wenn der Index nicht passt
            df['session'] = 'unknown'
            df['session_multiplier'] = np.nan
            return df

        # Definiere die Handelszeiten für die Sessions in UTC
        # Beispielzeiten (können je nach Börse und DST variieren)
        asian_start = 0 # 00:00 UTC
        asian_end = 9 # 09:00 UTC
        london_start = 8 # 08:00 UTC
        london_end = 17 # 17:00 UTC
        new_york_start = 13 # 13:00 UTC
        new_york_end = 22 # 22:00 UTC

        # Konvertiere Index zu UTC für konsistente Vergleiche
        utc_index = df.index.tz_convert('UTC') if df.index.tz is not None else df.index

        # Bestimme die Session für jeden Zeitstempel und füge als Spalte hinzu
        df['session'] = 'unknown'
        df.loc[(utc_index.hour >= asian_start) & (utc_index.hour < asian_end), 'session'] = 'asian'
        df.loc[(utc_index.hour >= london_start) & (utc_index.hour < london_end), 'session'] = 'london'
        df.loc[(utc_index.hour >= new_york_start) & (utc_index.hour < new_york_end), 'session'] = 'new_york'

        # Wende Session-Multiplikatoren an
        df['session_multiplier'] = df['session'].map(self.session_multipliers)

        logging.debug("Handels-Session-Bestimmung abgeschlossen.")
        return df

# Beispiel für die Verwendung (kann für Tests verwendet werden)
if __name__ == "__main__":
    # Beispiel-Konfiguration
    test_config = {
        'LIQUIDITY_FACTOR': 1.0,
        'MIN_LIQUIDITY_THRESHOLD': 1000,
        'SESSION_MULTIPLIER': {'asian': 0.8, 'london': 1.2, 'new_york': 1.5},
        'RSI_PERIOD': 14,
        'RSI_OVERBOUGHT': 70,
        'RSI_OVERSOLD': 30,
        'MACD_FAST': 9,
        'MACD_SLOW': 21,
        'MACD_SIGNAL': 9,
        'ATR_PERIOD': 14,
        'VOLATILITY_THRESHOLD': 0.03,
        'SR_LOOKBACK': 14,
        'RISK_REWARD_RATIO': 1.5,
        'POSITION_SIZE': 0.01,
        'RISK_PERCENTAGE': 2.0,
        'USE_VOLUME_FILTER': True,
        'VOLUME_THRESHOLD': 10000,
        'USE_KEY_LEVELS': True,
        'USE_PATTERN_RECOGNITION': True,
        'USE_ORDER_FLOW': True,
        'USE_LIQUIDITY_SWEEP': True,
        'STOP_LOSS_BUFFER': 0.001,
        'STOP_LOSS_ATR_MULTIPLIER': 1.5,
        'DEFAULT_STOP_LOSS_PERCENT': 0.01,
    }

    # Beispiel-Daten erstellen (simuliert)
    data = pd.DataFrame({
        'timestamp': pd.to_datetime(pd.date_range(start='2023-01-01', periods=100, freq='5min')),
        'open': np.random.rand(100) * 1000 + 40000,
        'high': np.random.rand(100) * 1000 + 40500,
        'low': np.random.rand(100) * 1000 + 39500,
        'close': np.random.rand(100) * 1000 + 40000,
        'volume': np.random.rand(100) * 50000 + 5000
    })
    data = data.set_index('timestamp')

    # Strategie-Instanz erstellen
    strategy = SmartMoneyStrategy(test_config)

    # Indikatoren berechnen
    data_with_indicators = strategy.calculate_indicators(data)

    # Signal generieren
    signal, entry_price, stop_loss, metadata = strategy.generate_signal(data_with_indicators)

    print(f"Generiertes Signal: {signal}")
    print(f"Eintrittspreis: {entry_price}")
    print(f"Stop-Loss: {stop_loss}")
    print(f"Metadaten: {metadata}")

    # Beispiel mit Position Management
    signal_long, entry_price_long, stop_loss_long, metadata_long = strategy.generate_signal(data_with_indicators, current_position='LONG')
    print(f"\nSignal mit LONG Position: {signal_long}")
    print(f"Eintrittspreis: {entry_price_long}")
    print(f"Stop-Loss: {stop_loss_long}")
    print(f"Metadaten: {metadata_long}")

    signal_short, entry_price_short, stop_loss_short, metadata_short = strategy.generate_signal(data_with_indicators, current_position='SHORT')
    print(f"\nSignal mit SHORT Position: {signal_short}")
    print(f"Eintrittspreis: {entry_price_short}")
    print(f"Stop-Loss: {stop_loss_short}")
    print(f"Metadaten: {metadata_short}")