"""
Strategiemodule für den Crypto Trading Bot V2.

Dieses Modul enthält Implementierungen verschiedener Handelsstrategien,
beginnend mit der einfachen Moving-Average-Crossover-Strategie.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional, Union, Any
from abc import ABC, abstractmethod

# Konfiguriere Logging
logger = logging.getLogger(__name__)

class Strategy(ABC):
    """
    Abstrakte Basisklasse für Handelsstrategien.
    
    Diese Klasse definiert die Grundstruktur, die alle Strategieklassen
    implementieren müssen.
    """
    
    def __init__(self, name: str = "BaseStrategy"):
        """
        Initialisiere die Strategie.
        
        Args:
            name: Name der Strategie
        """
        self.name = name
        logger.info(f"Strategie initialisiert: {name}")
        
    @abstractmethod
    def generate_signal(self, data: pd.DataFrame) -> Dict:
        """
        Generiert ein Handelssignal basierend auf Marktdaten.
        
        Args:
            data: DataFrame mit OHLCV-Daten und Indikatoren
            
        Returns:
            Dictionary mit Handelssignal
        """
        pass
        
    def calculate_stop_loss(self, data: pd.DataFrame, signal: Dict) -> float:
        """
        Berechnet den Stop-Loss-Preis für ein Handelssignal.
        
        Args:
            data: DataFrame mit OHLCV-Daten
            signal: Handelssignal-Dictionary
            
        Returns:
            Stop-Loss-Preis
        """
        # Standardimplementierung - kann von Unterklassen überschrieben werden
        if signal['action'] == 'buy':
            # Für Kauf-Signale: X% unter dem Einstiegspreis
            return signal['price'] * 0.97  # 3% Stop-Loss
        elif signal['action'] == 'sell':
            # Für Verkauf-Signale: X% über dem Einstiegspreis
            return signal['price'] * 1.03  # 3% Stop-Loss
        return 0.0
        
    def calculate_take_profit(self, data: pd.DataFrame, signal: Dict, risk_reward_ratio: float = 2.0) -> float:
        """
        Berechnet den Take-Profit-Preis für ein Handelssignal.
        
        Args:
            data: DataFrame mit OHLCV-Daten
            signal: Handelssignal-Dictionary
            risk_reward_ratio: Verhältnis von Gewinn zu Risiko
            
        Returns:
            Take-Profit-Preis
        """
        # Standardimplementierung - kann von Unterklassen überschrieben werden
        if not signal.get('stop_loss'):
            signal['stop_loss'] = self.calculate_stop_loss(data, signal)
            
        price = signal['price']
        stop_loss = signal['stop_loss']
        
        if signal['action'] == 'buy':
            # Für Kauf-Signale: Einstiegspreis + (Einstiegspreis - Stop-Loss) * RRR
            risk = price - stop_loss
            return price + (risk * risk_reward_ratio)
        elif signal['action'] == 'sell':
            # Für Verkauf-Signale: Einstiegspreis - (Stop-Loss - Einstiegspreis) * RRR
            risk = stop_loss - price
            return price - (risk * risk_reward_ratio)
        return 0.0

class MovingAverageCrossover(Strategy):
    """
    Moving-Average-Crossover-Strategie.
    
    Diese Strategie generiert Kauf-Signale, wenn ein kurzfristiger Moving Average
    einen langfristigen Moving Average von unten kreuzt, und Verkauf-Signale,
    wenn der kurzfristige MA den langfristigen MA von oben kreuzt.
    """
    
    def __init__(self, fast_period: int = 9, slow_period: int = 21, 
                risk_reward_ratio: float = 2.0):
        """
        Initialisiere die Moving-Average-Crossover-Strategie.
        
        Args:
            fast_period: Periode für den schnellen Moving Average
            slow_period: Periode für den langsamen Moving Average
            risk_reward_ratio: Verhältnis von Gewinn zu Risiko
        """
        super().__init__(name=f"MA_Crossover_{fast_period}_{slow_period}")
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.risk_reward_ratio = risk_reward_ratio
        logger.info(f"MA-Crossover-Strategie initialisiert: Fast={fast_period}, Slow={slow_period}")
        
    def prepare_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Bereitet Daten für die Strategieevaluation vor.
        
        Berechnet Moving Averages und fügt sie zum DataFrame hinzu.
        
        Args:
            data: Eingabe-DataFrame mit OHLCV-Daten
            
        Returns:
            DataFrame mit zusätzlichen Indikatoren
        """
        df = data.copy()
        
        # Prüfen, ob genügend Daten vorhanden sind
        if len(df) < self.slow_period:
            logger.warning(f"Nicht genügend Daten für MA-Berechnung: {len(df)} < {self.slow_period}")
            return df
        
        # Moving Averages berechnen
        df[f'ma_fast'] = df['close'].rolling(window=self.fast_period).mean()
        df[f'ma_slow'] = df['close'].rolling(window=self.slow_period).mean()
        
        # Crossover-Signal berechnen
        df['ma_crossover'] = 0
        
        # Prüfen, ob der fast MA den slow MA kreuzt
        df.loc[(df['ma_fast'] > df['ma_slow']) & 
              (df['ma_fast'].shift(1) <= df['ma_slow'].shift(1)), 'ma_crossover'] = 1  # Bullish
        
        df.loc[(df['ma_fast'] < df['ma_slow']) & 
              (df['ma_fast'].shift(1) >= df['ma_slow'].shift(1)), 'ma_crossover'] = -1  # Bearish
        
        return df
        
    def generate_signal(self, data: pd.DataFrame) -> Dict:
        """
        Generiert ein Handelssignal basierend auf dem MA-Crossover.
        
        Args:
            data: DataFrame mit OHLCV-Daten
            
        Returns:
            Dictionary mit Handelssignal
        """
        # Standard-Signal (Hold)
        signal = {
            'action': 'hold',
            'price': 0.0,
            'stop_loss': 0.0,
            'take_profit': 0.0,
            'timestamp': None,
            'details': {}
        }
        
        # Prüfen, ob genügend Daten vorhanden sind
        if len(data) < self.slow_period + 1:
            logger.info(f"Nicht genügend Daten für MA-Crossover: {len(data)} < {self.slow_period + 1}")
            return signal
        
        # Daten für die Strategie vorbereiten
        df = self.prepare_data(data)
        
        # Letzte Zeile auswählen
        current = df.iloc[-1]
        
        # Aktuelle Preise
        current_price = current['close']
        signal['price'] = current_price
        signal['timestamp'] = df.index[-1]
        
        # Details zur Signalgenerierung
        signal['details'] = {
            'ma_fast': current['ma_fast'],
            'ma_slow': current['ma_slow'],
            'crossover': current['ma_crossover']
        }
        
        # Bullish Crossover - Kauf-Signal
        if current['ma_crossover'] == 1:
            signal['action'] = 'buy'
            signal['stop_loss'] = self.calculate_stop_loss(df, signal)
            signal['take_profit'] = self.calculate_take_profit(df, signal, self.risk_reward_ratio)
            logger.info(f"BUY Signal generiert: Preis={current_price:.2f}, "
                      f"Stop-Loss={signal['stop_loss']:.2f}, "
                      f"Take-Profit={signal['take_profit']:.2f}")
            
        # Bearish Crossover - Verkauf-Signal
        elif current['ma_crossover'] == -1:
            signal['action'] = 'sell'
            signal['stop_loss'] = self.calculate_stop_loss(df, signal)
            signal['take_profit'] = self.calculate_take_profit(df, signal, self.risk_reward_ratio)
            logger.info(f"SELL Signal generiert: Preis={current_price:.2f}, "
                      f"Stop-Loss={signal['stop_loss']:.2f}, "
                      f"Take-Profit={signal['take_profit']:.2f}")
            
        return signal
    
    def calculate_stop_loss(self, data: pd.DataFrame, signal: Dict) -> float:
        """
        Berechnet den Stop-Loss-Preis basierend auf der Volatilität.
        
        Verwendet die ATR (Average True Range) für dynamische Stop-Loss-Berechnung.
        
        Args:
            data: DataFrame mit OHLCV-Daten
            signal: Handelssignal-Dictionary
            
        Returns:
            Stop-Loss-Preis
        """
        df = data.copy()
        
        # ATR berechnen, falls nicht vorhanden
        if 'atr' not in df.columns:
            high_low = df['high'] - df['low']
            high_close = np.abs(df['high'] - df['close'].shift())
            low_close = np.abs(df['low'] - df['close'].shift())
            
            tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            df['atr'] = tr.rolling(window=14).mean()
        
        # Letzte ATR
        last_atr = df['atr'].iloc[-1] if not pd.isna(df['atr'].iloc[-1]) else df['close'].iloc[-1] * 0.02
        
        if signal['action'] == 'buy':
            # Für Kauf-Signale: Preis - (ATR * Multiplikator)
            return signal['price'] - (last_atr * 1.5)
        elif signal['action'] == 'sell':
            # Für Verkauf-Signale: Preis + (ATR * Multiplikator)
            return signal['price'] + (last_atr * 1.5)
        
        return 0.0
        
class RSIOverboughtOversold(Strategy):
    """
    RSI-Überkauft/Überverkauft-Strategie.
    
    Diese Strategie generiert Kauf-Signale, wenn der RSI unter einen überverkauften
    Schwellenwert fällt und dann wieder darüber steigt, und Verkauf-Signale, wenn der 
    RSI über einen überkauften Schwellenwert steigt und dann wieder darunter fällt.
    """
    
    def __init__(self, period: int = 14, oversold: int = 30, overbought: int = 70,
                risk_reward_ratio: float = 2.0):
        """
        Initialisiere die RSI-Strategie.
        
        Args:
            period: Periode für die RSI-Berechnung
            oversold: RSI-Schwelle für überverkaufte Bedingungen
            overbought: RSI-Schwelle für überkaufte Bedingungen
            risk_reward_ratio: Verhältnis von Gewinn zu Risiko
        """
        super().__init__(name=f"RSI_{period}_{oversold}_{overbought}")
        self.period = period
        self.oversold = oversold
        self.overbought = overbought
        self.risk_reward_ratio = risk_reward_ratio
        logger.info(f"RSI-Strategie initialisiert: Period={period}, Oversold={oversold}, Overbought={overbought}")
        
    def prepare_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Bereitet Daten für die Strategieevaluation vor.
        
        Berechnet den RSI und fügt ihn zum DataFrame hinzu.
        
        Args:
            data: Eingabe-DataFrame mit OHLCV-Daten
            
        Returns:
            DataFrame mit zusätzlichen Indikatoren
        """
        df = data.copy()
        
        # Prüfen, ob genügend Daten vorhanden sind
        if len(df) < self.period + 1:
            logger.warning(f"Nicht genügend Daten für RSI-Berechnung: {len(df)} < {self.period + 1}")
            return df
        
        # RSI berechnen
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.period).mean()
        
        # RSI-Formel: 100 - (100 / (1 + RS))
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # Überkauft/Überverkauft-Bedingungen
        df['oversold'] = (df['rsi'] < self.oversold).astype(int)
        df['overbought'] = (df['rsi'] > self.overbought).astype(int)
        
        # Signale berechnen - wir wollen Signale, wenn der RSI aus dem überkauften/überverkauften Bereich kommt
        df['oversold_exit'] = ((df['rsi'] > self.oversold) & (df['rsi'].shift(1) <= self.oversold)).astype(int)
        df['overbought_exit'] = ((df['rsi'] < self.overbought) & (df['rsi'].shift(1) >= self.overbought)).astype(int)
        
        return df
        
    def generate_signal(self, data: pd.DataFrame) -> Dict:
        """
        Generiert ein Handelssignal basierend auf RSI-Bedingungen.
        
        Args:
            data: DataFrame mit OHLCV-Daten
            
        Returns:
            Dictionary mit Handelssignal
        """
        # Standard-Signal (Hold)
        signal = {
            'action': 'hold',
            'price': 0.0,
            'stop_loss': 0.0,
            'take_profit': 0.0,
            'timestamp': None,
            'details': {}
        }
        
        # Prüfen, ob genügend Daten vorhanden sind
        if len(data) < self.period + 1:
            logger.info(f"Nicht genügend Daten für RSI-Strategie: {len(data)} < {self.period + 1}")
            return signal
        
        # Daten für die Strategie vorbereiten
        df = self.prepare_data(data)
        
        # Letzte Zeile auswählen
        current = df.iloc[-1]
        
        # Aktuelle Preise
        current_price = current['close']
        signal['price'] = current_price
        signal['timestamp'] = df.index[-1]
        
        # Details zur Signalgenerierung
        signal['details'] = {
            'rsi': current['rsi'],
            'oversold': self.oversold,
            'overbought': self.overbought
        }
        
        # Kauf-Signal: RSI steigt aus überverkauftem Bereich
        if current['oversold_exit'] == 1:
            signal['action'] = 'buy'
            signal['stop_loss'] = self.calculate_stop_loss(df, signal)
            signal['take_profit'] = self.calculate_take_profit(df, signal, self.risk_reward_ratio)
            logger.info(f"BUY Signal generiert (RSI Exit Oversold): Preis={current_price:.2f}, "
                      f"RSI={current['rsi']:.2f}, "
                      f"Stop-Loss={signal['stop_loss']:.2f}, "
                      f"Take-Profit={signal['take_profit']:.2f}")
            
        # Verkauf-Signal: RSI fällt aus überkauftem Bereich
        elif current['overbought_exit'] == 1:
            signal['action'] = 'sell'
            signal['stop_loss'] = self.calculate_stop_loss(df, signal)
            signal['take_profit'] = self.calculate_take_profit(df, signal, self.risk_reward_ratio)
            logger.info(f"SELL Signal generiert (RSI Exit Overbought): Preis={current_price:.2f}, "
                      f"RSI={current['rsi']:.2f}, "
                      f"Stop-Loss={signal['stop_loss']:.2f}, "
                      f"Take-Profit={signal['take_profit']:.2f}")
            
        return signal
    
    def calculate_stop_loss(self, data: pd.DataFrame, signal: Dict) -> float:
        """
        Berechnet den Stop-Loss-Preis basierend auf der jüngsten Preisstruktur.
        
        Für Kauf-Signale: Minimum der letzten N Kerzen
        Für Verkauf-Signale: Maximum der letzten N Kerzen
        
        Args:
            data: DataFrame mit OHLCV-Daten
            signal: Handelssignal-Dictionary
            
        Returns:
            Stop-Loss-Preis
        """
        # Anzahl der Kerzen für Swing-High/Low
        n_periods = 5
        
        if signal['action'] == 'buy':
            # Für Kauf-Signale: Letztes Low - Buffer
            recent_low = data['low'].iloc[-n_periods:].min()
            buffer = (signal['price'] - recent_low) * 0.1  # 10% Buffer
            return recent_low - buffer
        elif signal['action'] == 'sell':
            # Für Verkauf-Signale: Letztes High + Buffer
            recent_high = data['high'].iloc[-n_periods:].max()
            buffer = (recent_high - signal['price']) * 0.1  # 10% Buffer
            return recent_high + buffer
        
        return 0.0
