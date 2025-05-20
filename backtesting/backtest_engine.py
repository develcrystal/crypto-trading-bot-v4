"""
Backtesting-Modul für den Crypto Trading Bot V2.

Dieses Modul stellt eine robuste Backtesting-Engine bereit, um Handelsstrategien
auf historischen Daten zu testen und zu bewerten.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import logging
import time
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any, Tuple

# Konfiguriere Logging
logger = logging.getLogger(__name__)

class BacktestEngine:
    """
    Engine für das Backtesting von Handelsstrategien.
    
    Diese Klasse ermöglicht die Simulation von Handelsstrategien auf historischen
    Marktdaten und bietet umfangreiche Analysen der Performance.
    """
    
    def __init__(self, data_handler, strategy, initial_balance: float = 10000.0,
                commission: float = 0.001, slippage: float = 0.0005):
        """
        Initialisiert die Backtesting-Engine.
        
        Args:
            data_handler: Datenhandler für den Zugriff auf historische Daten
            strategy: Handelsstrategie zur Evaluation
            initial_balance: Anfangsguthaben
            commission: Handelsgebühr (als Dezimalwert, z.B. 0.001 für 0.1%)
            slippage: Slippage (als Dezimalwert)
        """
        self.data_handler = data_handler
        self.strategy = strategy
        self.initial_balance = initial_balance
        self.commission = commission
        self.slippage = slippage
        
        # Ergebnisse
        self.results = None
        
        logger.info(f"BacktestEngine initialisiert: Strategy={strategy.name}, "
                  f"Balance=${initial_balance:.2f}, Commission={commission:.4f}, "
                  f"Slippage={slippage:.4f}")
    
    def run(self, symbol: str, timeframe: str, start_date: Union[str, datetime],
           end_date: Union[str, datetime] = None) -> Dict:
        """
        Führt einen Backtest für den angegebenen Zeitraum durch.
        
        Args:
            symbol: Handelssymbol (z.B. "BTCUSDT")
            timeframe: Zeitrahmen der Kerzen (z.B. "1h", "1d")
            start_date: Startdatum des Backtests
            end_date: Enddatum des Backtests (optional, Standard: aktuelles Datum)
            
        Returns:
            Dictionary mit Backtest-Ergebnissen
        """
        start_time = time.time()
        logger.info(f"Starte Backtest für {symbol}, Timeframe {timeframe}, "
                  f"Zeitraum: {start_date} bis {end_date or 'jetzt'}")
        
        # Historische Daten abrufen
        data = self.data_handler.get_historical_data(
            symbol=symbol,
            timeframe=timeframe,
            start_date=start_date,
            end_date=end_date
        )
        
        if data is None or data.empty:
            logger.error("Keine Daten für Backtest verfügbar")
            return {
                'success': False,
                'error': "Keine Daten verfügbar"
            }
        
        logger.info(f"Historische Daten abgerufen: {len(data)} Datenpunkte von "
                  f"{data.index[0]} bis {data.index[-1]}")
        
        # Simulation durchführen
        self.results = self._simulate_trading(data, symbol)
        
        # Performance-Metriken berechnen
        metrics = self._calculate_performance_metrics()
        self.results['metrics'] = metrics
        
        # Zusammenfassung ausgeben
        logger.info(f"Backtest abgeschlossen in {time.time() - start_time:.2f} Sekunden")
        logger.info(f"Trades: {len(self.results['trades'])}, "
                  f"Win Rate: {metrics['win_rate']:.2%}, "
                  f"Profit: ${metrics['net_profit']:.2f}, "
                  f"Rendite: {metrics['return']:.2%}")
        
        return self.results
    
    def _simulate_trading(self, data: pd.DataFrame, symbol: str) -> Dict:
        """
        Simuliert den Handel auf historischen Daten.
        
        Args:
            data: DataFrame mit historischen OHLCV-Daten
            symbol: Handelssymbol
            
        Returns:
            Dictionary mit Simulationsergebnissen
        """
        # Daten überprüfen
        if len(data) < 30:
            logger.warning(f"Wenige Datenpunkte für Simulation: {len(data)}")
        
        # Initialisierung
        balance = self.initial_balance
        position = None  # None = keine Position, 'long' = Long-Position, 'short' = Short-Position
        position_size = 0.0
        entry_price = 0.0
        entry_time = None
        stop_loss = 0.0
        take_profit = 0.0
        
        equity_curve = []  # Verlauf des Gesamtvermögens
        trades = []        # Abgeschlossene Trades
        signals = []       # Generierte Signale
        
        # Für jeden Zeitpunkt im Datensatz
        for i in range(30, len(data)):  # Start bei 30, um genügend Daten für Indikatoren zu haben
            # Aktuelle Daten bis zum Zeitpunkt i
            current_data = data.iloc[:i+1].copy()
            current_time = current_data.index[-1]
            
            # Aktuelle Preisdaten
            current_close = current_data['close'].iloc[-1]
            current_high = current_data['high'].iloc[-1]
            current_low = current_data['low'].iloc[-1]
            
            # Aktuelles Equity berechnen
            current_equity = balance
            if position == 'long':
                current_equity += position_size * (current_close - entry_price)
            elif position == 'short':
                current_equity += position_size * (entry_price - current_close)
            
            # Equity-Kurve aktualisieren
            equity_curve.append({
                'timestamp': current_time,
                'balance': balance,
                'equity': current_equity
            })
            
            # Prüfen, ob Stop-Loss oder Take-Profit getroffen wurden
            if position == 'long':
                # Stop-Loss prüfen
                if current_low <= stop_loss:
                    # Stop-Loss wurde getroffen
                    exit_price = self._apply_slippage(stop_loss, 'sell')
                    profit = position_size * (exit_price - entry_price)
                    commission_fee = position_size * exit_price * self.commission
                    net_profit = profit - commission_fee
                    
                    # Trade abschließen
                    trades.append({
                        'symbol': symbol,
                        'position': position,
                        'entry_time': entry_time,
                        'exit_time': current_time,
                        'entry_price': entry_price,
                        'exit_price': exit_price,
                        'size': position_size,
                        'profit': profit,
                        'commission': commission_fee,
                        'net_profit': net_profit,
                        'exit_reason': 'stop_loss'
                    })
                    
                    # Balance aktualisieren
                    balance += net_profit
                    
                    logger.info(f"Stop-Loss (Long): Exit bei ${exit_price:.2f}, "
                              f"Profit=${net_profit:.2f}")
                    
                    # Position zurücksetzen
                    position = None
                    position_size = 0.0
                    entry_price = 0.0
                    entry_time = None
                    stop_loss = 0.0
                    take_profit = 0.0
                    
                # Take-Profit prüfen
                elif current_high >= take_profit:
                    # Take-Profit wurde getroffen
                    exit_price = self._apply_slippage(take_profit, 'sell')
                    profit = position_size * (exit_price - entry_price)
                    commission_fee = position_size * exit_price * self.commission
                    net_profit = profit - commission_fee
                    
                    # Trade abschließen
                    trades.append({
                        'symbol': symbol,
                        'position': position,
                        'entry_time': entry_time,
                        'exit_time': current_time,
                        'entry_price': entry_price,
                        'exit_price': exit_price,
                        'size': position_size,
                        'profit': profit,
                        'commission': commission_fee,
                        'net_profit': net_profit,
                        'exit_reason': 'take_profit'
                    })
                    
                    # Balance aktualisieren
                    balance += net_profit
                    
                    logger.info(f"Take-Profit (Long): Exit bei ${exit_price:.2f}, "
                              f"Profit=${net_profit:.2f}")
                    
                    # Position zurücksetzen
                    position = None
                    position_size = 0.0
                    entry_price = 0.0
                    entry_time = None
                    stop_loss = 0.0
                    take_profit = 0.0
            
            elif position == 'short':
                # Stop-Loss prüfen
                if current_high >= stop_loss:
                    # Stop-Loss wurde getroffen
                    exit_price = self._apply_slippage(stop_loss, 'buy')
                    profit = position_size * (entry_price - exit_price)
                    commission_fee = position_size * exit_price * self.commission
                    net_profit = profit - commission_fee
                    
                    # Trade abschließen
                    trades.append({
                        'symbol': symbol,
                        'position': position,
                        'entry_time': entry_time,
                        'exit_time': current_time,
                        'entry_price': entry_price,
                        'exit_price': exit_price,
                        'size': position_size,
                        'profit': profit,
                        'commission': commission_fee,
                        'net_profit': net_profit,
                        'exit_reason': 'stop_loss'
                    })
                    
                    # Balance aktualisieren
                    balance += net_profit
                    
                    logger.info(f"Stop-Loss (Short): Exit bei ${exit_price:.2f}, "
                              f"Profit=${net_profit:.2f}")
                    
                    # Position zurücksetzen
                    position = None
                    position_size = 0.0
                    entry_price = 0.0
                    entry_time = None
                    stop_loss = 0.0
                    take_profit = 0.0
                    
                # Take-Profit prüfen
                elif current_low <= take_profit:
                    # Take-Profit wurde getroffen
                    exit_price = self._apply_slippage(take_profit, 'buy')
                    profit = position_size * (entry_price - exit_price)
                    commission_fee = position_size * exit_price * self.commission
                    net_profit = profit - commission_fee
                    
                    # Trade abschließen
                    trades.append({
                        'symbol': symbol,
                        'position': position,
                        'entry_time': entry_time,
                        'exit_time': current_time,
                        'entry_price': entry_price,
                        'exit_price': exit_price,
                        'size': position_size,
                        'profit': profit,
                        'commission': commission_fee,
                        'net_profit': net_profit,
                        'exit_reason': 'take_profit'
                    })
                    
                    # Balance aktualisieren
                    balance += net_profit
                    
                    logger.info(f"Take-Profit (Short): Exit bei ${exit_price:.2f}, "
                              f"Profit=${net_profit:.2f}")
                    
                    # Position zurücksetzen
                    position = None
                    position_size = 0.0
                    entry_price = 0.0
                    entry_time = None
                    stop_loss = 0.0
                    take_profit = 0.0
            
            # Nur Handelssignal generieren, wenn keine Position besteht
            if position is None:
                # Strategie evaluieren
                # Strategie evaluieren
                action_signal, entry_price_signal, stop_loss_signal, metadata_signal = self.strategy.generate_signal(current_data)
                
                # Signal speichern
                signals.append({
                    'timestamp': current_time,
                    'price': current_close,
                    'action': action_signal,
                    'details': metadata_signal
                })
                
                # Bei Kauf- oder Verkaufs-Signal eine Position eröffnen
                if action_signal in ['BUY', 'SELL']: # Use uppercase signals from strategy
                    # Position eröffnen
                    position = 'long' if action_signal == 'BUY' else 'short'
                    
                    # Einstiegspreis mit Slippage berechnen
                    entry_price = self._apply_slippage(current_close, action_signal)
                    entry_time = current_time
                    
                    # Stop-Loss und Take-Profit aus Signal verwenden oder berechnen
                    # Use the values returned by generate_signal
                    stop_loss = stop_loss_signal
                    take_profit = take_profit_signal
                    
                    # Standardwerte, falls nicht im Signal enthalten (Diese Logik sollte in der Strategie sein)
                    # Entferne diese Logik hier, da die Strategie SL/TP zurückgeben sollte
                    # if stop_loss == 0.0:
                    #     stop_loss = self.strategy.calculate_stop_loss(current_data, signal)
                    # if take_profit == 0.0:
                    #     take_profit = self.strategy.calculate_take_profit(current_data, signal)
                    
                    # Position Size berechnen (feste 2% Risiko)
                    risk_pct = 0.02  # 2% Risiko pro Trade
                    risk_amount = balance * risk_pct
                    
                    # Risiko berechnen
                    if position == 'long':
                        risk_per_unit = entry_price - stop_loss
                    else:  # short
                        risk_per_unit = stop_loss - entry_price
                    
                    # Position Size berechnen (mit mindestens 0.001)
                    if risk_per_unit > 0:
                        position_size = max(risk_amount / risk_per_unit, 0.001)
                    else:
                        # Fallback: 10% des Guthabens
                        position_size = (balance * 0.1) / entry_price
                    
                    # Gebühren berechnen und abziehen
                    commission_fee = position_size * entry_price * self.commission
                    balance -= commission_fee
                    
                    logger.info(f"{action_signal} Signal: Eintritt bei ${entry_price:.2f}, "
                               f"Stop-Loss=${stop_loss:.2f}, Take-Profit=${take_profit:.2f}, "
                               f"Size={position_size:.6f}, Gebühr=${commission_fee:.2f}")
        # Wenn am Ende des Backtests noch eine Position besteht, diese schließen
        if position is not None:
            # Letzter Preis
            last_price = data['close'].iloc[-1]
            last_time = data.index[-1]
            
            # Position schließen
            if position == 'long':
                exit_price = self._apply_slippage(last_price, 'sell')
                profit = position_size * (exit_price - entry_price)
            else:  # short
                exit_price = self._apply_slippage(last_price, 'buy')
                profit = position_size * (entry_price - exit_price)
                
            commission_fee = position_size * exit_price * self.commission
            net_profit = profit - commission_fee
            
            # Trade abschließen
            trades.append({
                'symbol': symbol,
                'position': position,
                'entry_time': entry_time,
                'exit_time': last_time,
                'entry_price': entry_price,
                'exit_price': exit_price,
                'size': position_size,
                'profit': profit,
                'commission': commission_fee,
                'net_profit': net_profit,
                'exit_reason': 'end_of_backtest'
            })
            
            # Balance aktualisieren
            balance += net_profit
            
            logger.info(f"End of Backtest: {position.capitalize()} Position geschlossen bei ${exit_price:.2f}, "
                      f"Profit=${net_profit:.2f}")
        
        # Ergebnisse zusammenstellen
        results = {
            'symbol': symbol,
            'start_date': data.index[0],
            'end_date': data.index[-1],
            'initial_balance': self.initial_balance,
            'final_balance': balance,
            'equity_curve': equity_curve,
            'trades': trades,
            'signals': signals,
            'strategy': self.strategy.name,
            'success': True
        }
        
        return results
    
    def _apply_slippage(self, price: float, action: str) -> float:
        """
        Wendet Slippage auf einen Preis an.
        
        Args:
            price: Originalpreis
            action: Handelsaktion ('buy' oder 'sell')
            
        Returns:
            Preis mit angewandter Slippage
        """
        if action.lower() == 'buy':
            # Für Käufe: Preis erhöhen
            return price * (1 + self.slippage)
        elif action.lower() == 'sell':
            # Für Verkäufe: Preis reduzieren
            return price * (1 - self.slippage)
        return price
    
    def _calculate_performance_metrics(self) -> Dict:
        """
        Berechnet Performance-Metriken für den Backtest.
        
        Returns:
            Dictionary mit Performance-Metriken
        """
        if not self.results or not self.results.get('trades'):
            return {}
        
        trades = self.results['trades']
        equity_curve = self.results['equity_curve']
        
        # Basismetriken
        total_trades = len(trades)
        winning_trades = [t for t in trades if t['net_profit'] > 0]
        losing_trades = [t for t in trades if t['net_profit'] <= 0]
        
        win_count = len(winning_trades)
        loss_count = len(losing_trades)
        
        win_rate = win_count / total_trades if total_trades > 0 else 0
        
        # Gewinn- und Verlustmetriken
        gross_profit = sum(t['net_profit'] for t in winning_trades) if winning_trades else 0
        gross_loss = sum(t['net_profit'] for t in losing_trades) if losing_trades else 0
        net_profit = gross_profit + gross_loss
        
        avg_win = gross_profit / win_count if win_count > 0 else 0
        avg_loss = gross_loss / loss_count if loss_count > 0 else 0
        
        # Profit Factor
        profit_factor = abs(gross_profit / gross_loss) if gross_loss != 0 else float('inf')
        
        # Return on Investment
        roi = net_profit / self.initial_balance
        
        # Drawdown-Berechnung
        equity_values = [e['equity'] for e in equity_curve]
        drawdowns = []
        peak = equity_values[0]
        
        for equity in equity_values:
            if equity > peak:
                peak = equity
            drawdown = (peak - equity) / peak if peak > 0 else 0
            drawdowns.append(drawdown)
        
        max_drawdown = max(drawdowns) if drawdowns else 0
        avg_drawdown = sum(drawdowns) / len(drawdowns) if drawdowns else 0
        
        # Sharpe Ratio (vereinfacht)
        if len(equity_values) > 1:
            returns = [
                (equity_values[i] - equity_values[i-1]) / equity_values[i-1]
                for i in range(1, len(equity_values))
            ]
            
            avg_return = sum(returns) / len(returns)
            std_return = np.std(returns) if len(returns) > 1 else 0
            
            # Annualisierter Sharpe Ratio (angenommen: tägliche Daten)
            risk_free_rate = 0.02 / 365  # 2% jährlich, auf täglich umgerechnet
            sharpe_ratio = (avg_return - risk_free_rate) / std_return * np.sqrt(252) if std_return > 0 else 0
        else:
            sharpe_ratio = 0
        
        # Calmar Ratio
        annual_return = roi * (252 / len(equity_values)) if len(equity_values) > 0 else 0
        calmar_ratio = annual_return / max_drawdown if max_drawdown > 0 else 0
        
        return {
            'total_trades': total_trades,
            'winning_trades': win_count,
            'losing_trades': loss_count,
            'win_rate': win_rate,
            'gross_profit': gross_profit,
            'gross_loss': gross_loss,
            'net_profit': net_profit,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'return': roi,
            'max_drawdown': max_drawdown,
            'avg_drawdown': avg_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'calmar_ratio': calmar_ratio,
            'annualized_return': annual_return
        }
    
    def plot_equity_curve(self, save_path: str = None) -> None:
        """
        Erstellt eine Grafik der Equity-Kurve.
        
        Args:
            save_path: Pfad zum Speichern der Grafik (optional)
        """
        if not self.results or not self.results.get('equity_curve'):
            logger.warning("Keine Daten für Equity-Kurve vorhanden")
            return
        
        equity_curve = self.results['equity_curve']
        trades = self.results['trades']
        
        # DataFrame für Equity-Kurve erstellen
        df_equity = pd.DataFrame(equity_curve)
        df_equity.set_index('timestamp', inplace=True)
        
        # Grafik erstellen
        plt.figure(figsize=(12, 8))
        
        # Equity-Kurve
        plt.subplot(2, 1, 1)
        plt.plot(df_equity.index, df_equity['equity'], label='Equity', color='blue')
        plt.plot(df_equity.index, df_equity['balance'], label='Balance', color='green', linestyle='--')
        
        # Trades markieren
        for trade in trades:
            if trade['net_profit'] > 0:
                color = 'green'
                marker = '^'  # Dreieck nach oben für Gewinne
            else:
                color = 'red'
                marker = 'v'  # Dreieck nach unten für Verluste
                
            plt.scatter(
                trade['exit_time'], 
                trade['exit_price'],
                color=color,
                marker=marker,
                s=100,
                alpha=0.7
            )
        
        plt.title(f"Equity-Kurve - {self.results['symbol']} - {self.strategy.name}")
        plt.ylabel('Equity ($)')
        plt.grid(True)
        plt.legend()
        
        # Drawdown
        plt.subplot(2, 1, 2)
        equity_values = np.array(df_equity['equity'])
        peak = np.maximum.accumulate(equity_values)
        drawdown = (peak - equity_values) / peak
        
        plt.fill_between(df_equity.index, 0, drawdown * 100, color='red', alpha=0.3)
        plt.title('Drawdown (%)')
        plt.ylabel('Drawdown (%)')
        plt.grid(True)
        plt.tight_layout()
        
        # Grafik speichern, wenn Pfad angegeben
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Equity-Kurve gespeichert: {save_path}")
        
        plt.show()
        
    def save_results(self, filename: str) -> bool:
        """
        Speichert die Backtesting-Ergebnisse in einer Datei.
        
        Args:
            filename: Dateiname zum Speichern der Ergebnisse
            
        Returns:
            True bei Erfolg, False bei Fehler
        """
        if not self.results:
            logger.warning("Keine Ergebnisse zum Speichern vorhanden")
            return False
        
        try:
            # Verzeichnis erstellen, falls nötig
            directory = os.path.dirname(filename)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            
            # Timestamps in ISO-Format konvertieren für JSON-Serialisierung
            results_copy = self.results.copy()
            
            for trade in results_copy['trades']:
                trade['entry_time'] = trade['entry_time'].isoformat() if hasattr(trade['entry_time'], 'isoformat') else trade['entry_time']
                trade['exit_time'] = trade['exit_time'].isoformat() if hasattr(trade['exit_time'], 'isoformat') else trade['exit_time']
            
            for point in results_copy['equity_curve']:
                point['timestamp'] = point['timestamp'].isoformat() if hasattr(point['timestamp'], 'isoformat') else point['timestamp']
            
            for signal in results_copy['signals']:
                signal['timestamp'] = signal['timestamp'].isoformat() if hasattr(signal['timestamp'], 'isoformat') else signal['timestamp']
            
            results_copy['start_date'] = results_copy['start_date'].isoformat() if hasattr(results_copy['start_date'], 'isoformat') else results_copy['start_date']
            results_copy['end_date'] = results_copy['end_date'].isoformat() if hasattr(results_copy['end_date'], 'isoformat') else results_copy['end_date']
            
            # Als JSON speichern
            with open(filename, 'w') as f:
                json.dump(results_copy, f, indent=2)
            
            logger.info(f"Ergebnisse gespeichert: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Fehler beim Speichern der Ergebnisse: {e}")
            return False
            
    def load_results(self, filename: str) -> bool:
        """
        Lädt Backtesting-Ergebnisse aus einer Datei.
        
        Args:
            filename: Dateiname zum Laden der Ergebnisse
            
        Returns:
            True bei Erfolg, False bei Fehler
        """
        try:
            with open(filename, 'r') as f:
                self.results = json.load(f)
            
            # Timestamps aus ISO-Format konvertieren
            for trade in self.results['trades']:
                trade['entry_time'] = pd.to_datetime(trade['entry_time'])
                trade['exit_time'] = pd.to_datetime(trade['exit_time'])
            
            for point in self.results['equity_curve']:
                point['timestamp'] = pd.to_datetime(point['timestamp'])
            
            for signal in self.results['signals']:
                signal['timestamp'] = pd.to_datetime(signal['timestamp'])
            
            self.results['start_date'] = pd.to_datetime(self.results['start_date'])
            self.results['end_date'] = pd.to_datetime(self.results['end_date'])
            
            logger.info(f"Ergebnisse geladen: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Fehler beim Laden der Ergebnisse: {e}")
            return False
