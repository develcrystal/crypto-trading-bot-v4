"""
Modul für statistische Auswertungen von Backtest-Ergebnissen.
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union, Any

logger = logging.getLogger(__name__)

def calculate_drawdown_statistics(results: Dict) -> Dict:
    """
    Berechnet detaillierte Drawdown-Statistiken.
    
    Args:
        results: Dictionary mit Backtest-Ergebnissen
        
    Returns:
        Dictionary mit Drawdown-Statistiken
    """
    if not results or 'equity_curve' not in results:
        logger.warning("Keine Daten für Drawdown-Analyse vorhanden")
        return {}
    
    # DataFrame für Equity-Kurve erstellen
    df_equity = pd.DataFrame(results['equity_curve'])
    df_equity['timestamp'] = pd.to_datetime(df_equity['timestamp'])
    df_equity.set_index('timestamp', inplace=True)
    
    # Berechne Drawdown
    equity_values = np.array(df_equity['equity'])
    peak = np.maximum.accumulate(equity_values)
    drawdown = (peak - equity_values) / peak
    underwater_periods = []
    
    # Finde Underwater-Perioden
    underwater = False
    start_idx = 0
    max_dd = 0
    max_dd_idx = 0
    
    for i in range(len(drawdown)):
        if not underwater and drawdown[i] > 0:
            underwater = True
            start_idx = i
            max_dd = drawdown[i]
            max_dd_idx = i
        elif underwater:
            if drawdown[i] > max_dd:
                max_dd = drawdown[i]
                max_dd_idx = i
            if drawdown[i] == 0:
                underwater = False
                recovery_time = (df_equity.index[i] - df_equity.index[start_idx]).days
                underwater_periods.append({
                    'start_date': df_equity.index[start_idx],
                    'end_date': df_equity.index[i],
                    'duration_days': recovery_time,
                    'max_drawdown': max_dd * 100,
                    'max_drawdown_date': df_equity.index[max_dd_idx]
                })
    
    # Wenn am Ende noch underwater
    if underwater:
        recovery_time = (df_equity.index[-1] - df_equity.index[start_idx]).days
        underwater_periods.append({
            'start_date': df_equity.index[start_idx],
            'end_date': df_equity.index[-1],
            'duration_days': recovery_time,
            'max_drawdown': max_dd * 100,
            'max_drawdown_date': df_equity.index[max_dd_idx]
        })
    
    # Sortiere nach Drawdown-Größe
    underwater_periods.sort(key=lambda x: x['max_drawdown'], reverse=True)
    
    # Erstelle DataFrame mit Underwater-Perioden
    df_underwater = pd.DataFrame(underwater_periods)
    
    # Berechne statistische Kennzahlen
    max_dd_overall = drawdown.max() * 100
    avg_dd = drawdown.mean() * 100
    dd_std = drawdown.std() * 100
    
    # Gebe Statistiken zurück
    underwater_stats = {
        'max_drawdown': max_dd_overall,
        'avg_drawdown': avg_dd,
        'drawdown_std': dd_std,
        'underwater_periods': len(underwater_periods),
        'underwater_periods_details': df_underwater.to_dict('records') if not df_underwater.empty else []
    }
    
    return underwater_stats

def calculate_monthly_returns(results: Dict) -> pd.DataFrame:
    """
    Berechnet monatliche Renditen.
    
    Args:
        results: Dictionary mit Backtest-Ergebnissen
        
    Returns:
        DataFrame mit monatlicher Performance
    """
    if not results or 'equity_curve' not in results:
        logger.warning("Keine Daten für monatliche Analyse vorhanden")
        return pd.DataFrame()
    
    # DataFrame für Equity-Kurve erstellen
    df_equity = pd.DataFrame(results['equity_curve'])
    df_equity['timestamp'] = pd.to_datetime(df_equity['timestamp'])
    df_equity.set_index('timestamp', inplace=True)
    
    # Berechne tägliche Returns
    df_equity['daily_return'] = df_equity['equity'].pct_change()
    
    # Extrahiere Jahr und Monat
    df_equity['year'] = df_equity.index.year
    df_equity['month'] = df_equity.index.month
    
    # Berechne monatliche Renditen
    monthly_returns = df_equity.groupby(['year', 'month']).apply(
        lambda x: (x['equity'].iloc[-1] / x['equity'].iloc[0] - 1) * 100
    ).reset_index()
    monthly_returns.columns = ['year', 'month', 'return']
    
    # Füge Monatsname hinzu
    month_names = {
        1: 'Jan', 2: 'Feb', 3: 'Mär', 4: 'Apr', 5: 'Mai', 6: 'Jun',
        7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Okt', 11: 'Nov', 12: 'Dez'
    }
    monthly_returns['month_name'] = monthly_returns['month'].map(month_names)
    monthly_returns['period'] = monthly_returns['year'].astype(str) + '-' + monthly_returns['month_name']
    
    return monthly_returns

def calculate_trade_statistics(results: Dict) -> Dict:
    """
    Berechnet detaillierte Trade-Statistiken.
    
    Args:
        results: Dictionary mit Backtest-Ergebnissen
        
    Returns:
        Dictionary mit Trade-Statistiken und DataFrame mit Trades
    """
    if not results or 'trades' not in results or not results['trades']:
        logger.warning("Keine Trades für Analyse vorhanden")
        return {}, pd.DataFrame()
    
    # DataFrame mit Trades erstellen
    df_trades = pd.DataFrame(results['trades'])
    
    # Konvertiere Zeitstempel
    df_trades['entry_time'] = pd.to_datetime(df_trades['entry_time'])
    df_trades['exit_time'] = pd.to_datetime(df_trades['exit_time'])
    
    # Berechne Trade-Dauer
    df_trades['duration'] = (df_trades['exit_time'] - df_trades['entry_time']).dt.total_seconds() / 3600  # in Stunden
    
    # Kategorisiere Trades
    df_trades['profitable'] = df_trades['net_profit'] > 0
    
    # Trade-Statistiken
    total_trades = len(df_trades)
    winning_trades = df_trades['profitable'].sum()
    losing_trades = total_trades - winning_trades
    
    win_rate = winning_trades / total_trades if total_trades > 0 else 0
    
    avg_profit = df_trades[df_trades['profitable']]['net_profit'].mean() if winning_trades > 0 else 0
    avg_loss = df_trades[~df_trades['profitable']]['net_profit'].mean() if losing_trades > 0 else 0
    
    profit_factor = abs(df_trades[df_trades['profitable']]['net_profit'].sum() / 
                      df_trades[~df_trades['profitable']]['net_profit'].sum()) if losing_trades > 0 else float('inf')
    
    avg_duration = df_trades['duration'].mean()
    max_duration = df_trades['duration'].max()
    min_duration = df_trades['duration'].min()
    
    # Weitere Statistiken berechnen
    consecutive_wins = 0
    consecutive_losses = 0
    max_consecutive_wins = 0
    max_consecutive_losses = 0
    current_streak = 0
    
    for profitable in df_trades['profitable']:
        if profitable:
            if current_streak > 0:
                current_streak += 1
            else:
                current_streak = 1
            max_consecutive_wins = max(max_consecutive_wins, current_streak)
        else:
            if current_streak < 0:
                current_streak -= 1
            else:
                current_streak = -1
            max_consecutive_losses = max(max_consecutive_losses, abs(current_streak))
    
    # Durchschnittliches Risiko-Ertrags-Verhältnis berechnen
    if 'position' in df_trades.columns and 'entry_price' in df_trades.columns and 'exit_price' in df_trades.columns:
        # Für Long-Positionen
        long_trades = df_trades[df_trades['position'] == 'long']
        if len(long_trades) > 0:
            long_rr = abs((long_trades['exit_price'] - long_trades['entry_price']) / 
                        (long_trades['entry_price'] - long_trades['stop_loss'])) if 'stop_loss' in long_trades.columns else None
        else:
            long_rr = None
        
        # Für Short-Positionen
        short_trades = df_trades[df_trades['position'] == 'short']
        if len(short_trades) > 0:
            short_rr = abs((short_trades['entry_price'] - short_trades['exit_price']) / 
                         (short_trades['stop_loss'] - short_trades['entry_price'])) if 'stop_loss' in short_trades.columns else None
        else:
            short_rr = None
        
        if long_rr is not None and short_rr is not None:
            avg_rr = pd.concat([long_rr, short_rr]).mean()
        elif long_rr is not None:
            avg_rr = long_rr.mean()
        elif short_rr is not None:
            avg_rr = short_rr.mean()
        else:
            avg_rr = None
    else:
        avg_rr = None
    
    # Trade-Statistiken zusammenfassen
    trade_stats = {
        'total_trades': total_trades,
        'winning_trades': winning_trades,
        'losing_trades': losing_trades,
        'win_rate': win_rate * 100,
        'avg_profit': avg_profit,
        'avg_loss': avg_loss,
        'profit_factor': profit_factor,
        'avg_duration_hours': avg_duration,
        'max_duration_hours': max_duration,
        'min_duration_hours': min_duration,
        'max_consecutive_wins': max_consecutive_wins,
        'max_consecutive_losses': max_consecutive_losses,
        'avg_risk_reward': avg_rr
    }
    
    return trade_stats, df_trades

def create_performance_metrics(results: Dict, trade_stats: Dict, underwater_stats: Dict) -> pd.DataFrame:
    """
    Erstellt eine Tabelle mit allen Performance-Metriken.
    
    Args:
        results: Dictionary mit Backtest-Ergebnissen
        trade_stats: Dictionary mit Trade-Statistiken
        underwater_stats: Dictionary mit Drawdown-Statistiken
        
    Returns:
        DataFrame mit Performance-Metriken
    """
    # Basis-Metriken aus den Backtest-Ergebnissen
    metrics = results.get('metrics', {})
    
    # Erstelle Dictionary mit allen Metriken
    all_metrics = {
        'Allgemeine Metriken': {
            'Symbol': results.get('symbol', 'Unbekannt'),
            'Strategie': results.get('strategy', 'Unbekannt'),
            'Zeitraum': f"{results.get('start_date', 'Unbekannt')} bis {results.get('end_date', 'Unbekannt')}",
            'Anfangsguthaben': f"${results.get('initial_balance', 0):.2f}",
            'Endguthaben': f"${results.get('final_balance', 0):.2f}",
            'Gesamtrendite': f"{metrics.get('return', 0):.2f}%",
            'Annualisierte Rendite': f"{metrics.get('annualized_return', 0):.2f}%"
        },
        'Risk/Reward Metriken': {
            'Sharpe Ratio': metrics.get('sharpe_ratio', 0),
            'Calmar Ratio': metrics.get('calmar_ratio', 0),
            'Maximaler Drawdown': f"{metrics.get('max_drawdown', 0):.2f}%",
            'Durchschnittlicher Drawdown': f"{underwater_stats.get('avg_drawdown', 0):.2f}%",
            'Underwater Perioden': underwater_stats.get('underwater_periods', 0)
        },
        'Trade-Statistiken': {
            'Anzahl Trades': trade_stats.get('total_trades', 0),
            'Gewinnende Trades': trade_stats.get('winning_trades', 0),
            'Verlierende Trades': trade_stats.get('losing_trades', 0),
            'Win Rate': f"{trade_stats.get('win_rate', 0):.2f}%",
            'Profit Factor': f"{trade_stats.get('profit_factor', 0):.2f}",
            'Durchschn. Gewinn': f"${trade_stats.get('avg_profit', 0):.2f}",
            'Durchschn. Verlust': f"${trade_stats.get('avg_loss', 0):.2f}",
            'Max Consecutive Wins': trade_stats.get('max_consecutive_wins', 0),
            'Max Consecutive Losses': trade_stats.get('max_consecutive_losses', 0)
        },
        'Timing-Statistiken': {
            'Durchschn. Trade-Dauer': f"{trade_stats.get('avg_duration_hours', 0):.2f} Stunden",
            'Max Trade-Dauer': f"{trade_stats.get('max_duration_hours', 0):.2f} Stunden",
            'Min Trade-Dauer': f"{trade_stats.get('min_duration_hours', 0):.2f} Stunden"
        }
    }
    
    # In flaches Dictionary konvertieren für DataFrame
    flat_metrics = {}
    for category, metrics_dict in all_metrics.items():
        for metric, value in metrics_dict.items():
            flat_metrics[f"{category} - {metric}"] = value
    
    # DataFrame erstellen
    df = pd.DataFrame.from_dict(flat_metrics, orient='index', columns=['Wert'])
    df.index.name = 'Metrik'
    
    return df
