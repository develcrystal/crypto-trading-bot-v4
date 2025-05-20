"""
Modul für Visualisierungen von Backtest-Ergebnissen.
"""

import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from typing import Dict, Optional

logger = logging.getLogger(__name__)

def create_equity_curve_plot(results: Dict, save_path: Optional[str] = None):
    """
    Erstellt eine Grafik der Equity-Kurve.
    
    Args:
        results: Dictionary mit Backtest-Ergebnissen
        save_path: Pfad zum Speichern der Grafik (optional)
    """
    if not results or 'equity_curve' not in results:
        logger.warning("Keine Daten für Equity-Kurve vorhanden")
        return
    
    # DataFrame für Equity-Kurve erstellen
    df_equity = pd.DataFrame(results['equity_curve'])
    df_equity['timestamp'] = pd.to_datetime(df_equity['timestamp'])
    df_equity.set_index('timestamp', inplace=True)
    
    # Grafik erstellen
    plt.figure(figsize=(12, 8))
    
    # Equity-Kurve
    plt.subplot(2, 1, 1)
    plt.plot(df_equity.index, df_equity['equity'], label='Equity', color='blue')
    plt.plot(df_equity.index, df_equity['balance'], label='Balance', color='green', linestyle='--')
    
    # Trades markieren
    if 'trades' in results:
        for trade in results['trades']:
            exit_time = pd.to_datetime(trade['exit_time']) if isinstance(trade['exit_time'], str) else trade['exit_time']
            exit_price = trade['exit_price']
            
            if trade['net_profit'] > 0:
                color = 'green'
                marker = '^'  # Dreieck nach oben für Gewinne
            else:
                color = 'red'
                marker = 'v'  # Dreieck nach unten für Verluste
                
            plt.scatter(exit_time, exit_price, color=color, marker=marker, s=100, alpha=0.7)
    
    plt.title(f"Equity-Kurve - {results['symbol']} - {results['strategy']}")
    plt.ylabel('Equity ($)')
    plt.grid(True)
    plt.legend()
    
    # X-Achse formatieren
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.gcf().autofmt_xdate()
    
    # Drawdown
    plt.subplot(2, 1, 2)
    equity_values = np.array(df_equity['equity'])
    peak = np.maximum.accumulate(equity_values)
    drawdown = (peak - equity_values) / peak
    
    plt.fill_between(df_equity.index, 0, drawdown * 100, color='red', alpha=0.3)
    plt.title('Drawdown (%)')
    plt.ylabel('Drawdown (%)')
    plt.grid(True)
    
    # X-Achse formatieren
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.gcf().autofmt_xdate()
    
    plt.tight_layout()
    
    # Grafik speichern, wenn Pfad angegeben
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"Equity-Kurve gespeichert: {save_path}")
    
    plt.show()

def create_drawdown_plot(results: Dict, save_path: Optional[str] = None):
    """
    Erstellt eine detaillierte Drawdown-Analyse-Grafik.
    
    Args:
        results: Dictionary mit Backtest-Ergebnissen
        save_path: Pfad zum Speichern der Grafik (optional)
    """
    if not results or 'equity_curve' not in results:
        logger.warning("Keine Daten für Drawdown-Analyse vorhanden")
        return
    
    # DataFrame für Equity-Kurve erstellen
    df_equity = pd.DataFrame(results['equity_curve'])
    df_equity['timestamp'] = pd.to_datetime(df_equity['timestamp'])
    df_equity.set_index('timestamp', inplace=True)
    
    # Berechne Drawdown
    equity_values = np.array(df_equity['equity'])
    peak = np.maximum.accumulate(equity_values)
    drawdown = (peak - equity_values) / peak
    
    # Grafik erstellen
    plt.figure(figsize=(12, 10))
    
    # Drawdown-Verlauf
    plt.subplot(2, 1, 1)
    plt.fill_between(df_equity.index, 0, drawdown * 100, color='red', alpha=0.5)
    plt.title('Drawdown-Verlauf')
    plt.ylabel('Drawdown (%)')
    plt.grid(True)
    
    # X-Achse formatieren
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.gcf().autofmt_xdate()
    
    # Drawdown-Verteilung
    plt.subplot(2, 1, 2)
    plt.hist(drawdown * 100, bins=50, color='red', alpha=0.7)
    plt.title('Drawdown-Verteilung')
    plt.xlabel('Drawdown (%)')
    plt.ylabel('Häufigkeit')
    plt.grid(True)
    
    plt.tight_layout()
    
    # Grafik speichern, wenn Pfad angegeben
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"Drawdown-Analyse gespeichert: {save_path}")
    
    plt.show()

def create_monthly_breakdown_plot(monthly_returns: pd.DataFrame, save_path: Optional[str] = None):
    """
    Erstellt eine Grafik der monatlichen Performance.
    
    Args:
        monthly_returns: DataFrame mit monatlicher Performance
        save_path: Pfad zum Speichern der Grafik (optional)
    """
    if monthly_returns is None or monthly_returns.empty:
        logger.warning("Keine Daten für monatliche Analyse vorhanden")
        return
    
    # Grafik erstellen
    plt.figure(figsize=(12, 6))
    
    # Monatliche Renditen
    colors = ['green' if r >= 0 else 'red' for r in monthly_returns['return']]
    plt.bar(monthly_returns['period'], monthly_returns['return'], color=colors)
    
    plt.title('Monatliche Performance (%)')
    plt.ylabel('Rendite (%)')
    plt.grid(True, axis='y')
    plt.xticks(rotation=45)
    
    # Statistiken hinzufügen
    winning_months = (monthly_returns['return'] > 0).sum()
    losing_months = (monthly_returns['return'] < 0).sum()
    win_rate = winning_months / (winning_months + losing_months) * 100 if (winning_months + losing_months) > 0 else 0
    
    avg_win = monthly_returns[monthly_returns['return'] > 0]['return'].mean() if winning_months > 0 else 0
    avg_loss = monthly_returns[monthly_returns['return'] < 0]['return'].mean() if losing_months > 0 else 0
    
    plt.figtext(0.15, 0.01, f"Gewinnmonate: {winning_months} ({win_rate:.1f}%)", ha='left')
    plt.figtext(0.4, 0.01, f"Verlustmonate: {losing_months}", ha='left')
    plt.figtext(0.65, 0.01, f"Ø Gewinn: {avg_win:.2f}%, Ø Verlust: {avg_loss:.2f}%", ha='left')
    
    plt.tight_layout()
    plt.subplots_adjust(bottom=0.15)
    
    # Grafik speichern, wenn Pfad angegeben
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"Monatliche Analyse gespeichert: {save_path}")
    
    plt.show()

def create_trade_analysis_plots(df_trades: pd.DataFrame, save_path: Optional[str] = None):
    """
    Erstellt eine detaillierte Analyse der Trades als Grafiken.
    
    Args:
        df_trades: DataFrame mit Trades
        save_path: Pfad zum Speichern der Grafik (optional)
    """
    if df_trades is None or df_trades.empty:
        logger.warning("Keine Trades für Analyse vorhanden")
        return
    
    # Grafiken erstellen
    fig = plt.figure(figsize=(15, 10))
    
    # Grafik 1: Trade-Größenverteilung
    plt.subplot(2, 2, 1)
    plt.hist(df_trades['net_profit'], bins=20, color='blue', alpha=0.7)
    plt.axvline(x=0, color='red', linestyle='--')
    plt.title('Trade-Größenverteilung')
    plt.xlabel('Profit/Loss ($)')
    plt.ylabel('Anzahl der Trades')
    plt.grid(True)
    
    # Grafik 2: Kumulative Profit/Loss
    plt.subplot(2, 2, 2)
    plt.plot(np.arange(1, len(df_trades) + 1), df_trades['net_profit'].cumsum(), color='green')
    plt.title('Kumulative Profit/Loss')
    plt.xlabel('Trade #')
    plt.ylabel('Kumulativer P/L ($)')
    plt.grid(True)
    
    # Grafik 3: Trade-Dauer vs. Profit
    if 'duration' in df_trades.columns:
        plt.subplot(2, 2, 3)
        plt.scatter(df_trades['duration'], df_trades['net_profit'], 
                   c=df_trades['profitable'].map({True: 'green', False: 'red'}), alpha=0.7)
        plt.axhline(y=0, color='black', linestyle='--')
        plt.title('Trade-Dauer vs. Profit')
        plt.xlabel('Dauer (Stunden)')
        plt.ylabel('Profit/Loss ($)')
        plt.grid(True)
    
    # Grafik 4: Gewinn/Verlust pro Monat
    plt.subplot(2, 2, 4)
    if 'exit_time' in df_trades.columns:
        df_trades['month'] = df_trades['exit_time'].dt.to_period('M')
        monthly_profit = df_trades.groupby('month')['net_profit'].sum()
        
        monthly_profit.plot(kind='bar', color=['green' if p > 0 else 'red' for p in monthly_profit])
        plt.title('Profit/Loss pro Monat')
        plt.xlabel('Monat')
        plt.ylabel('Profit/Loss ($)')
        plt.grid(True)
        plt.xticks(rotation=45)
    
    plt.tight_layout()
    
    # Grafik speichern, wenn Pfad angegeben
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"Trade-Analyse gespeichert: {save_path}")
    
    plt.show()
