"""
Erweiterte Backtesting-Funktionalität für die Smart Money Strategie.

Dieses Modul enthält die SmartMoneyBacktester-Klasse, die speziell auf die
Optimierung und Validierung der Smart Money Strategie ausgerichtet ist.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import logging
import time
import os
import json
import itertools
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any, Tuple
from tqdm import tqdm
import concurrent.futures
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter

from backtesting.backtest_engine import BacktestEngine
from strategies.smart_money import SmartMoneyStrategy

# Konfiguriere Logging
logger = logging.getLogger(__name__)


class SmartMoneyBacktester:
    """
    Spezialisierter Backtester für die Smart Money Strategie.
    
    Diese Klasse erweitert die Standard-Backtesting-Funktionalität um spezifische
    Features für die optimale Nutzung und Parametrisierung der Smart Money Strategie.
    """
    
    def __init__(self, data_handler, config: Dict, initial_balance: float = 10000.0,
                 commission: float = 0.001, slippage: float = 0.0005):
        """
        Initialisiert den Smart Money Backtester.
        
        Args:
            data_handler: Daten-Handler für den Zugriff auf historische Daten
            config: Konfigurationsparameter
            initial_balance: Anfangsguthaben
            commission: Handelsgebühr (als Dezimalwert)
            slippage: Slippage (als Dezimalwert)
        """
        self.data_handler = data_handler
        self.config = config
        self.initial_balance = initial_balance
        self.commission = commission
        self.slippage = slippage
        
        # Ergebnisse
        self.results = None
        self.optimization_results = None
        self.filter_study_results = None
        
        logger.info(f"SmartMoneyBacktester initialisiert: "
                   f"Balance=${initial_balance:.2f}, Commission={commission:.4f}, "
                   f"Slippage={slippage:.4f}")
    
    def run_backtest(self, strategy_params: Dict, symbol: str, timeframe: str, 
                     start_date: Union[str, datetime], end_date: Union[str, datetime] = None) -> Dict:
        """
        Führt einen einzelnen Backtest mit den angegebenen Parametern durch.
        
        Args:
            strategy_params: Parameter für die Smart Money Strategie
            symbol: Handelssymbol (z.B. "BTCUSDT")
            timeframe: Zeitrahmen der Kerzen (z.B. "1h", "1d")
            start_date: Startdatum des Backtests
            end_date: Enddatum des Backtests (optional)
            
        Returns:
            Dictionary mit Backtest-Ergebnissen
        """
        # Strategie mit den angegebenen Parametern erstellen
        combined_config = {**self.config, **strategy_params}
        strategy = SmartMoneyStrategy(combined_config)
        
        # BacktestEngine initialisieren
        backtest_engine = BacktestEngine(
            data_handler=self.data_handler,
            strategy=strategy,
            initial_balance=self.initial_balance,
            commission=self.commission,
            slippage=self.slippage
        )
        
        # Backtest durchführen
        results = backtest_engine.run(
            symbol=symbol,
            timeframe=timeframe,
            start_date=start_date,
            end_date=end_date
        )
        
        # Ergebnisse speichern
        self.results = results
        
        return results
    
    def parameter_sweep(self, symbol: str, timeframe: str, start_date: Union[str, datetime],
                       end_date: Union[str, datetime] = None, param_grid: Dict = None,
                       parallel: bool = True, max_workers: int = 4) -> Dict:
        """
        Führt einen Parameter-Sweep durch, um die optimalen Einstellungen zu finden.
        
        Args:
            symbol: Handelssymbol (z.B. "BTCUSDT")
            timeframe: Zeitrahmen der Kerzen (z.B. "1h")
            start_date: Startdatum des Backtests
            end_date: Enddatum des Backtests (optional)
            param_grid: Dictionary mit Parameter-Bereichen für Grid Search
            parallel: Ob Backtest-Läufe parallel ausgeführt werden sollen
            max_workers: Maximale Anzahl an Worker-Prozessen bei paralleler Ausführung
            
        Returns:
            Dictionary mit Optimierungsergebnissen
        """
        start_time = time.time()
        
        # Standardwerte für Parameter-Grid, falls nicht angegeben
        if param_grid is None:
            param_grid = {
                'VOLUME_THRESHOLD': [10000, 50000, 100000, 250000, 500000, 1000000],
                'LIQUIDITY_FACTOR': [0.8, 1.0, 1.2, 1.5],
                'USE_VOLUME_FILTER': [True, False],
                'USE_KEY_LEVELS': [True, False],
                'USE_PATTERN_RECOGNITION': [True, False],
                'USE_ORDER_FLOW': [True, False],
                'USE_LIQUIDITY_SWEEP': [True, False]
            }
        
        # Alle möglichen Parameterkombinationen generieren
        param_names = list(param_grid.keys())
        param_values = list(param_grid.values())
        param_combinations = list(itertools.product(*param_values))
        
        logger.info(f"Starte Parameter-Sweep mit {len(param_combinations)} Kombinationen")
        logger.info(f"Parameter-Grid: {param_grid}")
        
        results = []
        
        # Funktion für einen einzelnen Backtest-Lauf
        def run_single_backtest(params_tuple):
            # Parameter-Dictionary erstellen
            params = {param_names[i]: params_tuple[i] for i in range(len(param_names))}
            
            # Backtest durchführen
            backtest_results = self.run_backtest(
                strategy_params=params,
                symbol=symbol,
                timeframe=timeframe,
                start_date=start_date,
                end_date=end_date
            )
            
            if not backtest_results.get('success', False):
                logger.warning(f"Backtest fehlgeschlagen mit Parametern: {params}")
                return None
            
            # Relevante Metriken extrahieren
            metrics = backtest_results['metrics']
            trades_count = metrics['total_trades']
            
            # Nur speichern, wenn es tatsächlich Trades gab
            if trades_count > 0:
                result = {
                    'params': params,
                    'metrics': {
                        'net_profit': metrics['net_profit'],
                        'return': metrics['return'],
                        'win_rate': metrics['win_rate'],
                        'profit_factor': metrics['profit_factor'],
                        'sharpe_ratio': metrics['sharpe_ratio'],
                        'max_drawdown': metrics['max_drawdown']
                    },
                    'trades_count': trades_count
                }
                return result
            
            return None
        
        # Backtests ausführen (parallel oder sequentiell)
        if parallel and max_workers > 1:
            with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
                futures = [executor.submit(run_single_backtest, params) for params in param_combinations]
                
                # Fortschritt anzeigen
                with tqdm(total=len(param_combinations), desc="Optimizing") as pbar:
                    for future in concurrent.futures.as_completed(futures):
                        result = future.result()
                        if result is not None:
                            results.append(result)
                        pbar.update(1)
        else:
            # Sequentielle Ausführung mit Fortschrittsanzeige
            for params in tqdm(param_combinations, desc="Optimizing"):
                result = run_single_backtest(params)
                if result is not None:
                    results.append(result)
        
        # Ergebnisse nach Performance sortieren
        sorted_results = sorted(
            [r for r in results if r is not None],
            key=lambda x: (
                x['metrics']['net_profit'],              # Hauptkriterium: Nettogewinn
                x['metrics']['sharpe_ratio'],            # Zweites Kriterium: Sharpe Ratio
                -x['metrics']['max_drawdown']            # Drittes Kriterium: Minimaler Drawdown
            ),
            reverse=True
        )
        
        optimization_results = {
            'best_params': sorted_results[0]['params'] if sorted_results else None,
            'best_metrics': sorted_results[0]['metrics'] if sorted_results else None,
            'all_results': sorted_results,
            'duration': time.time() - start_time,
            'combinations_tested': len(param_combinations),
            'valid_results': len(sorted_results)
        }
        
        self.optimization_results = optimization_results
        
        logger.info(f"Parameter-Sweep abgeschlossen in {optimization_results['duration']:.2f} Sekunden")
        if sorted_results:
            logger.info(f"Beste Parameter: {optimization_results['best_params']}")
            logger.info(f"Beste Metriken: Nettogewinn=${optimization_results['best_metrics']['net_profit']:.2f}, "
                      f"Win Rate={optimization_results['best_metrics']['win_rate']:.2%}, "
                      f"Sharpe={optimization_results['best_metrics']['sharpe_ratio']:.2f}")
        else:
            logger.warning("Keine gültigen Ergebnisse gefunden!")
        
        return optimization_results
    
    def run_filter_activation_study(self, symbol: str, timeframe: str, 
                                   start_date: Union[str, datetime],
                                   end_date: Union[str, datetime] = None,
                                   volume_thresholds: List[int] = None) -> Dict:
        """
        Führt eine Studie zur schrittweisen Aktivierung der Filter durch.
        
        Diese Methode untersucht, wie sich das Hinzufügen verschiedener Filter auf 
        die Performance der Smart Money Strategie auswirkt.
        
        Args:
            symbol: Handelssymbol (z.B. "BTCUSDT")
            timeframe: Zeitrahmen der Kerzen (z.B. "1h")
            start_date: Startdatum des Backtests
            end_date: Enddatum des Backtests (optional)
            volume_thresholds: Liste von Volumen-Schwellenwerten zum Testen
            
        Returns:
            Dictionary mit Studienergebnissen
        """
        if volume_thresholds is None:
            volume_thresholds = [10000, 50000, 100000, 250000, 500000, 1000000]
        
        logger.info(f"Starte Filter-Aktivierungsstudie mit {len(volume_thresholds)} Volumen-Schwellen")
        
        # Schrittweise Filter-Aktivierung
        filter_steps = [
            {"name": "Nur Volumen", "filters": {"USE_VOLUME_FILTER": True, "USE_KEY_LEVELS": False, 
                                             "USE_PATTERN_RECOGNITION": False, "USE_ORDER_FLOW": False, 
                                             "USE_LIQUIDITY_SWEEP": False}},
            {"name": "+ Key Levels", "filters": {"USE_VOLUME_FILTER": True, "USE_KEY_LEVELS": True, 
                                              "USE_PATTERN_RECOGNITION": False, "USE_ORDER_FLOW": False, 
                                              "USE_LIQUIDITY_SWEEP": False}},
            {"name": "+ Pattern", "filters": {"USE_VOLUME_FILTER": True, "USE_KEY_LEVELS": True, 
                                           "USE_PATTERN_RECOGNITION": True, "USE_ORDER_FLOW": False, 
                                           "USE_LIQUIDITY_SWEEP": False}},
            {"name": "+ Order Flow", "filters": {"USE_VOLUME_FILTER": True, "USE_KEY_LEVELS": True, 
                                              "USE_PATTERN_RECOGNITION": True, "USE_ORDER_FLOW": True, 
                                              "USE_LIQUIDITY_SWEEP": False}},
            {"name": "+ Liquidity Sweep", "filters": {"USE_VOLUME_FILTER": True, "USE_KEY_LEVELS": True, 
                                                   "USE_PATTERN_RECOGNITION": True, "USE_ORDER_FLOW": True, 
                                                   "USE_LIQUIDITY_SWEEP": True}},
        ]
        
        study_results = []
        
        # Für jede Filter-Kombination und jeden Volumen-Schwellenwert einen Backtest durchführen
        total_tests = len(filter_steps) * len(volume_thresholds)
        with tqdm(total=total_tests, desc="Filter Study") as pbar:
            for filter_step in filter_steps:
                for volume_threshold in volume_thresholds:
                    # Parameter für diesen Test erstellen
                    params = {
                        **filter_step["filters"],
                        "VOLUME_THRESHOLD": volume_threshold
                    }
                    
                    # Backtest durchführen
                    backtest_results = self.run_backtest(
                        strategy_params=params,
                        symbol=symbol,
                        timeframe=timeframe,
                        start_date=start_date,
                        end_date=end_date
                    )
                    
                    if backtest_results.get('success', False):
                        metrics = backtest_results['metrics']
                        trades = backtest_results['trades']
                        
                        # Ergebnis speichern
                        result = {
                            "step": filter_step["name"],
                            "volume_threshold": volume_threshold,
                            "filters": filter_step["filters"],
                            "profit_loss": metrics['net_profit'],
                            "trades": metrics['total_trades'],
                            "win_rate": metrics['win_rate'],
                            "profit_factor": metrics['profit_factor'],
                            "max_drawdown": metrics['max_drawdown'],
                            "sharpe_ratio": metrics['sharpe_ratio']
                        }
                        
                        study_results.append(result)
                    
                    pbar.update(1)
        
        logger.info(f"Filter-Aktivierungsstudie abgeschlossen: {len(study_results)} gültige Ergebnisse")
        
        result_data = {
            "results": study_results,
            "volume_thresholds_tested": volume_thresholds,
            "filter_steps": [step["name"] for step in filter_steps]
        }
        
        self.filter_study_results = result_data
        
        return result_data
    
    def visualize_optimization_results(self, save_path: str = None, show_plot: bool = True) -> None:
        """
        Visualisiert die Ergebnisse der Parameter-Optimierung.
        
        Args:
            save_path: Pfad zum Speichern der Visualisierung (optional)
            show_plot: Ob der Plot direkt angezeigt werden soll
        """
        if not self.optimization_results or not self.optimization_results.get('all_results'):
            logger.warning("Keine Optimierungsergebnisse zum Visualisieren vorhanden")
            return
        
        # Ergebnisse in DataFrame konvertieren
        results = self.optimization_results['all_results']
        data = []
        
        for result in results:
            row = {}
            # Parameter hinzufügen
            for param, value in result['params'].items():
                row[param] = value
            
            # Metriken hinzufügen
            for metric, value in result['metrics'].items():
                row[metric] = value
            
            row['trades_count'] = result['trades_count']
            data.append(row)
        
        df = pd.DataFrame(data)
        
        # Mehrere Plots erstellen
        fig, axes = plt.subplots(2, 2, figsize=(20, 16))
        fig.suptitle('Smart Money Strategy Optimization Results', fontsize=16)
        
        # 1. Net Profit vs. Drawdown (Farbkodiert nach Win Rate)
        ax = axes[0, 0]
        scatter = ax.scatter(
            df['max_drawdown'], 
            df['net_profit'],
            c=df['win_rate'],
            cmap='viridis',
            alpha=0.7,
            s=100
        )
        plt.colorbar(scatter, ax=ax, label='Win Rate')
        ax.set_xlabel('Max Drawdown')
        ax.set_ylabel('Net Profit ($)')
        ax.set_title('Profit vs. Risk Analysis')
        ax.grid(True, alpha=0.3)
        
        # Markiere die besten 3 Ergebnisse
        top_3 = df.nlargest(3, 'net_profit')
        for i, row in top_3.iterrows():
            ax.annotate(
                f"Top {i+1}",
                (row['max_drawdown'], row['net_profit']),
                xytext=(10, 10),
                textcoords='offset points',
                arrowprops=dict(arrowstyle='->', color='red')
            )
        
        # 2. Parameter-Heatmap (Win Rate)
        ax = axes[0, 1]
        
        # Wähle die wichtigsten Parameter für die Heatmap aus
        key_params = ['VOLUME_THRESHOLD', 'LIQUIDITY_FACTOR']
        if all(param in df.columns for param in key_params) and df[key_params[0]].nunique() > 1 and df[key_params[1]].nunique() > 1:
            pivot_data = df.pivot_table(
                values='win_rate',
                index=key_params[0],
                columns=key_params[1],
                aggfunc='mean'
            )
            
            sns.heatmap(pivot_data, annot=True, cmap='YlGnBu', ax=ax)
            ax.set_title(f'Win Rate by {key_params[0]} and {key_params[1]}')
        else:
            ax.text(0.5, 0.5, 'Insufficient data for heatmap', 
                   horizontalalignment='center', verticalalignment='center')
        
        # 3. Filter-Einfluss auf Profit
        ax = axes[1, 0]
        
        filter_columns = [c for c in df.columns if c.startswith('USE_')]
        if filter_columns:
            # Erstelle temporäre Spalte für Filter-Kombination
            df['filter_combo'] = df[filter_columns].apply(
                lambda row: ', '.join([c.replace('USE_', '') for c, v in zip(filter_columns, row) if v]), 
                axis=1
            )
            
            # Durchschnittlicher Profit pro Filter-Kombination
            filter_profit = df.groupby('filter_combo')['net_profit'].mean().sort_values(ascending=False)
            
            filter_profit.plot(kind='bar', ax=ax, color='skyblue')
            ax.set_xlabel('Filter Combination')
            ax.set_ylabel('Average Net Profit ($)')
            ax.set_title('Impact of Different Filter Combinations')
            plt.xticks(rotation=45, ha='right')
            ax.grid(True, alpha=0.3)
        else:
            ax.text(0.5, 0.5, 'No filter data available', 
                   horizontalalignment='center', verticalalignment='center')
        
        # 4. Sharpe Ratio vs. Trades Count
        ax = axes[1, 1]
        scatter = ax.scatter(
            df['trades_count'], 
            df['sharpe_ratio'],
            c=df['profit_factor'],
            cmap='plasma',
            alpha=0.7,
            s=100
        )
        plt.colorbar(scatter, ax=ax, label='Profit Factor')
        ax.set_xlabel('Number of Trades')
        ax.set_ylabel('Sharpe Ratio')
        ax.set_title('Efficiency Analysis')
        ax.grid(True, alpha=0.3)
        
        # Markiere die besten 3 Ergebnisse nach Sharpe
        top_3_sharpe = df.nlargest(3, 'sharpe_ratio')
        for i, row in top_3_sharpe.iterrows():
            ax.annotate(
                f"Top {i+1}",
                (row['trades_count'], row['sharpe_ratio']),
                xytext=(10, 10),
                textcoords='offset points',
                arrowprops=dict(arrowstyle='->', color='red')
            )
        
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        
        # Speichern, falls erforderlich
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Optimierungsvisualisierung gespeichert: {save_path}")
        
        # Anzeigen, falls erforderlich
        if show_plot:
            plt.show()
        else:
            plt.close()
    
    def generate_report(self, output_dir: str, filename_prefix: str) -> None:
        """
        Generiert einen umfassenden Bericht über die Backtest-Ergebnisse.
        
        Args:
            output_dir: Verzeichnis für die Ausgabe
            filename_prefix: Präfix für die Dateinamen
        """
        if not self.results:
            logger.warning("Keine Ergebnisse für Berichterstellung vorhanden")
            return
        
        # Verzeichnis erstellen, falls nicht vorhanden
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"{output_dir}/{filename_prefix}_{timestamp}"
        
        # 1. JSON-Ausgabe
        json_file = f"{base_filename}_report.json"
        
        # Copy the results to avoid modifying the original
        results_copy = self.results.copy()
        
        # Convert datetime objects to string for JSON serialization
        for trade in results_copy['trades']:
            trade['entry_time'] = trade['entry_time'].isoformat() if hasattr(trade['entry_time'], 'isoformat') else trade['entry_time']
            trade['exit_time'] = trade['exit_time'].isoformat() if hasattr(trade['exit_time'], 'isoformat') else trade['exit_time']
        
        for point in results_copy['equity_curve']:
            point['timestamp'] = point['timestamp'].isoformat() if hasattr(point['timestamp'], 'isoformat') else point['timestamp']
        
        for signal in results_copy['signals']:
            signal['timestamp'] = signal['timestamp'].isoformat() if hasattr(signal['timestamp'], 'isoformat') else signal['timestamp']
        
        results_copy['start_date'] = results_copy['start_date'].isoformat() if hasattr(results_copy['start_date'], 'isoformat') else results_copy['start_date']
        results_copy['end_date'] = results_copy['end_date'].isoformat() if hasattr(results_copy['end_date'], 'isoformat') else results_copy['end_date']
        
        with open(json_file, 'w') as f:
            json.dump(results_copy, f, indent=2)
        
        logger.info(f"JSON-Bericht gespeichert: {json_file}")
        
        # 2. CSV-Ausgabe für Trades
        csv_file = f"{base_filename}_trades.csv"
        
        trades_df = pd.DataFrame(self.results['trades'])
        trades_df.to_csv(csv_file, index=False)
        
        logger.info(f"Trades-CSV gespeichert: {csv_file}")
        
        # 3. Zusammenfassung als TXT
        txt_file = f"{base_filename}_summary.txt"
        
        metrics = self.results['metrics']
        
        with open(txt_file, 'w') as f:
            f.write(f"===== SMART MONEY STRATEGY BACKTEST REPORT =====\n")
            f.write(f"Datum: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write(f"Symbol: {self.results['symbol']}\n")
            f.write(f"Zeitraum: {self.results['start_date']} bis {self.results['end_date']}\n")
            f.write(f"Strategie: {self.results['strategy']}\n\n")
            
            f.write(f"==== PERFORMANCE METRICS ====\n")
            f.write(f"Anfangsguthaben: ${self.results['initial_balance']:.2f}\n")
            f.write(f"Endguthaben: ${self.results['final_balance']:.2f}\n")
            f.write(f"Gesamtgewinn: ${metrics['net_profit']:.2f}\n")
            f.write(f"Gesamtrendite: {metrics['return']:.2%}\n")
            f.write(f"Annualisierte Rendite: {metrics['annualized_return']:.2%}\n\n")
            
            f.write(f"==== HANDELSSTATISTIKEN ====\n")
            f.write(f"Gesamtzahl Trades: {metrics['total_trades']}\n")
            f.write(f"Gewinn-Trades: {metrics['winning_trades']}\n")
            f.write(f"Verlust-Trades: {metrics['losing_trades']}\n")
            f.write(f"Win Rate: {metrics['win_rate']:.2%}\n")
            f.write(f"Profit Factor: {metrics['profit_factor']:.2f}\n")
            f.write(f"Durchschnittlicher Gewinn: ${metrics['avg_win']:.2f}\n")
            f.write(f"Durchschnittlicher Verlust: ${metrics['avg_loss']:.2f}\n\n")
            
            f.write(f"==== RISIKOMETRIKEN ====\n")
            f.write(f"Maximaler Drawdown: {metrics['max_drawdown']:.2%}\n")
            f.write(f"Durchschnittlicher Drawdown: {metrics['avg_drawdown']:.2%}\n")
            f.write(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}\n")
            f.write(f"Calmar Ratio: {metrics['calmar_ratio']:.2f}\n\n")
            
            f.write(f"==== FILTEREINSTELLUNGEN ====\n")
            # Extrahiere Smart Money Parameter aus den Signalen oder Trades, wenn möglich
            if self.results.get('signals') and self.results['signals']:
                signal = self.results['signals'][0]
                if 'details' in signal and isinstance(signal['details'], dict):
                    details = signal['details']
                    if 'volume_threshold' in details:
                        f.write(f"Volumen-Schwelle: {details['volume_threshold']}\n")
                    if 'use_key_levels' in details:
                        f.write(f"Key Levels: {'Aktiviert' if details['use_key_levels'] else 'Deaktiviert'}\n")
                    if 'use_pattern_recognition' in details:
                        f.write(f"Pattern Recognition: {'Aktiviert' if details['use_pattern_recognition'] else 'Deaktiviert'}\n")
                    if 'use_order_flow' in details:
                        f.write(f"Order Flow: {'Aktiviert' if details['use_order_flow'] else 'Deaktiviert'}\n")
                    if 'use_liquidity_sweep' in details:
                        f.write(f"Liquidity Sweep: {'Aktiviert' if details['use_liquidity_sweep'] else 'Deaktiviert'}\n")
        
        logger.info(f"Zusammenfassung gespeichert: {txt_file}")
        
        # 4. Equity-Kurve als PNG
        plot_file = f"{base_filename}_equity_curve.png"
        
        # Erstelle Equity-Kurve
        equity_df = pd.DataFrame(self.results['equity_curve'])
        equity_df.set_index('timestamp', inplace=True)
        
        plt.figure(figsize=(12, 8))
        
        # Equity-Kurve
        plt.subplot(2, 1, 1)
        plt.plot(equity_df.index, equity_df['equity'], label='Equity', color='blue')
        plt.plot(equity_df.index, equity_df['balance'], label='Balance', color='green', linestyle='--')
        
        # Trades markieren
        for trade in self.results['trades']:
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
        
        plt.title(f"Equity-Kurve - {self.results['symbol']} - {self.results['strategy']}")
        plt.ylabel('Equity ($)')
        plt.grid(True)
        plt.legend()
        
        # Drawdown
        plt.subplot(2, 1, 2)
        equity_values = np.array(equity_df['equity'])
        peak = np.maximum.accumulate(equity_values)
        drawdown = (peak - equity_values) / peak
        
        plt.fill_between(equity_df.index, 0, drawdown * 100, color='red', alpha=0.3)
        plt.title('Drawdown (%)')
        plt.ylabel('Drawdown (%)')
        plt.grid(True)
        
        plt.tight_layout()
        plt.savefig(plot_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Equity-Kurve gespeichert: {plot_file}")
        
        # 5. HTML-Bericht (optional)
        html_file = f"{base_filename}_report.html"
        
        # Erstelle HTML-Bericht
        html_output = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Smart Money Strategy Backtest Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1, h2, h3 {{ color: #333; }}
                .metrics-container {{ display: flex; flex-wrap: wrap; }}
                .metric-card {{ 
                    background-color: #f5f5f5; border-radius: 8px; 
                    padding: 15px; margin: 10px; flex: 1; min-width: 200px; 
                }}
                .positive {{ color: green; }}
                .negative {{ color: red; }}
                table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                tr:nth-child(even) {{ background-color: #f9f9f9; }}
                .chart-container {{ margin-top: 30px; text-align: center; }}
                img {{ max-width: 100%; height: auto; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }}
            </style>
        </head>
        <body>
            <h1>Smart Money Strategy Backtest Report</h1>
            <p><strong>Datum:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>Symbol:</strong> {self.results['symbol']}</p>
            <p><strong>Zeitraum:</strong> {self.results['start_date']} bis {self.results['end_date']}</p>
            <p><strong>Strategie:</strong> {self.results['strategy']}</p>
            
            <h2>Performance Metriken</h2>
            <div class="metrics-container">
                <div class="metric-card">
                    <h3>Grundlegende Metriken</h3>
                    <p>Anfangsguthaben: <strong>${self.results['initial_balance']:.2f}</strong></p>
                    <p>Endguthaben: <strong>${self.results['final_balance']:.2f}</strong></p>
                    <p>Gesamtgewinn: <strong class="{'positive' if metrics['net_profit'] >= 0 else 'negative'}">${metrics['net_profit']:.2f}</strong></p>
                    <p>Gesamtrendite: <strong class="{'positive' if metrics['return'] >= 0 else 'negative'}">{metrics['return']:.2%}</strong></p>
                    <p>Annualisierte Rendite: <strong class="{'positive' if metrics['annualized_return'] >= 0 else 'negative'}">{metrics['annualized_return']:.2%}</strong></p>
                </div>
                
                <div class="metric-card">
                    <h3>Handelsstatistiken</h3>
                    <p>Gesamtzahl Trades: <strong>{metrics['total_trades']}</strong></p>
                    <p>Gewinn-Trades: <strong>{metrics['winning_trades']}</strong></p>
                    <p>Verlust-Trades: <strong>{metrics['losing_trades']}</strong></p>
                    <p>Win Rate: <strong>{metrics['win_rate']:.2%}</strong></p>
                    <p>Profit Factor: <strong>{metrics['profit_factor']:.2f}</strong></p>
                </div>
                
                <div class="metric-card">
                    <h3>Risikometriken</h3>
                    <p>Maximaler Drawdown: <strong class="negative">{metrics['max_drawdown']:.2%}</strong></p>
                    <p>Durchschnittlicher Drawdown: <strong class="negative">{metrics['avg_drawdown']:.2%}</strong></p>
                    <p>Sharpe Ratio: <strong>{metrics['sharpe_ratio']:.2f}</strong></p>
                    <p>Calmar Ratio: <strong>{metrics['calmar_ratio']:.2f}</strong></p>
                </div>
            </div>
            
            <h2>Filter-Einstellungen</h2>
            <ul>
        """
        
        # Extrahiere Smart Money Parameter aus den Signalen, wenn möglich
        if self.results.get('signals') and self.results['signals']:
            signal = self.results['signals'][0]
            if 'details' in signal and isinstance(signal['details'], dict):
                details = signal['details']
                if 'volume_threshold' in details:
                    html_output += f"<li>Volumen-Schwelle: <strong>{details['volume_threshold']}</strong></li>\n"
                if 'use_key_levels' in details:
                    html_output += f"<li>Key Levels: <strong>{'Aktiviert' if details['use_key_levels'] else 'Deaktiviert'}</strong></li>\n"
                if 'use_pattern_recognition' in details:
                    html_output += f"<li>Pattern Recognition: <strong>{'Aktiviert' if details['use_pattern_recognition'] else 'Deaktiviert'}</strong></li>\n"
                if 'use_order_flow' in details:
                    html_output += f"<li>Order Flow: <strong>{'Aktiviert' if details['use_order_flow'] else 'Deaktiviert'}</strong></li>\n"
                if 'use_liquidity_sweep' in details:
                    html_output += f"<li>Liquidity Sweep: <strong>{'Aktiviert' if details['use_liquidity_sweep'] else 'Deaktiviert'}</strong></li>\n"
        
        html_output += f"""
            </ul>
            
            <h2>Top 10 Trades</h2>
            <table>
                <tr>
                    <th>Einstieg</th>
                    <th>Ausstieg</th>
                    <th>Position</th>
                    <th>Einstiegspreis</th>
                    <th>Ausstiegspreis</th>
                    <th>Größe</th>
                    <th>Profit</th>
                    <th>Grund</th>
                </tr>
        """
        
        # Top 10 Trades nach Profit
        top_trades = sorted(self.results['trades'], key=lambda x: x['net_profit'], reverse=True)[:10]
        
        for trade in top_trades:
            html_output += f"""
                <tr>
                    <td>{trade['entry_time']}</td>
                    <td>{trade['exit_time']}</td>
                    <td>{trade['position'].upper()}</td>
                    <td>${trade['entry_price']:.2f}</td>
                    <td>${trade['exit_price']:.2f}</td>
                    <td>{trade['size']:.6f}</td>
                    <td class="{'positive' if trade['net_profit'] >= 0 else 'negative'}">${trade['net_profit']:.2f}</td>
                    <td>{trade['exit_reason']}</td>
                </tr>
            """
        
        html_output += f"""
            </table>
            
            <div class="chart-container">
                <h2>Equity-Kurve und Drawdown</h2>
                <img src="{os.path.basename(plot_file)}" alt="Equity-Kurve und Drawdown" />
            </div>
            
            <p><small>Bericht generiert am {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</small></p>
        </body>
        </html>
        """
        
        with open(html_file, 'w') as f:
            f.write(html_output)
        
        logger.info(f"HTML-Bericht gespeichert: {html_file}")
        
        return {"json": json_file, "csv": csv_file, "txt": txt_file, "plot": plot_file, "html": html_file}
    
    def run_complete_analysis(self, symbol: str, timeframe: str, start_date: Union[str, datetime],
                           end_date: Union[str, datetime] = None, output_dir: str = "results",
                           run_parameter_sweep: bool = True, run_filter_study: bool = True,
                           show_plots: bool = True) -> Dict:
        """
        Führt eine vollständige Analyse mit Parameter-Sweep, Filter-Aktivierungsstudie und Berichterstellung durch.
        
        Args:
            symbol: Handelssymbol (z.B. "BTCUSDT")
            timeframe: Zeitrahmen der Kerzen (z.B. "1h")
            start_date: Startdatum des Backtests
            end_date: Enddatum des Backtests (optional)
            output_dir: Verzeichnis für die Ausgabe
            run_parameter_sweep: Ob ein Parameter-Sweep durchgeführt werden soll
            run_filter_study: Ob eine Filter-Aktivierungsstudie durchgeführt werden soll
            show_plots: Ob Plots angezeigt werden sollen
            
        Returns:
            Dictionary mit Analyseergebnissen
        """
        start_time = time.time()
        logger.info(f"Starte vollständige Analyse für {symbol} {timeframe} von {start_date} bis {end_date or 'jetzt'}")
        
        # Verzeichnis erstellen, falls nicht vorhanden
        os.makedirs(output_dir, exist_ok=True)
        
        results = {
            "symbol": symbol,
            "timeframe": timeframe,
            "start_date": start_date,
            "end_date": end_date,
            "duration": None,
            "backtest_results": None,
            "optimization_results": None,
            "filter_study_results": None,
            "report_files": None
        }
        
        # 1. Parameter-Sweep durchführen, falls gewünscht
        if run_parameter_sweep:
            logger.info("Starte Parameter-Sweep...")
            optimization_results = self.parameter_sweep(
                symbol=symbol,
                timeframe=timeframe,
                start_date=start_date,
                end_date=end_date,
                parallel=True,
                max_workers=4
            )
            
            results["optimization_results"] = optimization_results
            
            # Visualisierungen erstellen
            if optimization_results and optimization_results.get('all_results'):
                optim_plot_path = f"{output_dir}/{symbol}_{timeframe}_optimization.png"
                self.visualize_optimization_results(save_path=optim_plot_path, show_plot=show_plots)
                results["optimization_plot"] = optim_plot_path
                
                # Beste Parameter für Backtest verwenden, falls vorhanden
                if optimization_results.get('best_params'):
                    logger.info(f"Verwende die besten Parameter aus dem Parameter-Sweep:")
                    for param, value in optimization_results['best_params'].items():
                        logger.info(f"  {param}: {value}")
                    
                    # Backtest mit den besten Parametern durchführen
                    backtest_results = self.run_backtest(
                        strategy_params=optimization_results['best_params'],
                        symbol=symbol,
                        timeframe=timeframe,
                        start_date=start_date,
                        end_date=end_date
                    )
                    
                    results["backtest_results"] = backtest_results
            
        # 2. Filter-Aktivierungsstudie durchführen, falls gewünscht
        if run_filter_study:
            logger.info("Starte Filter-Aktivierungsstudie...")
            filter_study_results = self.run_filter_activation_study(
                symbol=symbol,
                timeframe=timeframe,
                start_date=start_date,
                end_date=end_date
            )
            
            results["filter_study_results"] = filter_study_results
            
            # Visualisierungen erstellen
            if filter_study_results and filter_study_results.get('results'):
                filter_plot_path = f"{output_dir}/{symbol}_{timeframe}_filter_study.png"
                self.visualize_filter_study(study_results=filter_study_results, save_path=filter_plot_path, show_plot=show_plots)
                results["filter_study_plot"] = filter_plot_path
                
                # Beste Filter-Kombination und Volumen-Schwelle ermitteln
                filter_df = pd.DataFrame(filter_study_results['results'])
                # Nach Profit/Loss sortieren und das beste Ergebnis nehmen
                best_filter_result = filter_df.sort_values('profit_loss', ascending=False).iloc[0]
                
                logger.info(f"Beste Filter-Kombination aus der Studie:")
                logger.info(f"  Schritt: {best_filter_result['step']}")
                logger.info(f"  Volumen-Schwelle: {best_filter_result['volume_threshold']}")
                logger.info(f"  Profit/Loss: ${best_filter_result['profit_loss']:.2f}")
                logger.info(f"  Win Rate: {best_filter_result['win_rate']:.2%}")
                
                # Falls kein Parameter-Sweep durchgeführt wurde, führe einen Backtest mit der besten Filter-Kombination durch
                if not run_parameter_sweep or not results.get('backtest_results'):
                    # Parameter für den Backtest erstellen
                    best_filter_params = {
                        **best_filter_result['filters'],
                        "VOLUME_THRESHOLD": best_filter_result['volume_threshold']
                    }
                    
                    logger.info(f"Führe Backtest mit der besten Filter-Kombination durch")
                    backtest_results = self.run_backtest(
                        strategy_params=best_filter_params,
                        symbol=symbol,
                        timeframe=timeframe,
                        start_date=start_date,
                        end_date=end_date
                    )
                    
                    results["backtest_results"] = backtest_results
        
        # 3. Falls noch kein Backtest durchgeführt wurde, führe einen mit Standardparametern durch
        if not results.get('backtest_results'):
            logger.info("Führe Backtest mit Standardparametern durch")
            backtest_results = self.run_backtest(
                strategy_params={},  # Leeres Dictionary = Standardparameter
                symbol=symbol,
                timeframe=timeframe,
                start_date=start_date,
                end_date=end_date
            )
            
            results["backtest_results"] = backtest_results
        
        # 4. Bericht generieren
        if results.get('backtest_results'):
            logger.info("Generiere Abschlussbericht...")
            report_files = self.generate_report(
                output_dir=output_dir,
                filename_prefix=f"{symbol}_{timeframe}"
            )
            
            results["report_files"] = report_files
        
        # Gesamtdauer berechnen
        results["duration"] = time.time() - start_time
        
        logger.info(f"Vollständige Analyse abgeschlossen in {results['duration']:.2f} Sekunden")
        
        return results
    
    class MockStrategy:
        """
        Eine Mock-Strategie für Tests und Entwicklung.
        
        Diese Klasse implementiert eine einfache, deterministische Handelsstrategie
        für Testzwecke, um die Funktionalität des Backtesting-Systems zu validieren,
        ohne eine vollständige Strategie implementieren zu müssen.
        """
        
        def __init__(self, config: Dict = None):
            """
            Initialisiert die MockStrategy.
            
            Args:
                config: Konfigurationsparameter (optional)
            """
            self.config = config or {}
            self.name = "MockStrategy"
            
            # Simple Konfiguration für das generierte Signal
            self.signal_pattern = self.config.get('signal_pattern', [0, 0, 1, 0, -1, 0, 0])  # 0=Hold, 1=Buy, -1=Sell
            self.pattern_index = 0
            
            # Basiswerte für Stop-Loss und Take-Profit
            self.stop_loss_pct = self.config.get('stop_loss_pct', 0.02)  # 2%
            self.take_profit_pct = self.config.get('take_profit_pct', 0.05)  # 5%
        
        def generate_signal(self, data: pd.DataFrame) -> Dict:
            """
            Generiert ein Handelssignal basierend auf dem vordefinierten Muster.
            
            Args:
                data: Ein Pandas DataFrame mit OHLCV-Daten
                
            Returns:
                Ein Signal-Dictionary mit Handelsanweisungen
            """
            if data.empty:
                return {"action": "hold", "details": {"reason": "Keine Daten vorhanden"}}
            
            # Aktuelles Signal aus dem Muster holen
            signal = self.signal_pattern[self.pattern_index]
            self.pattern_index = (self.pattern_index + 1) % len(self.signal_pattern)
            
            current_price = data['close'].iloc[-1]
            
            if signal == 1:  # Buy
                return {
                    "action": "buy",
                    "details": {
                        "reason": "Mock Buy Signal",
                        "pattern": "bullish_pattern",
                        "strength": 0.8,
                        "stop_loss": current_price * (1 - self.stop_loss_pct),
                        "take_profit": current_price * (1 + self.take_profit_pct),
                        "volume_threshold": self.config.get('VOLUME_THRESHOLD', 100000),
                        "use_key_levels": self.config.get('USE_KEY_LEVELS', True),
                        "use_pattern_recognition": self.config.get('USE_PATTERN_RECOGNITION', True),
                        "use_order_flow": self.config.get('USE_ORDER_FLOW', True),
                        "use_liquidity_sweep": self.config.get('USE_LIQUIDITY_SWEEP', True)
                    }
                }
            elif signal == -1:  # Sell
                return {
                    "action": "sell",
                    "details": {
                        "reason": "Mock Sell Signal",
                        "pattern": "bearish_pattern",
                        "strength": 0.7,
                        "stop_loss": current_price * (1 + self.stop_loss_pct),
                        "take_profit": current_price * (1 - self.take_profit_pct),
                        "volume_threshold": self.config.get('VOLUME_THRESHOLD', 100000),
                        "use_key_levels": self.config.get('USE_KEY_LEVELS', True),
                        "use_pattern_recognition": self.config.get('USE_PATTERN_RECOGNITION', True),
                        "use_order_flow": self.config.get('USE_ORDER_FLOW', True),
                        "use_liquidity_sweep": self.config.get('USE_LIQUIDITY_SWEEP', True)
                    }
                }
            else:  # Hold
                return {
                    "action": "hold",
                    "details": {
                        "reason": "Mock Hold Signal",
                        "strength": 0.3
                    }
                }
        
        def calculate_stop_loss(self, data: pd.DataFrame, signal: Dict) -> float:
            """
            Berechnet einen Stop-Loss-Level für das gegebene Signal.
            
            Args:
                data: Ein Pandas DataFrame mit OHLCV-Daten
                signal: Das Handelssignal
                
            Returns:
                Der Stop-Loss-Preis
            """
            if 'stop_loss' in signal:
                return signal['stop_loss']
            
            current_price = data['close'].iloc[-1]
            
            if signal['action'] == 'buy':
                return current_price * (1 - self.stop_loss_pct)
            elif signal['action'] == 'sell':
                return current_price * (1 + self.stop_loss_pct)
            else:
                return 0.0
        
        def calculate_take_profit(self, data: pd.DataFrame, signal: Dict) -> float:
            """
            Berechnet einen Take-Profit-Level für das gegebene Signal.
            
            Args:
                data: Ein Pandas DataFrame mit OHLCV-Daten
                signal: Das Handelssignal
                
            Returns:
                Der Take-Profit-Preis
            """
            if 'take_profit' in signal:
                return signal['take_profit']
            
            current_price = data['close'].iloc[-1]
            
            if signal['action'] == 'buy':
                return current_price * (1 + self.take_profit_pct)
            elif signal['action'] == 'sell':
                return current_price * (1 - self.take_profit_pct)
            else:
                return 0.0
    
    def visualize_filter_study(self, study_results: Dict = None, save_path: str = None, show_plot: bool = True) -> None:
        """
        Visualisiert die Ergebnisse der Filter-Aktivierungsstudie.
        
        Args:
            study_results: Ergebnisse der Filter-Aktivierungsstudie (optional, verwendet gespeicherte Ergebnisse, wenn None)
            save_path: Pfad zum Speichern der Visualisierung (optional)
            show_plot: Ob der Plot direkt angezeigt werden soll
        """
        if study_results is None:
            study_results = self.filter_study_results
            
        if not study_results or not study_results.get('results'):
            logger.warning("Keine Studienergebnisse zum Visualisieren vorhanden")
            return
        
        # Ergebnisse in DataFrame konvertieren
        df = pd.DataFrame(study_results['results'])
        
        # Mehrere Plots erstellen
        fig, axes = plt.subplots(2, 2, figsize=(20, 16))
        fig.suptitle('Smart Money Strategy Filter Activation Study', fontsize=16)
        
        # 1. Profit/Loss nach Filter-Schritt und Volumen-Schwelle
        ax = axes[0, 0]
        pivot_profit = df.pivot_table(
            values='profit_loss', 
            index='volume_threshold', 
            columns='step',
            aggfunc='mean'
        )
        
        pivot_profit.plot(kind='bar', ax=ax, colormap='viridis')
        ax.set_xlabel('Volume Threshold')
        ax.set_ylabel('Profit/Loss ($)')
        ax.set_title('Profit/Loss by Filter Step and Volume Threshold')
        plt.xticks(rotation=45, ha='right')
        ax.grid(True, alpha=0.3)
        ax.legend(title='Filter Steps')
        
        # 2. Win Rate nach Filter-Schritt
        ax = axes[0, 1]
        win_rate_by_step = df.groupby('step')['win_rate'].mean().sort_values(ascending=False)
        
        win_rate_by_step.plot(kind='bar', ax=ax, color='skyblue')
        ax.set_xlabel('Filter Steps')
        ax.set_ylabel('Average Win Rate')
        ax.set_title('Win Rate by Filter Step')
        ax.set_ylim(0, 1.0)  # 0-100%
        plt.xticks(rotation=45, ha='right')
        ax.grid(True, alpha=0.3)
        
        # 3. Trades Anzahl nach Filter-Schritt und Volumen-Schwelle
        ax = axes[1, 0]
        pivot_trades = df.pivot_table(
            values='trades', 
            index='volume_threshold', 
            columns='step',
            aggfunc='mean'
        )
        
        pivot_trades.plot(kind='bar', ax=ax, colormap='plasma')
        ax.set_xlabel('Volume Threshold')
        ax.set_ylabel('Number of Trades')
        ax.set_title('Trade Frequency by Filter Step and Volume Threshold')
        plt.xticks(rotation=45, ha='right')
        ax.grid(True, alpha=0.3)
        ax.legend(title='Filter Steps')
        
        # 4. Sharpe Ratio und Max Drawdown nach Filter-Schritt
        ax = axes[1, 1]
        
        # Erstelle zwei Achsen
        ax2 = ax.twinx()
        
        # Sharpe Ratio
        sharpe_by_step = df.groupby('step')['sharpe_ratio'].mean()
        sharpe_by_step.plot(kind='bar', ax=ax, color='forestgreen', alpha=0.7, position=1, width=0.4)
        ax.set_xlabel('Filter Steps')
        ax.set_ylabel('Average Sharpe Ratio', color='forestgreen')
        ax.tick_params(axis='y', colors='forestgreen')
        
        # Max Drawdown
        drawdown_by_step = df.groupby('step')['max_drawdown'].mean()
        drawdown_by_step.plot(kind='bar', ax=ax2, color='crimson', alpha=0.7, position=0, width=0.4)
        ax2.set_ylabel('Average Max Drawdown', color='crimson')
        ax2.tick_params(axis='y', colors='crimson')
        
        ax.set_title('Risk/Return Metrics by Filter Step')
        plt.xticks(rotation=45, ha='right')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        
        # Speichern, falls erforderlich
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Filter-Studie-Visualisierung gespeichert: {save_path}")
        
        # Anzeigen, falls erforderlich
        if show_plot:
            plt.show()
        else:
            plt.close()
