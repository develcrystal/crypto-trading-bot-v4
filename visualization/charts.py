"""
Visualisierungs-Modul für den Crypto Trading Bot.
Erstellt verschiedene Charts und Visualisierungen für Backtesting und Live-Trading.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from typing import Dict, List, Optional, Tuple, Union
from pathlib import Path
import mplfinance as mpf


def set_style():
    """Setzt den Stil für die Plots."""
    plt.style.use('seaborn-darkgrid')
    sns.set_context("paper")
    plt.rcParams['figure.figsize'] = (12, 7)
    plt.rcParams['font.size'] = 12


def plot_equity_curve(equity_data: pd.Series, title: str = "Equity Curve", 
                      save_path: Optional[str] = None):
    """
    Zeichnet eine Equity-Kurve aus den Equity-Daten.
    
    :param equity_data: Pandas Series mit Equity-Werten
    :param title: Titel des Plots
    :param save_path: Pfad zum Speichern des Plots (optional)
    """
    plt.figure(figsize=(12, 7))
    
    # Zeichne die Equity-Kurve
    plt.plot(equity_data.index, equity_data.values, label='Equity', color='blue', linewidth=2)
    
    # Zeichne eine horizontale Linie für das Anfangskapital
    plt.axhline(y=equity_data.iloc[0], color='gray', linestyle='--', alpha=0.7)
    
    # Berechne den Drawdown
    drawdown = equity_data.copy()
    drawdown_pct = equity_data.copy()
    
    peak = equity_data.expanding().max()
    drawdown = equity_data / peak - 1.0
    
    # Zeichne den Drawdown
    plt.fill_between(equity_data.index, 0, drawdown.values, alpha=0.3, color='red')
    
    # Formatierung
    plt.title(title, fontsize=16)
    plt.xlabel('Datum', fontsize=12)
    plt.ylabel('Kapital', fontsize=12)
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Formatiere die x-Achse für Datumsangaben
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
    
    plt.tight_layout()
    
    # Speichere den Plot, falls gewünscht
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    plt.show()


def plot_drawdown(equity_data: pd.Series, title: str = "Drawdown Analysis", 
                 save_path: Optional[str] = None):
    """
    Zeichnet eine Drawdown-Analyse.
    
    :param equity_data: Pandas Series mit Equity-Werten
    :param title: Titel des Plots
    :param save_path: Pfad zum Speichern des Plots (optional)
    """
    plt.figure(figsize=(12, 7))
    
    # Berechne den Drawdown
    peak = equity_data.expanding().max()
    drawdown = equity_data / peak - 1.0
    
    # Zeichne den Drawdown
    plt.fill_between(equity_data.index, 0, drawdown.values * 100, alpha=0.5, color='red')
    plt.plot(equity_data.index, drawdown.values * 100, color='darkred', linewidth=1)
    
    # Finde den maximalen Drawdown
    max_drawdown = drawdown.min()
    max_drawdown_date = drawdown.idxmin()
    
    # Markiere den maximalen Drawdown
    plt.scatter(max_drawdown_date, max_drawdown * 100, color='darkred', s=100, zorder=5)
    plt.annotate(f'Max Drawdown: {max_drawdown * 100:.2f}%',
                xy=(max_drawdown_date, max_drawdown * 100),
                xytext=(30, 20),
                textcoords='offset points',
                arrowprops=dict(arrowstyle='->'))
    
    # Formatierung
    plt.title(title, fontsize=16)
    plt.xlabel('Datum', fontsize=12)
    plt.ylabel('Drawdown (%)', fontsize=12)
    plt.grid(True, alpha=0.3)
    
    # Y-Achse invertieren für bessere Darstellung
    plt.gca().invert_yaxis()
    
    # Formatiere die x-Achse für Datumsangaben
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
    
    plt.tight_layout()
    
    # Speichere den Plot, falls gewünscht
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    plt.show()


def plot_performance_metrics(metrics: Dict, title: str = "Performance Metrics", 
                            save_path: Optional[str] = None):
    """
    Zeichnet Performance-Metriken als Balkendiagramm.
    
    :param metrics: Dictionary mit Performance-Metriken
    :param title: Titel des Plots
    :param save_path: Pfad zum Speichern des Plots (optional)
    """
    plt.figure(figsize=(12, 8))
    
    # Wähle relevante Metriken für die Visualisierung
    selected_metrics = {
        'Win Rate': metrics.get('win_rate', 0) * 100,
        'Avg. Profit (%)': metrics.get('avg_profit_pct', 0),
        'Avg. Loss (%)': abs(metrics.get('avg_loss_pct', 0)),
        'Profit Factor': metrics.get('profit_factor', 0),
        'Expectancy': metrics.get('expectancy', 0),
        'Sharpe Ratio': metrics.get('sharpe_ratio', 0)
    }
    
    # Erzeuge Balkendiagramm
    bars = plt.bar(selected_metrics.keys(), selected_metrics.values())
    
    # Farbige Balken
    colors = ['green', 'lightgreen', 'red', 'purple', 'blue', 'orange']
    for i, bar in enumerate(bars):
        bar.set_color(colors[i % len(colors)])
    
    # Füge Werte zu den Balken hinzu
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{height:.2f}', ha='center', va='bottom')
    
    # Formatierung
    plt.title(title, fontsize=16)
    plt.ylabel('Wert', fontsize=12)
    plt.grid(True, alpha=0.3, axis='y')
    
    # Zusätzliche Metriken als Text
    info_text = (
        f"Total Trades: {metrics.get('total_trades', 0)}\n"
        f"Max Drawdown: {metrics.get('max_drawdown', 0):.2f}%"
    )
    plt.figtext(0.15, 0.02, info_text, fontsize=12)
    
    plt.tight_layout()
    
    # Speichere den Plot, falls gewünscht
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    plt.show()


def plot_trades_on_chart(ohlcv_data: pd.DataFrame, trades: List[Dict], 
                        title: str = "Trades Analysis", save_path: Optional[str] = None):
    """
    Zeichnet die Trades auf einem Preischart.
    
    :param ohlcv_data: DataFrame mit OHLCV-Daten
    :param trades: Liste von Trade-Dictionaries
    :param title: Titel des Plots
    :param save_path: Pfad zum Speichern des Plots (optional)
    """
    # Vorbereitung der Daten für mplfinance
    ohlcv_data = ohlcv_data.copy()
    
    if not isinstance(ohlcv_data.index, pd.DatetimeIndex):
        # Wenn der Index kein DatetimeIndex ist, konvertieren
        ohlcv_data['date'] = pd.to_datetime(ohlcv_data.index)
        ohlcv_data.set_index('date', inplace=True)
    
    # Stelle sicher, dass die Spalten die richtigen Namen haben
    renamed_cols = {}
    for expected, possible_names in {
        'open': ['open', 'Open'],
        'high': ['high', 'High'],
        'low': ['low', 'Low'],
        'close': ['close', 'Close'],
        'volume': ['volume', 'Volume']
    }.items():
        for name in possible_names:
            if name in ohlcv_data.columns:
                renamed_cols[name] = expected
                break
    
    ohlcv_data.rename(columns=renamed_cols, inplace=True)
    
    # Bereite Marker für Trades vor
    buypoints = []
    sellpoints = []
    
    for trade in trades:
        if trade.get('direction') == 'long':
            # Finde Einstiegspunkt für Long-Trades
            entry_time = trade.get('entry_time')
            entry_price = trade.get('entry_price')
            
            # Finde Ausstiegspunkt für Long-Trades
            exit_time = trade.get('exit_time')
            exit_price = trade.get('exit_price')
            
            if entry_time and entry_price:
                buypoints.append(
                    (pd.to_datetime(entry_time), entry_price)
                )
            
            if exit_time and exit_price:
                sellpoints.append(
                    (pd.to_datetime(exit_time), exit_price)
                )
        elif trade.get('direction') == 'short':
            # Finde Einstiegspunkt für Short-Trades
            entry_time = trade.get('entry_time')
            entry_price = trade.get('entry_price')
            
            # Finde Ausstiegspunkt für Short-Trades
            exit_time = trade.get('exit_time')
            exit_price = trade.get('exit_price')
            
            if entry_time and entry_price:
                sellpoints.append(
                    (pd.to_datetime(entry_time), entry_price)
                )
            
            if exit_time and exit_price:
                buypoints.append(
                    (pd.to_datetime(exit_time), exit_price)
                )
    
    # Style für den Chart
    mc = mpf.make_marketcolors(
        up='green', down='red',
        wick={'up': 'green', 'down': 'red'},
        edge={'up': 'green', 'down': 'red'},
        volume={'up': 'green', 'down': 'red'}
    )
    
    s = mpf.make_mpf_style(
        marketcolors=mc,
        gridstyle='--',
        y_on_right=False,
        facecolor='white'
    )
    
    # Trades als Marker hinzufügen
    apd = []
    if buypoints:
        apd.append(
            mpf.make_addplot(
                [x[1] if pd.to_datetime(x[0]) in ohlcv_data.index else np.nan for x in buypoints],
                type='scatter',
                marker='^',
                markersize=100,
                color='green',
                secondary_y=False
            )
        )
    if sellpoints:
        apd.append(
            mpf.make_addplot(
                [x[1] if pd.to_datetime(x[0]) in ohlcv_data.index else np.nan for x in sellpoints],
                type='scatter',
                marker='v',
                markersize=100,
                color='red',
                secondary_y=False
            )
        )
    
    # Zeichne den Chart
    fig, axes = mpf.plot(
        ohlcv_data,
        title=title,
        type='candle',
        volume=True,
        style=s,
        addplot=apd if apd else None,
        figsize=(12, 8),
        panel_ratios=(6, 1),
        returnfig=True
    )
    
    # Speichere den Plot, falls gewünscht
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
    
    plt.show()


def plot_monthly_returns(returns_data: pd.Series, title: str = "Monatliche Rendite", 
                        save_path: Optional[str] = None):
    """
    Visualisiert die monatlichen Renditen als Heatmap.
    
    :param returns_data: Pandas Series mit täglichen Renditen
    :param title: Titel des Plots
    :param save_path: Pfad zum Speichern des Plots (optional)
    """
    # Monatliche Renditen berechnen
    monthly_returns = returns_data.resample('M').sum()
    
    # Renditen in eine Pivot-Tabelle umwandeln (Jahr x Monat)
    returns_pivot = pd.DataFrame(
        [
            (t.year, t.month, monthly_returns.loc[t])
            for t in monthly_returns.index
        ],
        columns=['Year', 'Month', 'Return']
    ).pivot('Year', 'Month', 'Return')
    
    # Monatsnamen erstellen
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    returns_pivot.columns = [month_names[i-1] for i in returns_pivot.columns]
    
    plt.figure(figsize=(12, 7))
    
    # Plot der Heatmap
    sns.heatmap(
        returns_pivot,
        annot=True,
        fmt=".2f",
        cmap="RdYlGn",
        center=0,
        linewidths=1,
        cbar_kws={'label': 'Rendite (%)'}
    )
    
    # Formatierung
    plt.title(title, fontsize=16)
    plt.tight_layout()
    
    # Speichere den Plot, falls gewünscht
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    plt.show()


def plot_return_distribution(returns_data: pd.Series, title: str = "Rendite-Verteilung", 
                           save_path: Optional[str] = None):
    """
    Visualisiert die Verteilung der Renditen als Histogramm mit Normalverteilung.
    
    :param returns_data: Pandas Series mit Renditen
    :param title: Titel des Plots
    :param save_path: Pfad zum Speichern des Plots (optional)
    """
    plt.figure(figsize=(12, 7))
    
    # Histogramm der Renditen
    sns.histplot(
        returns_data,
        kde=True,
        stat="density",
        bins=50,
        color='skyblue',
        alpha=0.7
    )
    
    # Normalverteilung zum Vergleich
    x = np.linspace(returns_data.min(), returns_data.max(), 100)
    plt.plot(
        x,
        stats.norm.pdf(x, returns_data.mean(), returns_data.std()),
        'r--',
        linewidth=2,
        label='Normalverteilung'
    )
    
    # Beschriftungen für Mean, Median, Std Dev
    plt.axvline(returns_data.mean(), color='red', linestyle='--', alpha=0.7)
    plt.axvline(returns_data.median(), color='green', linestyle='-', alpha=0.7)
    
    # Formatierung
    plt.title(title, fontsize=16)
    plt.xlabel('Rendite (%)', fontsize=12)
    plt.ylabel('Dichte', fontsize=12)
    
    # Statistiken in Textform
    stats_text = (
        f"Mittelwert: {returns_data.mean():.2f}%\n"
        f"Median: {returns_data.median():.2f}%\n"
        f"Std. Abw.: {returns_data.std():.2f}%\n"
        f"Min: {returns_data.min():.2f}%\n"
        f"Max: {returns_data.max():.2f}%\n"
        f"Schiefe: {returns_data.skew():.2f}\n"
        f"Exzess-Kurtosis: {returns_data.kurtosis():.2f}"
    )
    plt.figtext(0.15, 0.70, stats_text, fontsize=12, bbox=dict(facecolor='white', alpha=0.5))
    
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    # Speichere den Plot, falls gewünscht
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    plt.show()


def plot_technical_indicators(ohlcv_data: pd.DataFrame, indicators: Dict[str, pd.Series], 
                             title: str = "Technical Analysis", save_path: Optional[str] = None):
    """
    Zeichnet ein Candlestick-Chart mit technischen Indikatoren.
    
    :param ohlcv_data: DataFrame mit OHLCV-Daten
    :param indicators: Dictionary mit Indikator-Namen als Schlüssel und Series als Werte
    :param title: Titel des Plots
    :param save_path: Pfad zum Speichern des Plots (optional)
    """
    # Vorbereitung der Daten für mplfinance
    ohlcv_data = ohlcv_data.copy()
    
    if not isinstance(ohlcv_data.index, pd.DatetimeIndex):
        # Wenn der Index kein DatetimeIndex ist, konvertieren
        ohlcv_data['date'] = pd.to_datetime(ohlcv_data.index)
        ohlcv_data.set_index('date', inplace=True)
    
    # Stelle sicher, dass die Spalten die richtigen Namen haben
    renamed_cols = {}
    for expected, possible_names in {
        'open': ['open', 'Open'],
        'high': ['high', 'High'],
        'low': ['low', 'Low'],
        'close': ['close', 'Close'],
        'volume': ['volume', 'Volume']
    }.items():
        for name in possible_names:
            if name in ohlcv_data.columns:
                renamed_cols[name] = expected
                break
    
    ohlcv_data.rename(columns=renamed_cols, inplace=True)
    
    # Style für den Chart
    mc = mpf.make_marketcolors(
        up='green', down='red',
        wick={'up': 'green', 'down': 'red'},
        edge={'up': 'green', 'down': 'red'},
        volume={'up': 'green', 'down': 'red'}
    )
    
    s = mpf.make_mpf_style(
        marketcolors=mc,
        gridstyle='--',
        y_on_right=False,
        facecolor='white'
    )
    
    # Indikatoren als Addplots hinzufügen
    apd = []
    colors = ['blue', 'orange', 'green', 'red', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']
    color_idx = 0
    
    for name, indicator in indicators.items():
        apd.append(
            mpf.make_addplot(
                indicator,
                panel=0,
                color=colors[color_idx % len(colors)],
                secondary_y=False,
                width=1,
                alpha=0.7,
                linestyle='--',
                label=name
            )
        )
        color_idx += 1
    
    # Berechne die Anzahl der Panels basierend auf Indikatoren
    npanels = 2  # OHLC + Volume
    
    # Zeichne den Chart
    fig, axes = mpf.plot(
        ohlcv_data,
        title=title,
        type='candle',
        volume=True,
        style=s,
        addplot=apd if apd else None,
        figsize=(14, 10),
        panel_ratios=(6, 1),
        returnfig=True
    )
    
    # Legende hinzufügen, falls Indikatoren vorhanden sind
    if indicators:
        leg = axes[0].legend(
            [line for line in axes[0].get_lines() if line.get_label() not in ['', '_nolegend_']],
            [line.get_label() for line in axes[0].get_lines() if line.get_label() not in ['', '_nolegend_']],
            loc='upper left',
            fontsize=10
        )
        leg.get_frame().set_alpha(0.5)
    
    # Speichere den Plot, falls gewünscht
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
    
    plt.show()


def create_performance_summary(backtest_results: Dict, output_path: Optional[str] = None):
    """
    Erstellt eine umfassende Performance-Zusammenfassung als PDF.
    
    :param backtest_results: Dictionary mit Backtest-Ergebnissen
    :param output_path: Pfad zum Speichern der PDF (optional)
    """
    from matplotlib.backends.backend_pdf import PdfPages
    
    if output_path is None:
        output_path = f"backtest_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    
    with PdfPages(output_path) as pdf:
        # 1. Equity-Kurve
        if 'equity_curve' in backtest_results:
            plt.figure(figsize=(12, 7))
            plot_equity_curve(backtest_results['equity_curve'], "Equity Curve")
            pdf.savefig()
            plt.close()
        
        # 2. Drawdown-Analyse
        if 'equity_curve' in backtest_results:
            plt.figure(figsize=(12, 7))
            plot_drawdown(backtest_results['equity_curve'], "Drawdown Analysis")
            pdf.savefig()
            plt.close()
        
        # 3. Performance-Metriken
        if 'metrics' in backtest_results:
            plt.figure(figsize=(12, 8))
            plot_performance_metrics(backtest_results['metrics'], "Performance Metrics")
            pdf.savefig()
            plt.close()
        
        # 4. Monatliche Renditen
        if 'returns' in backtest_results:
            plt.figure(figsize=(12, 7))
            plot_monthly_returns(backtest_results['returns'], "Monatliche Rendite")
            pdf.savefig()
            plt.close()
        
        # 5. Rendite-Verteilung
        if 'returns' in backtest_results:
            plt.figure(figsize=(12, 7))
            plot_return_distribution(backtest_results['returns'], "Rendite-Verteilung")
            pdf.savefig()
            plt.close()
        
        # 6. Beispielhafte Trades
        if 'ohlcv_data' in backtest_results and 'trades' in backtest_results:
            plt.figure(figsize=(14, 10))
            plot_trades_on_chart(
                backtest_results['ohlcv_data'],
                backtest_results['trades'][:10],  # Nur die ersten 10 Trades zeigen
                "Beispielhafte Trades"
            )
            pdf.savefig()
            plt.close()
    
    print(f"Performance-Zusammenfassung wurde gespeichert unter: {output_path}")


# Füge Funktionen zur Erzeugung interaktiver Charts für Web-Dashboards hinzu (optional)
# Diese können später ergänzt werden, wenn ein Web-Dashboard implementiert wird
