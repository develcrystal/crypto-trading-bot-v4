"""
Datenverarbeitungsmodul für den Crypto Trading Bot V2.

Dieses Modul ist verantwortlich für den Abruf, die Verarbeitung
und Speicherung von Marktdaten.
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any

# Konfiguriere Logging
logger = logging.getLogger(__name__)

class DataHandler:
    """
    Hauptklasse für die Verarbeitung von Marktdaten.
    
    Diese Klasse bietet Funktionen zum Abrufen von historischen und Echtzeit-Marktdaten,
    sowie zur Verarbeitung und Transformation dieser Daten in ein für die Analyse 
    geeignetes Format.
    """
    
    def __init__(self, exchange_api=None):
        """
        Initialisiere den DataHandler.
        
        Args:
            exchange_api: API-Instanz für den Zugriff auf Börsendaten
        """
        self.exchange_api = exchange_api
        self.cache = {}  # Cache für historische Daten
        
    def get_historical_data(self, symbol: str, timeframe: str, 
                           start_date: Union[str, datetime], 
                           end_date: Union[str, datetime] = None,
                           limit: int = 1000) -> Optional[pd.DataFrame]:
        """
        Ruft historische Daten für das angegebene Symbol und den Zeitraum ab.
        
        Args:
            symbol: Handelssymbol (z.B. "BTCUSDT")
            timeframe: Zeitrahmen der Candlesticks (z.B. "1h", "1d")
            start_date: Startdatum für historische Daten
            end_date: Enddatum für historische Daten (optional, Standard: aktuelles Datum)
            limit: Maximale Anzahl von Datenpunkten (optional, Standard: 1000)
            
        Returns:
            DataFrame mit historischen Daten oder None bei Fehler
        """
        # Datum-Strings in datetime-Objekte konvertieren
        if isinstance(start_date, (int, float)):
            # Falls start_date bereits ein Timestamp ist (in Millisekunden)
            start_dt = datetime.fromtimestamp(start_date / 1000.0) if start_date > 10**12 else datetime.fromtimestamp(start_date)
        else:
            start_dt = start_date if isinstance(start_date, datetime) else pd.to_datetime(start_date)
        
        if isinstance(end_date, (int, float)):
            # Falls end_date bereits ein Timestamp ist (in Millisekunden)
            end_dt = datetime.fromtimestamp(end_date / 1000.0) if end_date > 10**12 else datetime.fromtimestamp(end_date)
        else:
            end_dt = end_date if isinstance(end_date, datetime) else (
                pd.to_datetime(end_date) if end_date else datetime.now())
        
        logger.info(f"Verarbeitung historischer Daten für {symbol} im Zeitrahmen {timeframe}: {start_dt} bis {end_dt}")
        
        # Cache-Schlüssel erstellen
        cache_key = f"{symbol}_{timeframe}_{start_dt.strftime('%Y%m%d')}_{end_dt.strftime('%Y%m%d')}"
        
        # Prüfen, ob Daten im Cache sind
        if cache_key in self.cache:
            logger.info(f"Verwende Cache-Daten für {cache_key}")
            return self.cache[cache_key]
        
        try:
            # Daten von der Börse abrufen
            if self.exchange_api:
                logger.info(f"Rufe historische Daten ab für {symbol}, {timeframe}, "
                          f"von {start_dt} bis {end_dt}")
                
                # Timestamps für API in Millisekunden
                start_timestamp = int(start_dt.timestamp() * 1000)
                end_timestamp = int(end_dt.timestamp() * 1000)
                
                # Daten von der API abrufen
                data = self.exchange_api.get_historical_data(
                    symbol=symbol,
                    interval=timeframe,
                    start_time=start_timestamp,
                    end_time=end_timestamp,
                    limit=limit
                )
                
                # Daten verarbeiten
                df = self._process_raw_data(data)
                
                # Daten im Cache speichern
                self.cache[cache_key] = df
                
                return df
            else:
                logger.warning("Kein Exchange-API-Objekt konfiguriert")
                return self._generate_synthetic_data(symbol, timeframe, start_dt, end_dt)
        except Exception as e:
            logger.error(f"Fehler beim Abrufen historischer Daten: {e}")
            
            # Bei Fehler synthetische Daten generieren
            logger.info("Generiere synthetische Daten als Fallback")
            return self._generate_synthetic_data(symbol, timeframe, start_dt, end_dt)
    
    def _process_raw_data(self, raw_data: Any) -> pd.DataFrame:
        """
        Verarbeitet Rohdaten in ein standardisiertes DataFrame-Format.
        
        Diese Methode wandelt Rohdaten von der Börsen-API in ein standardisiertes
        pandas DataFrame mit OHLCV-Daten um.
        
        Args:
            raw_data: Rohdaten von der API
            
        Returns:
            Standardisiertes DataFrame mit OHLCV-Daten
        """
        logger.debug(f"Verarbeite Rohdaten vom Typ: {type(raw_data)}")
        
        # Fall 1: DataFrame-Eingabe
        if isinstance(raw_data, pd.DataFrame):
            logger.debug("Verarbeite DataFrame-Eingabe")
            df = raw_data.copy()
            
            # Spalten prüfen und ggf. transformieren
            required_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            # Fehlende Spalten behandeln
            if missing_columns:
                if 'timestamp' in missing_columns and isinstance(df.index, pd.DatetimeIndex):
                    # Timestamp ist der Index
                    missing_columns.remove('timestamp')
                    df = df.reset_index().rename(columns={'index': 'timestamp'})
                
                # Wenn immer noch Spalten fehlen, Fehler ausgeben
                if missing_columns:
                    logger.warning(f"Fehlende Spalten im DataFrame: {missing_columns}")
                    
                    # Füge fehlende Spalten mit Standardwerten hinzu
                    for col in missing_columns:
                        if col == 'volume':
                            df[col] = 0.0
                        else:
                            df[col] = np.nan
                    
                    # Fehlende Werte füllen
                    df = df.ffill().bfill()
            
        # Fall 2: Liste von Dictionaries
        elif isinstance(raw_data, list) and raw_data and isinstance(raw_data[0], dict):
            logger.debug("Verarbeite Liste von Dictionaries")
            df = pd.DataFrame(raw_data)
            
            # Spalten prüfen
            required_keys = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
            missing_keys = [key for key in required_keys if key not in df.columns]
            
            if missing_keys:
                logger.warning(f"Fehlende Schlüssel in Daten: {missing_keys}")
                
                # Versuche, alternative Schlüsselnamen zu finden
                key_mapping = {
                    'timestamp': ['time', 't', 'date'],
                    'open': ['o', 'Open'],
                    'high': ['h', 'High', 'max'],
                    'low': ['l', 'Low', 'min'],
                    'close': ['c', 'Close'],
                    'volume': ['v', 'vol', 'Volume']
                }
                
                # Versuche, fehlende Schlüssel zu mappen
                for missing_key in missing_keys.copy():
                    alternates = key_mapping.get(missing_key, [])
                    for alt in alternates:
                        if alt in df.columns:
                            df[missing_key] = df[alt]
                            missing_keys.remove(missing_key)
                            break
                
                # Füge Standardwerte für verbleibende fehlende Schlüssel hinzu
                for key in missing_keys:
                    if key == 'volume':
                        df[key] = 0.0
                    else:
                        df[key] = np.nan
                        
                # Fehlende Werte füllen
                df = df.ffill().bfill()
                
        # Fall 3: Liste von Listen (Bybit-Format)
        elif isinstance(raw_data, list) and raw_data and isinstance(raw_data[0], list):
            logger.debug("Verarbeite Liste von Listen")
            
            # Annahme: Daten in der Reihenfolge timestamp, open, high, low, close, volume
            columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
            
            # Überprüfen, ob genügend Spalten vorhanden sind
            if len(raw_data[0]) < len(columns):
                # Fehlende Spalten hinzufügen
                columns = columns[:len(raw_data[0])]
                logger.warning(f"Nicht genügend Spalten in Rohdaten, verwende: {columns}")
            
            df = pd.DataFrame(raw_data, columns=columns)
            
        # Fall 4: Verschachtelte Dictionary-Struktur (Bybit-Response-Format)
        elif isinstance(raw_data, dict) and 'result' in raw_data:
            logger.debug("Verarbeite verschachteltes Dictionary")
            
            if isinstance(raw_data['result'], dict) and 'list' in raw_data['result']:
                data_list = raw_data['result']['list']
                
                # Überprüfen, ob es sich um Listen oder Dictionaries handelt
                if data_list and isinstance(data_list[0], list):
                    # Liste von Listen
                    columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
                    if len(data_list[0]) < len(columns):
                        columns = columns[:len(data_list[0])]
                    
                    df = pd.DataFrame(data_list, columns=columns)
                    
                elif data_list and isinstance(data_list[0], dict):
                    # Liste von Dictionaries
                    df = pd.DataFrame(data_list)
                else:
                    logger.error(f"Unbekanntes Datenformat in 'list': {type(data_list[0]) if data_list else 'empty'}")
                    return pd.DataFrame()
            else:
                logger.error("Keine 'list' im 'result'-Schlüssel gefunden")
                return pd.DataFrame()
        else:
            logger.error(f"Nicht unterstütztes Datenformat: {type(raw_data)}")
            return pd.DataFrame()
        
        # Datentypen konvertieren
        df = self._convert_dtypes(df)
        
        # Zusätzliche Features hinzufügen
        df = self._add_features(df)
        
        return df
    
    def _convert_dtypes(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Konvertiert die Datentypen im DataFrame.
        
        Args:
            df: Eingabe-DataFrame
            
        Returns:
            DataFrame mit konvertierten Datentypen
        """
        # Kopie des DataFrames erstellen
        df = df.copy()
        
        # Timestamp konvertieren
        if 'timestamp' in df.columns:
            # Überprüfen, ob bereits ein datetime-Objekt
            if not pd.api.types.is_datetime64_any_dtype(df['timestamp']):
                try:
                    # Stichprobe für das Format
                    sample = df['timestamp'].iloc[0] if len(df) > 0 else None
                    
                    if isinstance(sample, (int, float)):
                        # Millisekunden seit Unix-Epoch
                        if sample > 1e12:  # ca. Jahr 2001 in ms
                            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                        # Sekunden seit Unix-Epoch
                        else:
                            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
                    else:
                        # String-Format
                        df['timestamp'] = pd.to_datetime(df['timestamp'])
                except Exception as e:
                    logger.error(f"Fehler bei Timestamp-Konvertierung: {e}")
                    # Synthetische Timestamps erstellen
                    df['timestamp'] = pd.date_range(
                        end=datetime.now(), 
                        periods=len(df), 
                        freq='1H'
                    )
            
            # Timestamp als Index setzen
            df.set_index('timestamp', inplace=True)
        
        # Numerische Spalten konvertieren
        numeric_cols = ['open', 'high', 'low', 'close', 'volume']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # NaN-Werte füllen
        df = df.ffill().bfill()
        
        return df
    
    def _add_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Fügt abgeleitete Features zum DataFrame hinzu.
        
        Args:
            df: Eingabe-DataFrame
            
        Returns:
            DataFrame mit zusätzlichen Features
        """
        try:
            # Prüfen, ob erforderliche Spalten vorhanden sind
            required_cols = ['open', 'high', 'low', 'close', 'volume']
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if missing_cols:
                logger.warning(f"Fehlende Spalten für Feature-Berechnung: {missing_cols}")
                return df
            
            # Preisänderungen
            df['returns'] = df['close'].pct_change()
            
            # Typischer Preis
            df['typical_price'] = (df['high'] + df['low'] + df['close']) / 3
            
            # Volatilität
            df['volatility'] = (df['high'] - df['low']) / df['close']
            
            # Volumen-Features
            if 'volume' in df.columns:
                df['volume_ma'] = df['volume'].rolling(window=20).mean()
                df['volume_ratio'] = df['volume'] / df['volume_ma']
            
            return df
        except Exception as e:
            logger.error(f"Fehler beim Hinzufügen von Features: {e}")
            return df
    
    def _generate_synthetic_data(self, symbol: str, timeframe: str, 
                               start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """
        Generiert synthetische Marktdaten für Tests.
        
        Args:
            symbol: Handelssymbol
            timeframe: Zeitrahmen
            start_date: Startdatum
            end_date: Enddatum
            
        Returns:
            DataFrame mit synthetischen Daten
        """
        logger.info(f"Generiere synthetische Daten für {symbol} von {start_date} bis {end_date}")
        
        # Zeitreihe generieren
        if timeframe == '1h':
            freq = 'H'
        elif timeframe == '4h':
            freq = '4H'
        elif timeframe == '1d':
            freq = 'D'
        else:
            logger.warning(f"Unbekannter Zeitrahmen: {timeframe}, verwende 1h")
            freq = 'H'
        
        # Datums-Index erstellen
        dates = pd.date_range(start=start_date, end=end_date, freq=freq)
        
        # Anfangspreis basierend auf Symbol
        if symbol.startswith('BTC'):
            base_price = 50000.0
        elif symbol.startswith('ETH'):
            base_price = 3000.0
        else:
            base_price = 100.0
        
        # Zufällige Preisbewegungen generieren
        np.random.seed(42)  # Für Reproduzierbarkeit
        returns = np.random.normal(0, 0.01, size=len(dates))
        log_returns = np.cumsum(returns)
        prices = base_price * np.exp(log_returns)
        
        # OHLCV-Daten erstellen
        df = pd.DataFrame(index=dates)
        df['close'] = prices
        df['open'] = prices * (1 + np.random.normal(0, 0.002, size=len(dates)))
        df['high'] = np.maximum(df['open'], df['close']) * (1 + np.abs(np.random.normal(0, 0.003, size=len(dates))))
        df['low'] = np.minimum(df['open'], df['close']) * (1 - np.abs(np.random.normal(0, 0.003, size=len(dates))))
        df['volume'] = np.random.lognormal(10, 1, size=len(dates))
        
        logger.info(f"Synthetische Daten generiert: {len(df)} Datenpunkte")
        
        # Features hinzufügen
        df = self._add_features(df)
        
        return df
    
    def get_latest_data(self, symbol: str, timeframe: str, 
                      limit: int = 100) -> Optional[pd.DataFrame]:
        """
        Ruft die neuesten Marktdaten ab.
        
        Args:
            symbol: Handelssymbol
            timeframe: Zeitrahmen
            limit: Anzahl der Datenpunkte
            
        Returns:
            DataFrame mit den neuesten Daten
        """
        try:
            # Aktuelle Zeit
            end_date = datetime.now()
            
            # Berechne Startdatum basierend auf Timeframe und Limit
            if timeframe == '1m':
                start_date = end_date - timedelta(minutes=limit)
            elif timeframe == '1h':
                start_date = end_date - timedelta(hours=limit)
            elif timeframe == '1d':
                start_date = end_date - timedelta(days=limit)
            else:
                # Fallback: Annahme Stunden
                start_date = end_date - timedelta(hours=limit)
            
            # Historische Daten für den entsprechenden Zeitraum abrufen
            return self.get_historical_data(
                symbol=symbol,
                timeframe=timeframe,
                start_date=start_date,
                end_date=end_date,
                limit=limit
            )
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der neuesten Daten: {e}")
            return None
    
    def resample_data(self, df: pd.DataFrame, new_timeframe: str) -> pd.DataFrame:
        """
        Resampled Daten in einen neuen Zeitrahmen.
        
        Args:
            df: Eingabe-DataFrame
            new_timeframe: Ziel-Zeitrahmen
            
        Returns:
            Resampled DataFrame
        """
        # Mappings für Pandas-Resampling
        timeframe_map = {
            '1m': '1min',
            '3m': '3min',
            '5m': '5min',
            '15m': '15min',
            '30m': '30min',
            '1h': '1H',
            '2h': '2H',
            '4h': '4H',
            '6h': '6H',
            '12h': '12H',
            '1d': '1D',
            '3d': '3D',
            '1w': '1W'
        }
        
        # Pandas-Resample-Frequenz ermitteln
        resample_freq = timeframe_map.get(new_timeframe)
        if not resample_freq:
            logger.error(f"Unbekannter Zeitrahmen für Resampling: {new_timeframe}")
            return df
        
        # Resample-Regeln für OHLCV-Daten
        resampled = df.resample(resample_freq).agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        })
        
        # NaN-Werte entfernen
        resampled = resampled.dropna()
        
        # Features hinzufügen
        resampled = self._add_features(resampled)
        
        return resampled
    
    def save_data(self, df: pd.DataFrame, filename: str) -> bool:
        """
        Speichert Daten in einer CSV-Datei.
        
        Args:
            df: Zu speicherndes DataFrame
            filename: Dateiname (inkl. Pfad)
            
        Returns:
            True bei Erfolg, False bei Fehler
        """
        try:
            df.to_csv(filename)
            logger.info(f"Daten gespeichert in: {filename}")
            return True
        except Exception as e:
            logger.error(f"Fehler beim Speichern der Daten: {e}")
            return False
    
    def load_data(self, filename: str) -> Optional[pd.DataFrame]:
        """
        Lädt Daten aus einer CSV-Datei.
        
        Args:
            filename: Dateiname (inkl. Pfad)
            
        Returns:
            DataFrame mit geladenen Daten oder None bei Fehler
        """
        try:
            df = pd.read_csv(filename, index_col=0, parse_dates=True)
            logger.info(f"Daten geladen aus: {filename}")
            return df
        except Exception as e:
            logger.error(f"Fehler beim Laden der Daten: {e}")
            return None

# Initialisierung des Loggers
def init_logger():
    """Initialisiert den Logger für das Datenmodul."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
