# Code Statusbericht

Dieser Bericht gibt einen Überblick über die Codebasis des Krypto-Bots.

## Dateistruktur

Die Codebasis ist in folgende Hauptverzeichnisse unterteilt:

- `backtesting/`: Enthält Code für Backtesting-Strategien (`backtest_engine.py`).
- `config/`: Enthält Konfigurationsdateien (`config.py`).
- `data/`: Enthält Code für die Datenverarbeitung (`data_handler.py`).
- `exchange/`: Enthält Code für die Interaktion mit der Bybit-API (`bybit_api.py`).
- `indicators/`: Enthält Code für verschiedene technische Indikatoren (z.B. `moving_averages.py`, `oscillators.py`, `support_resistance.py`, `volatility.py`).
- `risk/`: Enthält Code für das Risikomanagement (`risk_manager.py`).
- `strategies/`: Enthält Code für verschiedene Handelsstrategien (z.B. `bollinger_bands.py`, `macd.py`, `moving_average.py`, `multi_timeframe.py`, `smart_money_strategy.py`).
- `utils/`: Enthält Hilfsfunktionen (z.B. `logging.py`, `validation.py`).
- `visualization/`: Enthält Code für die Visualisierung von Daten (`charts.py`).

## Wichtige Dateien

- `run_backtest.py`: Skript zum Ausführen von Backtests.
- `run_live.py`: Skript zum Ausführen des Bots im Live-Modus.
- `analyze_results.py`: Skript zum Analysieren der Ergebnisse von Backtests.
- `strategies/smart_money_strategy.py`: Implementierung einer Smart-Money-Strategie.
- `README.md`: Enthält allgemeine Informationen über das Projekt.

## Verwendete Strategien

Die Codebasis enthält Implementierungen für folgende Handelsstrategien:

- Bollinger Bands
- MACD
- Moving Average
- Multi-Timeframe
- Smart Money

## Verwendete Indikatoren

Die Codebasis verwendet verschiedene technische Indikatoren, darunter:

- Moving Averages
- Oscillators
- Support and Resistance
- Volatility

## Offene Tabs in VSCode

Die folgenden Dateien sind derzeit in VSCode geöffnet:

- `run_live.py`
- `analyze_results.py`
- `strategies/smart_money_strategy.py`
- `README.md`
- `run_backtest.py`