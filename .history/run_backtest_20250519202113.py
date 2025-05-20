#!/usr/bin/env python
"""
Backtest-Script für den Crypto Trading Bot V2 mit Smart Money Strategie.

Dieses Skript führt einen Backtest für die Smart Money Handelsstrategie durch und 
ermöglicht die Evaluierung der Strategie mit verschiedenen Filter-Kombinationen.
"""

import os
import argparse
import logging
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv

# Lokale Module importieren
from data.data_handler import DataHandler
from backtesting.backtest_engine import BacktestEngine
from visualization.charts import plot_equity_curve, plot_performance_metrics
from exchange.bybit_api import BybitAPI
from config.config import config
from utils.backtester import SmartMoneyBacktester
from strategies.smart_money import SmartMoneyStrategy

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

def parse_args():
    """Verarbeitet Kommandozeilenargumente."""
    parser = argparse.ArgumentParser(description="Crypto Trading Bot V2 - Smart Money Strategy Backtest")
    
    # Allgemeine Parameter
    parser.add_argument('--symbol', type=str, default='BTCUSDT',
                        help='Trading-Symbol (z.B. BTCUSDT)')
    parser.add_argument('--timeframe', type=str, default='1h',
                        help='Zeitrahmen (z.B. 1h, 4h, 1d)')
    parser.add_argument('--start-date', type=str, 
                        default=(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
                        help='Startdatum (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=str, default=None,
                        help='Enddatum (YYYY-MM-DD), Standard: aktuelles Datum')
    parser.add_argument('--initial-balance', type=float, default=10000.0,
                        help='Anfangsguthaben in USD')
    
    # Smart Money Strategie Parameter
    parser.add_argument('--volume-threshold', type=int, default=100000,
                        help='Volumen-Schwellenwert für die Smart Money Strategie')
    parser.add_argument('--liquidity-factor', type=float, default=1.0,
                        help='Liquiditätsfaktor für die Smart Money Strategie')
    parser.add_argument('--use-volume-filter', action='store_true', default=True,
                        help='Volumen-Filter verwenden')
    parser.add_argument('--use-key-levels', action='store_true', default=True,
                        help='Key-Levels-Filter verwenden')
    parser.add_argument('--use-pattern', action='store_true', default=True,
                        help='Pattern-Recognition-Filter verwenden')
    parser.add_argument('--use-order-flow', action='store_true', default=True,
                        help='Order-Flow-Filter verwenden')
    parser.add_argument('--use-liquidity-sweep', action='store_true', default=True,
                        help='Liquidity-Sweep-Filter verwenden')
    
    # Analysemodus
    parser.add_argument('--mode', type=str, default='basic',
                        choices=['basic', 'parameter-sweep', 'filter-study', 'complete'],
                        help='Backtest-Modus: basic=einfacher Backtest, parameter-sweep=Parameteroptimierung, '
                             'filter-study=Filter-Aktivierungsstudie, complete=Komplette Analyse')
    
    # Ausgabe-Parameter
    parser.add_argument('--output-dir', type=str, default='backtest_results',
                        help='Verzeichnis für Backtest-Ergebnisse')
    parser.add_argument('--plot', action='store_true',
                        help='Visualisierungen anzeigen')
    
    return parser.parse_args()

def run_backtest(args):
    """Führt den Backtest mit den angegebenen Parametern durch."""
    logger.info(f"Starte Smart Money Strategy Backtest für {args.symbol} im {args.timeframe} Timeframe")
    
    try:
        # Exchange API initialisieren (für historische Daten)
        exchange_api = None
        if config.get('USE_EXCHANGE_API', False):
            exchange_api = BybitAPI(
                api_key=config.get('API_KEY', ''),
                api_secret=config.get('API_SECRET', ''),
                testnet=config.get('USE_TESTNET', True)
            )
        
        # DataHandler initialisieren
        data_handler = DataHandler(exchange_api)
        
        # Smart Money Strategie Parameter
        strategy_params = {
            'VOLUME_THRESHOLD': args.volume_threshold,
            'LIQUIDITY_FACTOR': args.liquidity_factor,
            'USE_VOLUME_FILTER': args.use_volume_filter,
            'USE_KEY_LEVELS': args.use_key_levels,
            'USE_PATTERN_RECOGNITION': args.use_pattern,
            'USE_ORDER_FLOW': args.use_order_flow,
            'USE_LIQUIDITY_SWEEP': args.use_liquidity_sweep,
        }
        
        # Basis-Konfiguration aus config ergänzen
        full_config = {**config, **strategy_params}
        
        # Erstelle Ausgabeverzeichnis
        os.makedirs(args.output_dir, exist_ok=True)
        
        # Je nach Modus unterschiedliche Backtests durchführen
        if args.mode == 'basic':
            # Strategie erstellen
            strategy = SmartMoneyStrategy(full_config)
            
            # BacktestEngine initialisieren
            backtest_engine = BacktestEngine(
                data_handler=data_handler,
                strategy=strategy,
                initial_balance=args.initial_balance,
                commission=float(os.environ.get('COMMISSION', 0.001)),
                slippage=float(os.environ.get('SLIPPAGE', 0.0005))
            )
            
            # Führe Backtest durch
            results = backtest_engine.run(
                symbol=args.symbol,
                timeframe=args.timeframe,
                start_date=args.start_date,
                end_date=args.end_date
            )
            
            if not results.get('success', False):
                logger.error(f"Backtest fehlgeschlagen: {results.get('error', 'Unbekannter Fehler')}")
                return
            
            # Speichere Ergebnisse
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results_file = f"{args.output_dir}/{args.symbol}_{args.timeframe}_smart_money_{timestamp}.json"
            backtest_engine.save_results(results_file)
            
            # Erstelle Equity-Kurve
            if args.plot:
                backtest_engine.plot_equity_curve(
                    save_path=f"{args.output_dir}/{args.symbol}_{args.timeframe}_smart_money_{timestamp}_equity.png"
                )
                
                # Erstelle Performance-Metriken-Chart
                create_performance_metrics_chart(
                    results['metrics'],
                    title=f"{args.symbol} {args.timeframe} - Smart Money Performance",
                    save_path=f"{args.output_dir}/{args.symbol}_{args.timeframe}_smart_money_{timestamp}_metrics.png"
                )
            
            # Zeige Zusammenfassung
            metrics = results['metrics']
            
            print("\n" + "="*60)
            print(f"Backtest-Ergebnisse für {args.symbol} ({args.timeframe}) mit Smart Money Strategie")
            print("="*60)
            print(f"Zeitraum: {results['start_date']} bis {results['end_date']}")
            print(f"Anfangsguthaben: ${args.initial_balance:.2f}")
            print(f"Endguthaben: ${results['final_balance']:.2f}")
            print(f"Gesamtrendite: {metrics['return']:.2%}")
            print(f"Annualisierte Rendite: {metrics['annualized_return']:.2%}")
            print(f"Maximaler Drawdown: {metrics['max_drawdown']:.2%}")
            print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
            print(f"Profit Factor: {metrics['profit_factor']:.2f}")
            print(f"Trades: {metrics['total_trades']}")
            print(f"Gewinn-Rate: {metrics['win_rate']:.2%}")
            print(f"Durchschn. Gewinn: ${metrics['avg_win']:.2f}")
            print(f"Durchschn. Verlust: ${metrics['avg_loss']:.2f}")
            print(f"Ergebnisse gespeichert in: {results_file}")
            print("="*60)
        
        elif args.mode == 'parameter-sweep':
            # SmartMoneyBacktester initialisieren
            backtester = SmartMoneyBacktester(
                data_handler=data_handler,
                config=config,
                initial_balance=args.initial_balance,
                commission=float(os.environ.get('COMMISSION', 0.001)),
                slippage=float(os.environ.get('SLIPPAGE', 0.0005))
            )
            
            # Parameter-Sweep durchführen
            logger.info("Starte Parameter-Sweep für Smart Money Strategie...")
            
            # Parameter-Grid definieren
            param_grid = {
                'VOLUME_THRESHOLD': [10000, 50000, 100000, 250000, 500000, 1000000],
                'LIQUIDITY_FACTOR': [0.8, 1.0, 1.2, 1.5],
                'USE_VOLUME_FILTER': [True],  # Immer aktiviert
                'USE_KEY_LEVELS': [False, True],
                'USE_PATTERN_RECOGNITION': [False, True],
                'USE_ORDER_FLOW': [False, True],
                'USE_LIQUIDITY_SWEEP': [False, True]
            }
            
            # Parameter-Sweep durchführen
            optimization_results = backtester.parameter_sweep(
                symbol=args.symbol,
                timeframe=args.timeframe,
                start_date=args.start_date,
                end_date=args.end_date,
                param_grid=param_grid,
                parallel=True,
                max_workers=4
            )
            
            # Visualisierung erstellen
            if args.plot:
                backtester.visualize_optimization_results(
                    save_path=f"{args.output_dir}/{args.symbol}_{args.timeframe}_parameter_sweep.png",
                    show_plot=True
                )
            
            # Beste Parameter ausgeben
            if optimization_results.get('best_params'):
                print("\n" + "="*60)
                print(f"Parameter-Sweep Ergebnisse für {args.symbol} ({args.timeframe})")
                print("="*60)
                print("Beste Parameter:")
                for param, value in optimization_results['best_params'].items():
                    print(f"  {param}: {value}")
                
                print("\nBeste Metriken:")
                for metric, value in optimization_results['best_metrics'].items():
                    if metric in ['return', 'win_rate', 'max_drawdown']:
                        print(f"  {metric}: {value:.2%}")
                    else:
                        print(f"  {metric}: {value:.2f}")
                
                print(f"\nInsgesamt getestete Kombinationen: {optimization_results['combinations_tested']}")
                print(f"Gültige Ergebnisse: {optimization_results['valid_results']}")
                print(f"Dauer: {optimization_results['duration']:.2f} Sekunden")
                print("="*60)
            else:
                print("\nKeine gültigen Ergebnisse gefunden!")
        
        elif args.mode == 'filter-study':
            # SmartMoneyBacktester initialisieren
            backtester = SmartMoneyBacktester(
                data_handler=data_handler,
                config=config,
                initial_balance=args.initial_balance,
                commission=float(os.environ.get('COMMISSION', 0.001)),
                slippage=float(os.environ.get('SLIPPAGE', 0.0005))
            )
            
            # Filter-Aktivierungsstudie durchführen
            logger.info("Starte Filter-Aktivierungsstudie für Smart Money Strategie...")
            
            # Volumen-Schwellen definieren
            volume_thresholds = [10000, 50000, 100000, 250000, 500000, 1000000]
            
            # Filter-Aktivierungsstudie durchführen
            study_results = backtester.run_filter_activation_study(
                symbol=args.symbol,
                timeframe=args.timeframe,
                start_date=args.start_date,
                end_date=args.end_date,
                volume_thresholds=volume_thresholds
            )
            
            # Visualisierung erstellen
            if args.plot:
                backtester.visualize_filter_study(
                    study_results=study_results,
                    save_path=f"{args.output_dir}/{args.symbol}_{args.timeframe}_filter_study.png",
                    show_plot=True
                )
            
            # Ergebnisse in Tabelle umwandeln und ausgeben
            if study_results.get('results'):
                df = pd.DataFrame(study_results['results'])
                
                # Nach Profit/Loss sortieren
                sorted_df = df.sort_values('profit_loss', ascending=False)
                
                # Ergebnisse ausgeben
                print("\n" + "="*100)
                print(f"Filter-Aktivierungsstudie Ergebnisse für {args.symbol} ({args.timeframe})")
                print("="*100)
                print("Top 10 Filter-Kombinationen:")
                
                # Tabelle mit Ergebnissen
                table_data = sorted_df[['step', 'volume_threshold', 'profit_loss', 'trades', 'win_rate']].head(10)
                table_data['win_rate'] = table_data['win_rate'].apply(lambda x: f"{x:.2%}")
                table_data['profit_loss'] = table_data['profit_loss'].apply(lambda x: f"${x:.2f}")
                
                print(table_data.to_string(index=False))
                print("="*100)
                
                # Parameter der besten Kombination
                best_result = sorted_df.iloc[0]
                print(f"\nBeste Filter-Kombination: {best_result['step']} mit Volumen-Schwelle {best_result['volume_threshold']}")
                print(f"Profit: ${best_result['profit_loss']:.2f}, Win Rate: {best_result['win_rate']:.2%}, Trades: {best_result['trades']}")
                print("="*60)
            else:
                print("\nKeine gültigen Ergebnisse gefunden!")
        
        elif args.mode == 'complete':
            # SmartMoneyBacktester initialisieren
            backtester = SmartMoneyBacktester(
                data_handler=data_handler,
                config=config,
                initial_balance=args.initial_balance,
                commission=float(os.environ.get('COMMISSION', 0.001)),
                slippage=float(os.environ.get('SLIPPAGE', 0.0005))
            )
            
            # Komplette Analyse durchführen
            logger.info("Starte komplette Analyse für Smart Money Strategie...")
            
            # Komplett-Analyse mit beiden Studien durchführen
            analysis_results = backtester.run_complete_analysis(
                symbol=args.symbol,
                timeframe=args.timeframe,
                start_date=args.start_date,
                end_date=args.end_date,
                output_dir=args.output_dir,
                run_parameter_sweep=True,
                run_filter_study=True,
                show_plots=args.plot
            )
            
            # Zeige Abschlussbericht
            duration = analysis_results['duration']
            print("\n" + "="*60)
            print(f"Smart Money Strategie Komplettanalyse für {args.symbol} ({args.timeframe})")
            print("="*60)
            print(f"Dauer der Analyse: {duration:.2f} Sekunden ({duration/60:.2f} Minuten)")
            
            # Zeige Backtest-Ergebnisse
            if analysis_results.get('backtest_results'):
                metrics = analysis_results['backtest_results']['metrics']
                print("\nBacktest-Ergebnisse:")
                print(f"Gesamtrendite: {metrics['return']:.2%}")
                print(f"Max. Drawdown: {metrics['max_drawdown']:.2%}")
                print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
                print(f"Profit Factor: {metrics['profit_factor']:.2f}")
                print(f"Anzahl Trades: {metrics['total_trades']}")
                print(f"Win Rate: {metrics['win_rate']:.2%}")
            
            # Zeige beste Parameter aus dem Parameter-Sweep
            if analysis_results.get('optimization_results') and analysis_results['optimization_results'].get('best_params'):
                best_params = analysis_results['optimization_results']['best_params']
                print("\nBeste Parameter aus Parameter-Sweep:")
                for param, value in best_params.items():
                    print(f"  {param}: {value}")
            
            # Zeige beste Filter-Kombination aus der Filter-Studie
            if analysis_results.get('filter_study_results') and analysis_results['filter_study_results'].get('results'):
                filter_df = pd.DataFrame(analysis_results['filter_study_results']['results'])
                best_filter = filter_df.sort_values('profit_loss', ascending=False).iloc[0]
                print("\nBeste Filter-Kombination aus Filter-Studie:")
                print(f"  Schritte: {best_filter['step']}")
                print(f"  Volumen-Schwelle: {best_filter['volume_threshold']}")
                print(f"  Profit: ${best_filter['profit_loss']:.2f}")
                print(f"  Win Rate: {best_filter['win_rate']:.2%}")
            
            # Zeige generierte Berichte
            if analysis_results.get('report_files'):
                print("\nGenerierte Berichte:")
                for report_type, report_file in analysis_results['report_files'].items():
                    print(f"  {report_type}: {os.path.basename(report_file)}")
            
            print("="*60)
            print("Analyse abgeschlossen! Detaillierte Ergebnisse sind in den Berichten zu finden.")
        
        logger.info(f"Smart Money Strategy Backtest erfolgreich abgeschlossen")
        
    except Exception as e:
        logger.exception(f"Fehler beim Backtesting: {e}")

if __name__ == "__main__":
    args = parse_args()
    run_backtest(args)
