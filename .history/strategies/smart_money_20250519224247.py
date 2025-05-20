    def _calculate_base_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Berechnet Basisindikatoren für die Strategie.

        Args:
            df: Ein Pandas DataFrame mit Marktdaten.

        Returns:
            DataFrame mit Basisindikatoren.
        """
        # Überprüfen, ob genügend Daten für die Berechnung vorhanden sind
        if len(df) < max(self.rsi_period, self.macd_slow, self.atr_period):
            logging.warning(f"Nicht genügend Daten für Indikatorberechnung: {len(df)} Datenpunkte vorhanden.")
            # Füge Dummy-Werte für die Ergebnis-Spalten hinzu
            df['rsi'] = np.nan
            df['ema_fast'] = np.nan
            df['ema_slow'] = np.nan
            df['macd'] = np.nan
            df['macd_signal'] = np.nan
            df['macd_histogram'] = np.nan
            df['atr'] = np.nan
            df['volume_sma'] = np.nan
            df['above_avg_volume'] = False
            return df

        # RSI (Relative Strength Index) berechnen
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)

        avg_gain = gain.ewm(com=self.rsi_period - 1, adjust=False).mean()
        avg_loss = loss.ewm(com=self.rsi_period - 1, adjust=False).mean()

        rs = avg_gain / avg_loss.replace(0, np.finfo(float).eps)  # Vermeide Division durch Null
        df['rsi'] = 100 - (100 / (1 + rs))

        # MACD berechnen
        df['ema_fast'] = df['close'].ewm(span=self.macd_fast, adjust=False).mean()
        df['ema_slow'] = df['close'].ewm(span=self.macd_slow, adjust=False).mean()
        df['macd'] = df['ema_fast'] - df['ema_slow']
        df['macd_signal'] = df['macd'].ewm(span=self.macd_signal, adjust=False).mean()
        df['macd_histogram'] = df['macd'] - df['macd_signal']

        # Speichere vorherige Werte für Trend-Bestimmung
        df['macd_histogram_1'] = df['macd_histogram'].shift(1)

        # ATR (Average True Range) für Volatilität berechnen
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df['atr'] = tr.ewm(span=self.atr_period, adjust=False).mean()

        # Volume Profile (einfach)
        df['volume_sma'] = df['volume'].rolling(window=20).mean()
        df['above_avg_volume'] = df['volume'] > df['volume_sma']

        return df

    def _add_pattern_recognition(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Erkennt wichtige Chartmuster wie Engulfing, Dojis, etc.

        Args:
            df: Ein Pandas DataFrame mit Marktdaten.

        Returns:
            DataFrame mit erkannten Mustern.
        """
        if len(df) < 3:
            logging.warning("Nicht genügend Daten für Pattern-Erkennung.")
            # Füge Dummy-Werte für die Ergebnis-Spalten hinzu
            df['bullish_engulfing'] = False
            df['bearish_engulfing'] = False
            df['doji'] = False
            df['shooting_star'] = False
            df['hammer'] = False
            df['evening_star'] = False
            df['morning_star'] = False
            df['bullish_pattern'] = False
            df['bearish_pattern'] = False
            return df

        # Initialisierung der Muster-Spalten
        df['bullish_engulfing'] = False
        df['bearish_engulfing'] = False
        df['doji'] = False
        df['shooting_star'] = False
        df['hammer'] = False
        df['evening_star'] = False
        df['morning_star'] = False

        # Body und Schatten berechnen
        df['body'] = abs(df['close'] - df['open'])
        df['upper_shadow'] = df['high'] - df[['open', 'close']].max(axis=1)
        df['lower_shadow'] = df[['open', 'close']].min(axis=1) - df['low']
        df['body_to_range'] = df['body'] / (df['high'] - df['low']).clip(lower=0.0001)

        # 1. Bullish Engulfing Pattern
        df['bullish_engulfing'] = (
            (df['open'].shift(1) > df['close'].shift(1)) &  # Vorheriger Candle ist bearish
            (df['close'] > df['open']) &  # Aktueller Candle ist bullish
            (df['open'] <= df['close'].shift(1)) &  # Öffnung unter dem Vorgänger-Schluss
            (df['close'] > df['open'].shift(1))  # Schluss über dem Vorgänger-Öffnung
        )

        # 2. Bearish Engulfing Pattern
        df['bearish_engulfing'] = (
            (df['close'].shift(1) > df['open'].shift(1)) &  # Vorheriger Candle ist bullish
            (df['open'] > df['close']) &  # Aktueller Candle ist bearish
            (df['open'] >= df['close'].shift(1)) &  # Öffnung über dem Vorgänger-Schluss
            (df['close'] < df['open'].shift(1))  # Schluss unter dem Vorgänger-Öffnung
        )

        # 3. Doji (very small body)
        small_body_threshold = 0.1  # Body is less than 10% of the total range
        df['doji'] = df['body_to_range'] < small_body_threshold

        # 4. Shooting Star (small body at top, long upper shadow, small lower shadow)
        df['shooting_star'] = (
            (df['body_to_range'] < 0.3) &  # Kleiner Body
            (df['upper_shadow'] > df['body'] * 2) &  # Langer oberer Schatten
            (df['lower_shadow'] < df['body'])  # Kleiner unterer Schatten
        )

        # 5. Hammer (small body at bottom, long lower shadow, small upper shadow)
        df['hammer'] = (
            (df['body_to_range'] < 0.3) &  # Kleiner Body
            (df['lower_shadow'] > df['body'] * 2) &  # Langer unterer Schatten
            (df['upper_shadow'] < df['body'])  # Kleiner oberer Schatten
        )