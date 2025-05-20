"""
Bollinger Bands Strategie für den Crypto Trading Bot.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Union


class BollingerBandsStrategy:
    """
    Handelsstrategie basierend auf Bollinger Bands.
    Bollinger Bands bestehen aus einem mittleren Band (in der Regel ein SMA) und einem 
    oberen und unteren Band, die um eine bestimmte Anzahl von Standardabweichungen 
    vom mittleren Band entfernt sind.
    """
    
    def __init__(self, period: int = 20, std_dev: float = 2.0, 
                 use_atr_for_sl: bool = True, atr_period: int = 14,
                 sl_atr_multiplier: float = 1.5, tp_atr_multiplier: float = 3.0,
                 require_volume_confirmation: bool = True, 
                 volume_threshold: float = 1.5):
        """
        Initialisiert die Bollinger Bands Strategie.
        
        :param period: Periode für die Berechnung des gleitenden Durchschnitts
        :param std_dev: Anzahl der Standardabweichungen für die oberen/unteren Bänder
        :param use_atr_for_sl: Verwende ATR für Stop-Loss-Berechnung
        :param atr_period: Periode für ATR-Berechnung
        :param sl_atr_multiplier: Multiplikator für ATR bei Stop-Loss
        :param tp_atr_multiplier: Multiplikator für ATR bei Take-Profit
        :param require_volume_confirmation: Erfordere Volumenbestätigung für Signale
        :param volume_threshold: Schwellenwert für Volumen (Multiplikator des durchschnittlichen Volumens)
        """
        self.period = period
        self.std_dev = std_dev
        self.use_atr_for_sl = use_atr_for_sl
        self.atr_period = atr_period
        self.sl_atr_multiplier = sl_atr_multiplier
        self.tp_atr_multiplier = tp_atr_multiplier
        self.require_volume_confirmation = require_volume_confirmation
        self.volume_threshold = volume_threshold
        
        self.name = f"BollingerBands_{period}_{std_dev}"
    
    def calculate_indicators(self, ohlcv_data: pd.DataFrame) -> pd.DataFrame:
        """
        Berechnet die Bollinger Bands und andere benötigte Indikatoren.
        
        :param ohlcv_data: DataFrame mit OHLCV-Daten
        :return: DataFrame mit hinzugefügten Indikatoren
        """
        df = ohlcv_data.copy()
        
        # Extrahiere die Schlusskurse, falls erforderlich
        if 'close' in df.columns:
            close = df['close']
        elif 'Close' in df.columns:
            close = df['Close']
        else:
            raise ValueError("DataFrame muss eine 'close' oder 'Close'-Spalte enthalten")
        
        # Extrahiere das Volumen, falls erforderlich
        if 'volume' in df.columns:
            volume = df['volume']
        elif 'Volume' in df.columns:
            volume = df['Volume']
        else:
            if self.require_volume_confirmation:
                raise ValueError("DataFrame muss eine 'volume' oder 'Volume'-Spalte enthalten")
            volume = pd.Series(0, index=df.index)
        
        # Berechne den SMA für das mittlere Band
        df['bb_middle'] = close.rolling(window=self.period).mean()
        
        # Berechne die Standardabweichung
        df['bb_std'] = close.rolling(window=self.period).std()
        
        # Berechne die oberen und unteren Bänder
        df['bb_upper'] = df['bb_middle'] + (df['bb_std'] * self.std_dev)
        df['bb_lower'] = df['bb_middle'] - (df['bb_std'] * self.std_dev)
        
        # Berechne den %B-Indikator (wo sich der Preis innerhalb der Bänder befindet)
        df['bb_percent_b'] = (close - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
        
        # Berechne die Bandbreite-Indikator (Volatilitätsmaß)
        df['bb_bandwidth'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
        
        # Berechne Volumen-Durchschnitt für Bestätigung
        df['volume_sma'] = volume.rolling(window=self.period).mean()
        df['volume_ratio'] = volume / df['volume_sma']
        
        # Berechne ATR für Stop-Loss und Take-Profit, falls aktiviert
        if self.use_atr_for_sl:
            # Extrahiere Hoch-, Tief- und Schlusskurse
            if 'high' in df.columns and 'low' in df.columns:
                high = df['high']
                low = df['low']
            elif 'High' in df.columns and 'Low' in df.columns:
                high = df['High']
                low = df['Low']
            else:
                raise ValueError("DataFrame muss 'high'/'High' und 'low'/'Low'-Spalten enthalten")
            
            # Berechne True Range
            tr1 = high - low
            tr2 = abs(high - close.shift(1))
            tr3 = abs(low - close.shift(1))
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            
            # Berechne ATR
            df['atr'] = tr.rolling(window=self.atr_period).mean()
        
        return df
    
    def generate_signals(self, ohlcv_data: pd.DataFrame) -> pd.DataFrame:
        """
        Generiert Handelssignale basierend auf der Bollinger-Band-Strategie.
        
        :param ohlcv_data: DataFrame mit OHLCV-Daten
        :return: DataFrame mit hinzugefügten Signalen
        """
        # Berechne zunächst alle Indikatoren
        df = self.calculate_indicators(ohlcv_data)
        
        # Initialisiere Signal-Spalten
        df['signal'] = 0  # 1 für Long, -1 für Short, 0 für kein Signal
        df['entry_price'] = np.nan
        df['stop_loss'] = np.nan
        df['take_profit'] = np.nan
        
        # Extrahiere relevante Daten
        close = df['close'] if 'close' in df.columns else df['Close']
        high = df['high'] if 'high' in df.columns else df['High']
        low = df['low'] if 'low' in df.columns else df['Low']
        
        # Generiere Kauf-Signale (Preis kreuzt unteres Band von unten nach oben)
        long_condition = (
            (close.shift(1) <= df['bb_lower'].shift(1)) &  # Voriger Schlusskurs unter dem unteren Band
            (close > df['bb_lower']) &                      # Aktueller Schlusskurs über dem unteren Band
            (df['bb_bandwidth'] > df['bb_bandwidth'].rolling(window=self.period).mean())  # Erhöhte Volatilität
        )
        
        # Füge Volumenbestätigung hinzu, falls erforderlich
        if self.require_volume_confirmation:
            long_condition = long_condition & (df['volume_ratio'] >= self.volume_threshold)
        
        # Generiere Verkaufs-Signale (Preis kreuzt oberes Band von unten nach oben)
        short_condition = (
            (close.shift(1) >= df['bb_upper'].shift(1)) &  # Voriger Schlusskurs über dem oberen Band
            (close < df['bb_upper']) &                      # Aktueller Schlusskurs unter dem oberen Band
            (df['bb_bandwidth'] > df['bb_bandwidth'].rolling(window=self.period).mean())  # Erhöhte Volatilität
        )
        
        # Füge Volumenbestätigung hinzu, falls erforderlich
        if self.require_volume_confirmation:
            short_condition = short_condition & (df['volume_ratio'] >= self.volume_threshold)
        
        # Setze Signal-Werte
        df.loc[long_condition, 'signal'] = 1
        df.loc[short_condition, 'signal'] = -1
        
        # Setze entry_price als den aktuellen Schlusskurs
        df.loc[df['signal'] != 0, 'entry_price'] = close
        
        # Berechne Stop-Loss und Take-Profit
        if self.use_atr_for_sl:
            # Verwende ATR für Stop-Loss und Take-Profit
            for i in df.index[df['signal'] != 0]:
                atr_value = df.loc[i, 'atr']
                if df.loc[i, 'signal'] == 1:  # Long
                    df.loc[i, 'stop_loss'] = df.loc[i, 'entry_price'] - (atr_value * self.sl_atr_multiplier)
                    df.loc[i, 'take_profit'] = df.loc[i, 'entry_price'] + (atr_value * self.tp_atr_multiplier)
                else:  # Short
                    df.loc[i, 'stop_loss'] = df.loc[i, 'entry_price'] + (atr_value * self.sl_atr_multiplier)
                    df.loc[i, 'take_profit'] = df.loc[i, 'entry_price'] - (atr_value * self.tp_atr_multiplier)
        else:
            # Verwende feste Prozentsätze basierend auf der Bandbreite
            for i in df.index[df['signal'] != 0]:
                band_width = df.loc[i, 'bb_bandwidth'] * df.loc[i, 'entry_price']
                if df.loc[i, 'signal'] == 1:  # Long
                    df.loc[i, 'stop_loss'] = df.loc[i, 'entry_price'] - (band_width * 0.5)
                    df.loc[i, 'take_profit'] = df.loc[i, 'entry_price'] + (band_width * 1.0)
                else:  # Short
                    df.loc[i, 'stop_loss'] = df.loc[i, 'entry_price'] + (band_width * 0.5)
                    df.loc[i, 'take_profit'] = df.loc[i, 'entry_price'] - (band_width * 1.0)
        
        return df
    
    def backtest(self, ohlcv_data: pd.DataFrame, initial_capital: float = 10000.0,
                commission: float = 0.001) -> Dict:
        """
        Führt einen Backtest der Strategie durch.
        
        :param ohlcv_data: DataFrame mit OHLCV-Daten
        :param initial_capital: Anfangskapital
        :param commission: Kommission pro Trade (als Dezimalzahl, z.B. 0.001 für 0,1%)
        :return: Dictionary mit Backtest-Ergebnissen
        """
        # Generiere Signale
        signals_df = self.generate_signals(ohlcv_data)
        
        # Extrahiere Close für die Berechnung von P&L
        close = signals_df['close'] if 'close' in signals_df.columns else signals_df['Close']
        
        # Initialisiere Tracking-Variablen
        capital = initial_capital
        position = 0
        entry_price = 0
        stop_loss = 0
        take_profit = 0
        trades = []
        equity_curve = [capital]
        
        # Durchlaufe die Daten und simuliere das Trading
        for i in range(1, len(signals_df)):
            current_date = signals_df.index[i]
            current_price = close.iloc[i]
            previous_price = close.iloc[i-1]
            
            # Überprüfe, ob eine Position offen ist
            if position != 0:
                # Berechne unrealisierten P&L
                if position > 0:  # Long
                    # Prüfe, ob Stop-Loss oder Take-Profit aktiviert wurde
                    if previous_price >= stop_loss and current_price < stop_loss:
                        # Stop-Loss wurde aktiviert
                        pnl = position * (stop_loss - entry_price)
                        commission_cost = position * entry_price * commission + position * stop_loss * commission
                        capital += pnl - commission_cost
                        
                        trades.append({
                            'entry_date': entry_date,
                            'exit_date': current_date,
                            'direction': 'long',
                            'entry_price': entry_price,
                            'exit_price': stop_loss,
                            'position_size': position,
                            'pnl': pnl,
                            'commission': commission_cost,
                            'exit_type': 'stop_loss'
                        })
                        
                        position = 0
                    elif previous_price <= take_profit and current_price > take_profit:
                        # Take-Profit wurde aktiviert
                        pnl = position * (take_profit - entry_price)
                        commission_cost = position * entry_price * commission + position * take_profit * commission
                        capital += pnl - commission_cost
                        
                        trades.append({
                            'entry_date': entry_date,
                            'exit_date': current_date,
                            'direction': 'long',
                            'entry_price': entry_price,
                            'exit_price': take_profit,
                            'position_size': position,
                            'pnl': pnl,
                            'commission': commission_cost,
                            'exit_type': 'take_profit'
                        })
                        
                        position = 0
                
                elif position < 0:  # Short
                    # Prüfe, ob Stop-Loss oder Take-Profit aktiviert wurde
                    if previous_price <= stop_loss and current_price > stop_loss:
                        # Stop-Loss wurde aktiviert
                        pnl = position * (entry_price - stop_loss)
                        commission_cost = abs(position) * entry_price * commission + abs(position) * stop_loss * commission
                        capital += pnl - commission_cost
                        
                        trades.append({
                            'entry_date': entry_date,
                            'exit_date': current_date,
                            'direction': 'short',
                            'entry_price': entry_price,
                            'exit_price': stop_loss,
                            'position_size': abs(position),
                            'pnl': pnl,
                            'commission': commission_cost,
                            'exit_type': 'stop_loss'
                        })
                        
                        position = 0
                    elif previous_price >= take_profit and current_price < take_profit:
                        # Take-Profit wurde aktiviert
                        pnl = position * (entry_price - take_profit)
                        commission_cost = abs(position) * entry_price * commission + abs(position) * take_profit * commission
                        capital += pnl - commission_cost
                        
                        trades.append({
                            'entry_date': entry_date,
                            'exit_date': current_date,
                            'direction': 'short',
                            'entry_price': entry_price,
                            'exit_price': take_profit,
                            'position_size': abs(position),
                            'pnl': pnl,
                            'commission': commission_cost,
                            'exit_type': 'take_profit'
                        })
                        
                        position = 0
            
            # Überprüfe auf neue Signale, wenn keine Position offen ist
            if position == 0 and signals_df['signal'].iloc[i] != 0:
                signal = signals_df['signal'].iloc[i]
                entry_price = signals_df['entry_price'].iloc[i]
                stop_loss = signals_df['stop_loss'].iloc[i]
                take_profit = signals_df['take_profit'].iloc[i]
                
                # Berechne die Positionsgröße basierend auf Risikomanagement
                # Einfaches Modell: Fester Prozentsatz des Kapitals
                position_size = capital * 0.1 / abs(entry_price - stop_loss)
                
                if signal > 0:  # Long
                    position = position_size
                else:  # Short
                    position = -position_size
                
                entry_date = current_date
            
            # Aktualisiere die Equity-Kurve
            equity_curve.append(capital + (position * (current_price - entry_price) if position != 0 else 0))
        
        # Verkaufe offene Position zum letzten Preis
        if position != 0:
            current_price = close.iloc[-1]
            if position > 0:  # Long
                pnl = position * (current_price - entry_price)
            else:  # Short
                pnl = position * (entry_price - current_price)
            
            commission_cost = abs(position) * entry_price * commission + abs(position) * current_price * commission
            capital += pnl - commission_cost
            
            trades.append({
                'entry_date': entry_date,
                'exit_date': signals_df.index[-1],
                'direction': 'long' if position > 0 else 'short',
                'entry_price': entry_price,
                'exit_price': current_price,
                'position_size': abs(position),
                'pnl': pnl,
                'commission': commission_cost,
                'exit_type': 'end_of_period'
            })
        
        # Berechne Performance-Metriken
        equity_curve_series = pd.Series(equity_curve, index=signals_df.index)
        returns = equity_curve_series.pct_change().dropna()
        
        winning_trades = [t for t in trades if t['pnl'] > 0]
        losing_trades = [t for t in trades if t['pnl'] <= 0]
        
        total_trades = len(trades)
        win_rate = len(winning_trades) / total_trades if total_trades > 0 else 0
        average_win = np.mean([t['pnl'] for t in winning_trades]) if winning_trades else 0
        average_loss = np.mean([t['pnl'] for t in losing_trades]) if losing_trades else 0
        profit_factor = abs(sum(t['pnl'] for t in winning_trades) / sum(t['pnl'] for t in losing_trades)) if losing_trades and sum(t['pnl'] for t in losing_trades) != 0 else float('inf')
        
        # Berechne Drawdown
        peak = equity_curve_series.expanding().max()
        drawdown = equity_curve_series / peak - 1.0
        max_drawdown = drawdown.min()
        
        # Sammle Ergebnisse
        results = {
            'initial_capital': initial_capital,
            'final_capital': equity_curve[-1],
            'total_return': (equity_curve[-1] / initial_capital - 1) * 100,
            'annualized_return': ((equity_curve[-1] / initial_capital) ** (252 / len(signals_df)) - 1) * 100,
            'max_drawdown': max_drawdown * 100,
            'total_trades': total_trades,
            'win_rate': win_rate * 100,
            'average_win': average_win,
            'average_loss': average_loss,
            'profit_factor': profit_factor,
            'sharpe_ratio': returns.mean() / returns.std() * np.sqrt(252) if returns.std() != 0 else 0,
            'equity_curve': equity_curve_series,
            'trades': trades
        }
        
        return results
    
    def optimize(self, ohlcv_data: pd.DataFrame, period_range: List[int] = [10, 20, 30, 40, 50],
               std_dev_range: List[float] = [1.5, 2.0, 2.5, 3.0],
               atr_multiplier_range: List[float] = [1.0, 1.5, 2.0, 2.5, 3.0]) -> Dict:
        """
        Optimiert die Strategie-Parameter durch Grid-Search.
        
        :param ohlcv_data: DataFrame mit OHLCV-Daten
        :param period_range: Liste von Perioden zum Testen
        :param std_dev_range: Liste von Standardabweichungen zum Testen
        :param atr_multiplier_range: Liste von ATR-Multiplikatoren zum Testen
        :return: Dictionary mit optimierten Parametern und Ergebnissen
        """
        best_return = -float('inf')
        best_params = {}
        best_results = {}
        all_results = []
        
        # Grid-Search über alle Parameter-Kombinationen
        for period in period_range:
            for std_dev in std_dev_range:
                for sl_multiplier in atr_multiplier_range:
                    for tp_multiplier in [m * 2 for m in atr_multiplier_range]:  # TP typischerweise 2x SL
                        # Aktualisiere Parameter
                        self.period = period
                        self.std_dev = std_dev
                        self.sl_atr_multiplier = sl_multiplier
                        self.tp_atr_multiplier = tp_multiplier
                        
                        # Führe Backtest durch
                        results = self.backtest(ohlcv_data)
                        
                        # Speichere Ergebnisse
                        param_results = {
                            'period': period,
                            'std_dev': std_dev,
                            'sl_atr_multiplier': sl_multiplier,
                            'tp_atr_multiplier': tp_multiplier,
                            'total_return': results['total_return'],
                            'win_rate': results['win_rate'],
                            'profit_factor': results['profit_factor'],
                            'max_drawdown': results['max_drawdown'],
                            'sharpe_ratio': results['sharpe_ratio']
                        }
                        all_results.append(param_results)
                        
                        # Aktualisiere beste Parameter, falls bessere Rendite erzielt wurde
                        if results['total_return'] > best_return:
                            best_return = results['total_return']
                            best_params = {
                                'period': period,
                                'std_dev': std_dev,
                                'sl_atr_multiplier': sl_multiplier,
                                'tp_atr_multiplier': tp_multiplier
                            }
                            best_results = results
        
        # Setze auf beste Parameter zurück
        self.period = best_params['period']
        self.std_dev = best_params['std_dev']
        self.sl_atr_multiplier = best_params['sl_atr_multiplier']
        self.tp_atr_multiplier = best_params['tp_atr_multiplier']
        
        return {
            'best_params': best_params,
            'best_results': best_results,
            'all_results': all_results
        }
