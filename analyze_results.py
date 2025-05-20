#!/usr/bin/env python
"""
Analyse-Tool für Backtest-Ergebnisse des Crypto Trading Bot V2.

Dieses Skript analysiert und visualisiert die Ergebnisse von Backtests,
generiert umfassende Berichte und Performance-Metriken.
"""

import os
import argparse
import logging
from dotenv import load_dotenv

# Lokale Module importieren
from analysis.data_loader import load_backtest_results
from analysis.visualizations import (
    create_equity_curve_plot,
    create_drawdown_plot,
    create_monthly_breakdown_plot,
    create_trade_analysis_plots
)
from analysis.statistics import (
    calculate_drawdown_statistics,
    calculate_monthly_returns,
    calculate_trade_statistics,
    create_performance_metrics
)
from analysis.reporting import (
    save_reports,
    print_summary
)

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
    parser = argparse.ArgumentParser(description="Crypto Trading Bot V2 - Ergebnisanalyse")
    
    # Eingabe-Parameter
    parser.add_argument('--result-file', type=str, required=True,
                        help='Pfad zur JSON-Datei mit Backtest-Ergebnissen')
    
    # Ausgabe-Parameter
    parser.add_argument('--output-dir', type=str, default='analysis_results',
                        help='Verzeichnis für Analyseberichte')
    parser.add_argument('--report-format', type=str, default='all',
                        choices=['all', 'json', 'csv', 'txt', 'html'],
                        help='Format für den Analysebericht')
    
    # Visualisierungs-Parameter
    parser.add_argument('--plot', action='store_true',
                        help='Grafiken anzeigen')
    parser.add_argument('--save-plots', action='store_true',
                        help='Grafiken speichern')
    
    # Analyse-Parameter
    parser.add_argument('--monthly-breakdown', action='store_true',
                        help='Monatliche Performance-Analyse')
    parser.add_argument('--drawdown-analysis', action='store_true',
                        help='Detaillierte Drawdown-Analyse')
    parser.add_argument('--trade-analysis', action='store_true',
                        help='Detaillierte Trade-Analyse')
    
    return parser.parse_args()

def main():
    """Hauptfunktion für die Analyse von Backtest-Ergebnissen."""
    args = parse_args()
    
    try:
        # Backtest-Ergebnisse laden
        results = load_backtest_results(args.result_file)
        
        # Erstelle Ausgabeverzeichnis
        os.makedirs(args.output_dir, exist_ok=True)
        
        # Berechne Statistiken
        underwater_stats = calculate_drawdown_statistics(results)
        monthly_returns = calculate_monthly_returns(results)
        trade_stats, df_trades = calculate_trade_statistics(results)
        
        # Erstelle Performance-Tabelle
        performance_metrics = create_performance_metrics(results, trade_stats, underwater_stats)
        
        # Ausgabe der Zusammenfassung auf der Konsole
        print_summary(results, trade_stats, underwater_stats, performance_metrics)
        
        # Speichere Berichte
        file_base = save_reports(
            results=results,
            trade_stats=trade_stats,
            underwater_stats=underwater_stats,
            monthly_returns=monthly_returns,
            performance_metrics=performance_metrics,
            output_dir=args.output_dir,
            formats=args.report_format.split(',') if ',' in args.report_format else [args.report_format]
        )
        
        # Erstelle und zeige/speichere Grafiken
        if args.plot or args.save_plots:
            # Equity-Kurve
            equity_plot_path = f"{file_base}_equity.png" if args.save_plots else None
            create_equity_curve_plot(results, save_path=equity_plot_path)
            
            # Drawdown-Analyse
            if args.drawdown_analysis:
                drawdown_plot_path = f"{file_base}_drawdown.png" if args.save_plots else None
                create_drawdown_plot(results, save_path=drawdown_plot_path)
            
            # Monatliche Aufschlüsselung
            if args.monthly_breakdown and monthly_returns is not None and not monthly_returns.empty:
                monthly_plot_path = f"{file_base}_monthly.png" if args.save_plots else None
                create_monthly_breakdown_plot(monthly_returns, save_path=monthly_plot_path)
            
            # Trade-Analyse
            if args.trade_analysis and not df_trades.empty:
                trade_plot_path = f"{file_base}_trades.png" if args.save_plots else None
                create_trade_analysis_plots(df_trades, save_path=trade_plot_path)
        
        logger.info(f"Analyse erfolgreich abgeschlossen. Berichte wurden gespeichert in: {args.output_dir}")
        print(f"\nAnalyse erfolgreich abgeschlossen. Berichte wurden gespeichert in: {args.output_dir}")
        
        return 0
        
    except Exception as e:
        logger.exception(f"Fehler bei der Analyse: {e}")
        print(f"Fehler bei der Analyse: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
