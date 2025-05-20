# Smart Money Strategie - Implementierungsplan

## Übersicht
Dieses Dokument beschreibt den Plan zur Vervollständigung der Smart Money Strategie-Implementierung in Version 2 des Crypto Trading Bots. Die Strategie basiert auf den Konzepten aus Version 1, wurde aber für Version 2 neu strukturiert und erweitert.

## Aktueller Status
In Version 2 ist die Struktur der Smart Money Strategie bereits implementiert, aber die eigentliche Handelslogik enthält noch Platzhalter. Die Backtesting-Engine ist vollständig funktionsfähig und bietet erweiterte Möglichkeiten zur Strategieoptimierung.

## Implementierungsschritte

### 1. Smart Money Strategie-Logik vervollständigen

Die `generate_signal`-Methode in `strategies/smart_money_strategy.py` muss implementiert werden, basierend auf der folgenden Logik:

```python
def generate_signal(self, data: pd.DataFrame) -> Dict:
    """
    Generiert ein Handelssignal basierend auf der Smart Money Strategie.
    
    Args:
        data: Ein DataFrame mit OHLCV-Daten und technischen Indikatoren
        
    Returns:
        Ein Dictionary mit dem Handelssignal ('buy', 'sell', 'hold'),
        sowie Details zur Signalberechnung
    """
    if data.empty:
        return {"action": "hold", "details": {"reason": "Keine Daten vorhanden"}}
    
    # Initialisierung
    signal = "hold"
    details = {
        "reason": "Kein Signal generiert",
        "filters_passed": [],
        "filters_failed": []
    }
    
    # Aktuellen Datenpunkt abrufen
    current = data.iloc[-1]
    
    # 1. Volumen-Filter
    if current['volume'] >= self.config.get('VOLUME_THRESHOLD', 100000):
        details['filters_passed'].append('volume')
        
        # 2. Key Levels Filter
        support_levels = self._find_nearest_support_levels(data)
        resistance_levels = self._find_nearest_resistance_levels(data)
        
        # Prüfe, ob der aktuelle Preis nahe an einem wichtigen Level ist
        price_at_key_level = self._is_price_at_key_level(current, support_levels, resistance_levels)
        
        if price_at_key_level or not self.config.get('USE_KEY_LEVELS', True):
            if price_at_key_level:
                details['filters_passed'].append('key_levels')
            
            # 3. Pattern Filter
            patterns = self._detect_patterns(data)
            if patterns or not self.config.get('USE_PATTERN_RECOGNITION', True):
                if patterns:
                    details['filters_passed'].append('pattern')
                    details['patterns'] = patterns
                
                # 4. Order Flow Filter
                order_flow = self._analyze_order_flow(data)
                if order_flow['bias'] != 'NEUTRAL' or not self.config.get('USE_ORDER_FLOW', True):
                    if order_flow['bias'] != 'NEUTRAL':
                        details['filters_passed'].append('order_flow')
                        details['order_flow'] = order_flow
                    
                    # 5. Liquidity Sweep Filter
                    liquidity_sweep = self._detect_liquidity_sweep(data, support_levels, resistance_levels)
                    if liquidity_sweep['detected'] or not self.config.get('USE_LIQUIDITY_SWEEP', True):
                        if liquidity_sweep['detected']:
                            details['filters_passed'].append('liquidity_sweep')
                            details['liquidity_sweep'] = liquidity_sweep
                        
                        # Alle Filter bestanden oder ignoriert, generiere Signal
                        if order_flow['bias'] == 'BULLISH' and (liquidity_sweep['type'] == 'SUPPORT' or not liquidity_sweep['detected']):
                            signal = "buy"
                            details['reason'] = "Bullish order flow nach liquidity sweep auf Support-Level"
                            details['stop_loss'] = self._calculate_stop_loss(data, "buy")
                            details['take_profit'] = self._calculate_take_profit(data, "buy", details['stop_loss'])
                        
                        elif order_flow['bias'] == 'BEARISH' and (liquidity_sweep['type'] == 'RESISTANCE' or not liquidity_sweep['detected']):
                            signal = "sell"
                            details['reason'] = "Bearish order flow nach liquidity sweep auf Resistance-Level"
                            details['stop_loss'] = self._calculate_stop_loss(data, "sell")
                            details['take_profit'] = self._calculate_take_profit(data, "sell", details['stop_loss'])
                    else:
                        details['filters_failed'].append('liquidity_sweep')
                else:
                    details['filters_failed'].append('order_flow')
            else:
                details['filters_failed'].append('pattern')
        else:
            details['filters_failed'].append('key_levels')
    else:
        details['filters_failed'].append('volume')
    
    return {
        "action": signal,
        "details": details
    }
```

### 2. Hilfsmethoden implementieren

Die folgenden Hilfsmethoden müssen implementiert werden:

1. `_find_nearest_support_levels`: Findet die nächsten Support-Levels
2. `_find_nearest_resistance_levels`: Findet die nächsten Resistance-Levels
3. `_is_price_at_key_level`: Prüft, ob der Preis nahe an einem wichtigen Level ist
4. `_detect_patterns`: Erkennt Chart-Muster
5. `_analyze_order_flow`: Analysiert den Order Flow
6. `_detect_liquidity_sweep`: Erkennt Liquidity Sweeps
7. `_calculate_stop_loss`: Berechnet den Stop-Loss
8. `_calculate_take_profit`: Berechnet den Take-Profit

Die Implementierungen dieser Methoden können aus V1/strategies/smart_money.py übernommen und an die neue Struktur angepasst werden.

### 3. Backtesting-Parameter optimieren

Nach der Implementierung der Strategie sollten die folgenden Parameter durch umfangreiche Backtests optimiert werden:

- `VOLUME_THRESHOLD`: Verschiedene Volumen-Schwellenwerte testen
- `LIQUIDITY_FACTOR`: Einfluss der Liquidität auf die Signalgenerierung anpassen
- Filter-Kombinationen: Verschiedene Kombinationen der Filter testen

### 4. Validierung der Implementierung

Die implementierte Strategie sollte durch folgende Tests validiert werden:

1. Einfacher Backtest mit Standardparametern
2. Parameter-Sweep zur Optimierung
3. Filter-Aktivierungsstudie
4. Komplette Analyse mit verschiedenen Symbolen und Zeitrahmen

## Zeitplan
- Implementierung der Kernlogik: 1-2 Tage
- Implementierung der Hilfsmethoden: 2-3 Tage
- Backtesting und Optimierung: 2-3 Tage
- Validierung und Feinabstimmung: 1-2 Tage

## Erfolgskriterien
- Win-Rate > 55%
- Profit-Faktor > 1.5
- Sharpe Ratio > 1.0
- Max. Drawdown < 15%
- Jährliche Rendite > 25%
