"""
Modul für die Berichterstattung und das Speichern von Analyseergebnissen.
"""

import os
import json
import logging
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Union, Any

logger = logging.getLogger(__name__)

def save_reports(results: Dict, 
                trade_stats: Dict, 
                underwater_stats: Dict, 
                monthly_returns: pd.DataFrame, 
                performance_metrics: pd.DataFrame,
                output_dir: str, 
                formats: List[str]):
    """
    Speichert die Analyseberichte in verschiedenen Formaten.
    
    Args:
        results: Dictionary mit Backtest-Ergebnissen
        trade_stats: Dictionary mit Trade-Statistiken
        underwater_stats: Dictionary mit Drawdown-Statistiken
        monthly_returns: DataFrame mit monatlicher Performance
        performance_metrics: DataFrame mit Performance-Metriken
        output_dir: Ausgabeverzeichnis
        formats: Liste mit Ausgabeformaten
    """
    # Erstelle Ausgabeverzeichnis
    os.makedirs(output_dir, exist_ok=True)
    
    # Basisname für Dateien
    base_name = f"{results.get('symbol', 'unknown')}_{results.get('strategy', 'unknown')}"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_base = f"{output_dir}/{base_name}_{timestamp}"
    
    # CSV-Format
    if 'csv' in formats or 'all' in formats:
        # Performance-Tabelle
        performance_metrics.to_csv(f"{file_base}_performance.csv")
        
        # Trades
        trades_df = pd.DataFrame(results.get('trades', []))
        if not trades_df.empty:
            trades_df.to_csv(f"{file_base}_trades.csv", index=False)
        
        # Monatliche Renditen
        if monthly_returns is not None and not monthly_returns.empty:
            monthly_returns.to_csv(f"{file_base}_monthly.csv", index=False)
        
        # Drawdown-Perioden
        if 'underwater_periods_details' in underwater_stats and underwater_stats['underwater_periods_details']:
            pd.DataFrame(underwater_stats['underwater_periods_details']).to_csv(
                f"{file_base}_drawdowns.csv", index=False)
        
        logger.info(f"CSV-Berichte gespeichert in: {output_dir}")
    
    # JSON-Format
    if 'json' in formats or 'all' in formats:
        # Performance-Metriken
        with open(f"{file_base}_metrics.json", 'w') as f:
            json.dump({
                'performance': performance_metrics.to_dict(),
                'trade_stats': trade_stats,
                'underwater_stats': underwater_stats
            }, f, indent=2, default=str)
        
        logger.info(f"JSON-Berichte gespeichert in: {output_dir}")
    
    # TXT-Format
    if 'txt' in formats or 'all' in formats:
        with open(f"{file_base}_report.txt", 'w') as f:
            f.write(f"BACKTEST REPORT: {results.get('symbol', 'unknown')} - {results.get('strategy', 'unknown')}\n")
            f.write(f"Zeitraum: {results.get('start_date', 'unknown')} bis {results.get('end_date', 'unknown')}\n")
            f.write("="*80 + "\n\n")
            
            # Performance-Metriken
            f.write("PERFORMANCE METRIKEN:\n")
            f.write("-"*80 + "\n")
            f.write(performance_metrics.to_string() + "\n\n")
            
            # Trade-Statistiken
            f.write("TRADE DETAILS:\n")
            f.write("-"*80 + "\n")
            f.write(f"Anzahl Trades: {trade_stats.get('total_trades', 0)}\n")
            f.write(f"Gewinnende Trades: {trade_stats.get('winning_trades', 0)}\n")
            f.write(f"Verlierende Trades: {trade_stats.get('losing_trades', 0)}\n")
            f.write(f"Win Rate: {trade_stats.get('win_rate', 0):.2f}%\n")
            f.write(f"Profit Factor: {trade_stats.get('profit_factor', 0):.2f}\n")
            f.write(f"Durchschn. Gewinn: ${trade_stats.get('avg_profit', 0):.2f}\n")
            f.write(f"Durchschn. Verlust: ${trade_stats.get('avg_loss', 0):.2f}\n")
            f.write(f"Max Consecutive Wins: {trade_stats.get('max_consecutive_wins', 0)}\n")
            f.write(f"Max Consecutive Losses: {trade_stats.get('max_consecutive_losses', 0)}\n\n")
            
            # Drawdown-Statistiken
            f.write("DRAWDOWN DETAILS:\n")
            f.write("-"*80 + "\n")
            f.write(f"Maximaler Drawdown: {underwater_stats.get('max_drawdown', 0):.2f}%\n")
            f.write(f"Durchschnittlicher Drawdown: {underwater_stats.get('avg_drawdown', 0):.2f}%\n")
            f.write(f"Drawdown Standardabweichung: {underwater_stats.get('drawdown_std', 0):.2f}%\n")
            f.write(f"Anzahl Underwater Perioden: {underwater_stats.get('underwater_periods', 0)}\n\n")
            
            # TOP 5 Drawdown-Perioden
            if 'underwater_periods_details' in underwater_stats and underwater_stats['underwater_periods_details']:
                f.write("TOP 5 DRAWDOWN PERIODEN:\n")
                f.write("-"*80 + "\n")
                for i, period in enumerate(underwater_stats['underwater_periods_details'][:5]):
                    f.write(f"{i+1}. Von {period['start_date']} bis {period['end_date']} " + 
                           f"({period['duration_days']} Tage): {period['max_drawdown']:.2f}% " + 
                           f"(Maximum am {period['max_drawdown_date']})\n")
                f.write("\n")
            
            # Monatliche Performance
            if monthly_returns is not None and not monthly_returns.empty:
                f.write("MONATLICHE PERFORMANCE:\n")
                f.write("-"*80 + "\n")
                monthly_df = monthly_returns.sort_values(['year', 'month'])
                for _, row in monthly_df.iterrows():
                    f.write(f"{row['year']}-{row['month_name']}: {row['return']:.2f}%\n")
            
        logger.info(f"TXT-Bericht gespeichert in: {file_base}_report.txt")
    
    # HTML-Format
    if 'html' in formats or 'all' in formats:
        # Erstelle HTML-Report
        html_content = f"""
        <!DOCTYPE html>
        <html lang="de">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Backtest Report - {results.get('symbol', 'unknown')} - {results.get('strategy', 'unknown')}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1, h2 {{ color: #333; }}
                table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
                th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background-color: #f2f2f2; }}
                tr:hover {{ background-color: #f5f5f5; }}
                .positive {{ color: green; }}
                .negative {{ color: red; }}
                .section {{ margin-bottom: 30px; }}
            </style>
        </head>
        <body>
            <h1>Backtest Report: {results.get('symbol', 'unknown')} - {results.get('strategy', 'unknown')}</h1>
            <p>Zeitraum: {results.get('start_date', 'unknown')} bis {results.get('end_date', 'unknown')}</p>
            
            <div class="section">
                <h2>Performance Metriken</h2>
                <table>
                    <tr><th>Metrik</th><th>Wert</th></tr>
        """
        
        # Füge Performance-Metriken hinzu
        for index, row in performance_metrics.iterrows():
            html_content += f"<tr><td>{index}</td><td>{row['Wert']}</td></tr>\n"
        
        html_content += """
                </table>
            </div>
            
            <div class="section">
                <h2>Trade Statistiken</h2>
                <table>
                    <tr><th>Metrik</th><th>Wert</th></tr>
        """
        
        # Füge Trade-Statistiken hinzu
        trade_stats_display = {
            'Anzahl Trades': trade_stats.get('total_trades', 0),
            'Gewinnende Trades': trade_stats.get('winning_trades', 0),
            'Verlierende Trades': trade_stats.get('losing_trades', 0),
            'Win Rate': f"{trade_stats.get('win_rate', 0):.2f}%",
            'Profit Factor': f"{trade_stats.get('profit_factor', 0):.2f}",
            'Durchschn. Gewinn': f"${trade_stats.get('avg_profit', 0):.2f}",
            'Durchschn. Verlust': f"${trade_stats.get('avg_loss', 0):.2f}",
            'Max Consecutive Wins': trade_stats.get('max_consecutive_wins', 0),
            'Max Consecutive Losses': trade_stats.get('max_consecutive_losses', 0)
        }
        
        for key, value in trade_stats_display.items():
            html_content += f"<tr><td>{key}</td><td>{value}</td></tr>\n"
        
        html_content += """
                </table>
            </div>
        """
        
        # Monatliche Performance hinzufügen, wenn verfügbar
        if monthly_returns is not None and not monthly_returns.empty:
            html_content += """
            <div class="section">
                <h2>Monatliche Performance</h2>
                <table>
                    <tr><th>Monat</th><th>Rendite (%)</th></tr>
            """
            
            monthly_df = monthly_returns.sort_values(['year', 'month'])
            for _, row in monthly_df.iterrows():
                color_class = "positive" if row['return'] >= 0 else "negative"
                html_content += f"<tr><td>{row['year']}-{row['month_name']}</td><td class='{color_class}'>{row['return']:.2f}%</td></tr>\n"
            
            html_content += """
                </table>
            </div>
            """
        
        # Drawdown-Perioden hinzufügen, wenn verfügbar
        if 'underwater_periods_details' in underwater_stats and underwater_stats['underwater_periods_details']:
            html_content += """
            <div class="section">
                <h2>Top 5 Drawdown Perioden</h2>
                <table>
                    <tr><th>#</th><th>Von</th><th>Bis</th><th>Dauer (Tage)</th><th>Max Drawdown</th><th>Datum Max DD</th></tr>
            """
            
            for i, period in enumerate(underwater_stats['underwater_periods_details'][:5]):
                html_content += f"<tr><td>{i+1}</td><td>{period['start_date']}</td><td>{period['end_date']}</td>" + \
                               f"<td>{period['duration_days']}</td><td class='negative'>{period['max_drawdown']:.2f}%</td>" + \
                               f"<td>{period['max_drawdown_date']}</td></tr>\n"
            
            html_content += """
                </table>
            </div>
            """
        
        # HTML-Dokument abschließen
        html_content += """
            <div class="footer">
                <p>Erstellt am """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """ mit Crypto Trading Bot V2</p>
            </div>
        </body>
        </html>
        """
        
        # HTML-Datei speichern
        with open(f"{file_base}_report.html", 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"HTML-Bericht gespeichert in: {file_base}_report.html")
    
    logger.info(f"Alle Berichte wurden erfolgreich gespeichert in: {output_dir}")
    
    return file_base

def print_summary(results: Dict, trade_stats: Dict, underwater_stats: Dict, performance_metrics: pd.DataFrame):
    """
    Gibt eine Zusammenfassung der Backtestergebnisse auf der Konsole aus.
    
    Args:
        results: Dictionary mit Backtest-Ergebnissen
        trade_stats: Dictionary mit Trade-Statistiken
        underwater_stats: Dictionary mit Drawdown-Statistiken
        performance_metrics: DataFrame mit Performance-Metriken
    """
    print("\n" + "="*80)
    print(f"BACKTEST SUMMARY: {results.get('symbol', 'unknown')} - {results.get('strategy', 'unknown')}")
    print("="*80)
    
    # Allgemeine Informationen
    print(f"\nZeitraum: {results.get('start_date', 'unknown')} bis {results.get('end_date', 'unknown')}")
    print(f"Anfangsguthaben: ${results.get('initial_balance', 0):.2f}")
    print(f"Endguthaben: ${results.get('final_balance', 0):.2f}")
    
    # Rendite
    metrics = results.get('metrics', {})
    print(f"\nGesamtrendite: {metrics.get('return', 0):.2f}%")
    print(f"Annualisierte Rendite: {metrics.get('annualized_return', 0):.2f}%")
    print(f"Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.2f}")
    print(f"Calmar Ratio: {metrics.get('calmar_ratio', 0):.2f}")
    print(f"Maximaler Drawdown: {metrics.get('max_drawdown', 0):.2f}%")
    
    # Trade-Statistiken
    print(f"\nAnzahl Trades: {trade_stats.get('total_trades', 0)}")
    print(f"Gewinnende Trades: {trade_stats.get('winning_trades', 0)}")
    print(f"Verlierende Trades: {trade_stats.get('losing_trades', 0)}")
    print(f"Win Rate: {trade_stats.get('win_rate', 0):.2f}%")
    print(f"Profit Factor: {trade_stats.get('profit_factor', 0):.2f}")
    print(f"Durchschn. Gewinn: ${trade_stats.get('avg_profit', 0):.2f}")
    print(f"Durchschn. Verlust: ${trade_stats.get('avg_loss', 0):.2f}")
    
    print("="*80)
