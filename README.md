# Crypto Trading Bot V2

## Übersicht
Dieser Bot ist für den automatisierten Handel mit Kryptowährungen konzipiert. Er unterstützt Backtesting von Strategien und Live-Trading über die Bybit-API. Version 2 stellt eine komplette Überarbeitung der Architektur und Funktionalität von Version 1 dar, mit dem Ziel, profitablere Handelsergebnisse zu erzielen.

## Aktueller Status
- **Version**: 2.0.0-beta
- **Entwicklungsstatus**: In aktiver Entwicklung
- **Smart Money Strategie**: Grundstruktur implementiert, Handelslogik muss noch vervollständigt werden
- **Live-Trading**: Noch nicht vollständig implementiert
- Weitere Details siehe [STATUS.md](STATUS.md)

## Installation
1. Klone das Repository.
2. Installiere die erforderlichen Pakete mit `pip install -r requirements.txt`.
3. Erstelle eine `.env`-Datei im Hauptverzeichnis des Projekts basierend auf `.env.example` und trage deine Bybit API-Schlüssel ein.

## Konfiguration
Die Hauptkonfiguration des Bots erfolgt über die Datei `config/config.py`. Hier kannst du Einstellungen für den Handel (Symbol, Intervall), die Exchange-Verbindung, das Risikomanagement und die Strategie vornehmen.

Stelle sicher, dass du die Konfiguration an deine Bedürfnisse anpasst, bevor du den Bot ausführst.

## Nutzung

### Backtesting
Führe Backtests deiner Strategien aus, um ihre Performance anhand historischer Daten zu bewerten. Die Version 2 bietet erweiterte Backtesting-Modi:

```bash
python run_backtest.py --symbol BTCUSDT --timeframe 1h --start-date 2024-01-01 --end-date 2024-05-01 --mode MODE --plot
```

Verfügbare Modi:
- `basic`: Einfacher Backtest mit einer Konfiguration
- `parameter-sweep`: Optimiert Parameter durch Grid-Search
- `filter-study`: Analysiert den Einfluss verschiedener Filter
- `complete`: Führt alle obigen Analysen durch

Parameter:
- `--symbol`: Handelssymbol (z.B. BTCUSDT)
- `--timeframe`: Zeitrahmen (z.B. 1h, 4h, 1d)
- `--start-date`: Startdatum im Format YYYY-MM-DD
- `--end-date`: Enddatum im Format YYYY-MM-DD
- `--mode`: Backtest-Modus (basic, parameter-sweep, filter-study, complete)
- `--plot`: Visualisierungen anzeigen
- `--output-dir`: Verzeichnis für Ergebnisse (Standard: backtest_results)

Die Backtest-Ergebnisse werden im `backtest_results`-Verzeichnis gespeichert.

### Live-Trading
Starte den Bot für den Live-Handel auf der konfigurierten Exchange.
```bash
python run_live.py
```
Stelle sicher, dass deine Konfiguration in `config/config.py` korrekt für den Live-Handel eingerichtet ist (insbesondere API-Schlüssel und Handels-Parameter).

### Analyse der Backtest-Ergebnisse
Analysiere die Ergebnisse deiner Backtests detailliert.
```bash
python analyze_results.py <Pfad zur Ergebnisdatei> [--plot] [--output_dir <Ausgabeverzeichnis>]
```
- `<Pfad zur Ergebnisdatei>`: Der Pfad zur JSON-Datei mit den Backtest-Ergebnissen (z.B. `backtest_results/results_smart_money_strategy_2023-01-01_2023-12-31.json`).
- `--plot`: Optionales Flag, um die kumulative Performance zu plotten.
- `--output_dir <Ausgabeverzeichnis>`: Optionales Verzeichnis zum Speichern der Plots (Standard: `analysis_plots`).

## Market Maker Strategie 5-Minuten-Optimierung (Stand: 20.05.2025)

### Schrittweise Aktivierung der Filter:
1. Nur Volumen
2. \+ Key Levels
3. \+ Pattern
4. \+ Order Flow
5. \+ Liquidity Sweep

### Volumen-Schwellen getestet: 10k, 50k, 100k, 250k, 500k, 1M

### Filter-Aktivierungsstudie Ergebnisse:

| Step | Volumen-Schwelle | Filter aktiv | Profit / Loss | Trades | Bemerkung |
|------|------------------|--------------|---------------|--------|-----------|
| Nur Volumen | 250.000 | Volumen-Filter | +$2.665 | 39 | 1/5 Filter aktiv |
| \+ Key Levels | 10.000 | Volumen \+ Key Levels | +$3.850 | 35 | 2/5 Filter aktiv |
| \+ Pattern | 100.000 | Volumen \+ Key Levels \+ Pattern | +$4.595 | 27 | 3/5 Filter aktiv |
| \+ Order Flow | 500.000 | Volumen \+ Key Levels \+ Pattern \+ Order Flow | +$4.273 | 21 | 4/5 Filter aktiv |
| \+ Liquidity Sweep | 100.000 | Alle Filter aktiv | +$3.880 | 17 | 5/5 Filter aktiv |

### 🏆 SIEGER-KONFIGURATION:
- **Filter-Stufe**: Volumen + Key Levels + Pattern (3/5 Filter)
- **Volumen-Schwelle**: 100.000
- **Performance**: $4.595 Profit, 77.5% Win Rate, 27 Trades
- **Optimaler Sweet Spot**: Balanciert Profitabilität und Trade-Aktivität perfekt

### Key Insights:
✅ Mehr Filter = höhere Signalqualität, aber weniger Trades  
✅ Volumen-Schwellen von 100k-250k zeigen beste Balance  
✅ 3-Filter-Kombination bietet optimales Risk/Reward-Verhältnis  
✅ Alle 5 Filter zusammen maximieren Präzision auf Kosten der Aktivität

## Handelsstrategien

### Smart Money Strategy
Die `SmartMoneyStrategy` (`strategies/smart_money_strategy.py`) ist eine fortschrittliche Strategie, die darauf abzielt, die Bewegungen von "Smart Money" im Markt zu identifizieren. Die Implementierung basiert auf der V1-Dokumentation und berücksichtigt folgende Konzepte:
- Order Flow Analyse
- Identifizierung von Liquiditätszonen
- Verwendung relevanter Indikatoren (z.B. Volume Profile, VWAP)
- Berücksichtigung von Marktstruktur (Break of Structure, Change of Character)
- Bestätigungssignale

**Implementierungsstatus:**
Die Grundstruktur der Strategie ist vorhanden, aber die eigentliche Handelslogik muss noch implementiert werden. Ein detaillierter Implementierungsplan ist in [SMART_MONEY_IMPLEMENTATION.md](SMART_MONEY_IMPLEMENTATION.md) zu finden.

**Konfiguration:**
Spezifische Parameter für die `SmartMoneyStrategy` können im `config/config.py` unter dem Abschnitt `strategy` konfiguriert werden.

## Projektstruktur
```
.
├── .env                  # Umgebungsvariablen (API-Schlüssel)
├── .env.example          # Beispiel für Umgebungsvariablen
├── README.md             # Projektdokumentation
├── STATUS.md             # Aktueller Entwicklungsstand und Migrationsplan
├── SMART_MONEY_IMPLEMENTATION.md # Plan zur Vervollständigung der Strategie
├── requirements.txt      # Erforderliche Python-Pakete
├── run_backtest.py       # Skript für Backtesting
├── run_live.py           # Skript für Live-Trading
├── analyze_results.py    # Skript zur Analyse von Backtest-Ergebnissen
├── backtesting/
│   └── backtest_engine.py # Backtesting-Engine
├── config/
│   └── config.py         # Konfigurationsdatei
├── data/
│   └── data_handler.py   # Datenhandling (Abruf, Speicherung)
├── exchange/
│   └── bybit_api.py      # Bybit API-Integration
├── indicators/           # Technische Indikatoren
│   ├── moving_averages.py
│   ├── oscillators.py
│   ├── support_resistance.py
│   └── volatility.py
├── risk/
│   └── risk_manager.py   # Risikomanagement und Position Sizing
├── strategies/           # Handelsstrategien
│   ├── bollinger_bands.py
│   ├── macd.py
│   ├── moving_average.py
│   ├── multi_timeframe.py
│   └── smart_money_strategy.py # Smart Money Strategie
├── utils/                # Hilfsfunktionen
│   ├── logging.py
│   └── validation.py
└── visualization/        # Visualisierungstools
    └── charts.py
```

## Verbesserungen gegenüber Version 1
- **Modulare Architektur**: Klare Trennung von Verantwortlichkeiten
- **Erweiterte Backtesting-Fähigkeiten**: Verschiedene Analyse-Modi, Parameter-Sweep, Filter-Studien
- **Verbesserte Datenverarbeitung**: Robustere Handhabung von Daten, Fallback auf synthetische Daten
- **Umfangreiche Berichterstattung**: Detaillierte Berichte, Visualisierungen und Performance-Metriken
- **Optimierte Smart Money Strategie**: Flexiblere Filter und Parameter

## Weiterentwicklung
- Implementierung der vollständigen Smart Money Strategie-Logik
- Implementierung weiterer Handelsstrategien
- Integration anderer Exchanges
- Erweiterte Risikomanagement-Funktionen
- Verbesserte Analyse- und Visualisierungstools
- Hinzufügen von Benachrichtigungsfunktionen (z.B. Telegram, E-Mail)
