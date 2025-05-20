import pandas as pd
import json
import logging
import matplotlib.pyplot as plt
import os

# Konfiguriere das Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_backtest_results(filepath):
    """
    Lädt Backtest-Ergebnisse aus einer JSON-Datei.
    """
    try:
        with open(filepath, 'r') as f:
            results = json.load(f)
        logging.info(f"Backtest-Ergebnisse erfolgreich aus {filepath} geladen.")
        return results
    except FileNotFoundError:
        logging.error(f"Datei nicht gefunden: {filepath}")
        return None
    except json.JSONDecodeError:
        logging.error(f"Fehler beim Dekodieren der JSON-Datei: {filepath}")
        return None
    except Exception as e:
        logging.error(f"Fehler beim Laden der Backtest-Ergebnisse: {e}")
        return None

def analyze_results(results):
    """
    Analysiert die geladenen Backtest-Ergebnisse.
    Gibt einen DataFrame mit den Analyseergebnissen zurück.
    """
    if not results or 'trades' not in results:
        logging.warning("Keine oder unvollständige Ergebnisse zur Analyse vorhanden.")
        return None

    trades = pd.DataFrame(results['trades'])

    if trades.empty:
        logging.warning("Keine Trades in den Ergebnissen gefunden.")
        return None

    # Berechne grundlegende Metriken
    total_trades = len(trades)
    winning_trades = trades[trades['profit_usd'] > 0]
    losing_trades = trades[trades['profit_usd'] < 0]
    total_profit_usd = trades['profit_usd'].sum()
    win_rate = len(winning_trades) / total_trades if total_trades > 0 else 0
    average_profit_per_trade = total_profit_usd / total_trades if total_trades > 0 else 0
    average_winning_trade = winning_trades['profit_usd'].mean() if not winning_trades.empty else 0
    average_losing_trade = losing_trades['profit_usd'].mean() if not losing_trades.empty else 0
    largest_winning_trade = winning_trades['profit_usd'].max() if not winning_trades.empty else 0
    largest_losing_trade = losing_trades['profit_usd'].min() if not losing_trades.empty else 0

    # Berechne Drawdown (vereinfacht)
    # Dies ist eine einfache Methode, eine detailliertere Drawdown-Berechnung wäre komplexer
    cumulative_profit = trades['profit_usd'].cumsum()
    peak = cumulative_profit.expanding(min_periods=1).max()
    drawdown = (peak - cumulative_profit) / peak
    max_drawdown = drawdown.max() if not drawdown.empty else 0

    analysis_summary = {
        "Total Trades": total_trades,
        "Winning Trades": len(winning_trades),
        "Losing Trades": len(losing_trades),
        "Win Rate (%)": win_rate * 100,
        "Total Profit (USD)": total_profit_usd,
        "Average Profit per Trade (USD)": average_profit_per_trade,
        "Average Winning Trade (USD)": average_winning_trade,
        "Average Losing Trade (USD)": average_losing_trade,
        "Largest Winning Trade (USD)": largest_winning_trade,
        "Largest Losing Trade (USD)": largest_losing_trade,
        "Max Drawdown (%)": max_drawdown * 100 # Negativer Wert für Drawdown
    }

    logging.info("Analyse abgeschlossen.")
    return pd.DataFrame([analysis_summary])

def plot_results(results, output_dir="analysis_plots"):
    """
    Plottet die kumulative Performance der Backtest-Ergebnisse.
    """
    if not results or 'trades' not in results:
        logging.warning("Keine oder unvollständige Ergebnisse zum Plotten vorhanden.")
        return

    trades = pd.DataFrame(results['trades'])

    if trades.empty:
        logging.warning("Keine Trades zum Plotten gefunden.")
        return

    trades['cumulative_profit'] = trades['profit_usd'].cumsum()

    plt.figure(figsize=(12, 6))
    plt.plot(trades.index, trades['cumulative_profit'], label='Kumulativer Profit (USD)')
    plt.xlabel("Trade Index")
    plt.ylabel("Kumulativer Profit (USD)")
    plt.title("Kumulative Performance des Backtests")
    plt.legend()
    plt.grid(True)

    # Stelle sicher, dass das Ausgabeverzeichnis existiert
    os.makedirs(output_dir, exist_ok=True)
    plot_filepath = os.path.join(output_dir, "cumulative_performance.png")
    plt.savefig(plot_filepath)
    logging.info(f"Kumulative Performance Grafik gespeichert unter: {plot_filepath}")
    # plt.show() # Optional: Zeige das Plot direkt an

def main():
    """
    Hauptfunktion für die Analyse der Backtest-Ergebnisse.
    """
    import argparse

    parser = argparse.ArgumentParser(description="Analysiere Backtest-Ergebnisse.")
    parser.add_argument("results_filepath", help="Pfad zur JSON-Datei mit den Backtest-Ergebnissen.")
    parser.add_argument("--plot", action="store_true", help="Plotte die Ergebnisse.")
    parser.add_argument("--output_dir", default="analysis_plots", help="Verzeichnis zum Speichern der Plots.")

    args = parser.parse_args()

    results = load_backtest_results(args.results_filepath)

    if results:
        analysis_summary_df = analyze_results(results)
        if analysis_summary_df is not None:
            print("\n--- Analyse Zusammenfassung ---")
            print(analysis_summary_df.to_string(index=False))
            print("-------------------------------\n")

        if args.plot:
            plot_results(results, args.output_dir)

if __name__ == "__main__":
    main()