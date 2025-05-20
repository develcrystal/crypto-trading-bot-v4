"""
Verschiedene Oszillatoren für technische Analyse.
"""
import numpy as np
import pandas as pd


def relative_strength_index(data, period=14):
    """
    Berechnet den Relative Strength Index (RSI).

    :param data: Datenreihe (üblicherweise Schlusskurse)
    :param period: Zeitraum für RSI-Berechnung
    :return: RSI-Werte
    """
    delta = data.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    
    # Für fortlaufende Berechnungen nach der ersten Periode
    for i in range(period, len(delta)):
        avg_gain.iloc[i] = (avg_gain.iloc[i-1] * (period-1) + gain.iloc[i]) / period
        avg_loss.iloc[i] = (avg_loss.iloc[i-1] * (period-1) + loss.iloc[i]) / period
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi


def macd(data, fast_period=12, slow_period=26, signal_period=9):
    """
    Berechnet den Moving Average Convergence Divergence (MACD).

    :param data: Datenreihe (üblicherweise Schlusskurse)
    :param fast_period: Periode für den schnellen EMA
    :param slow_period: Periode für den langsamen EMA
    :param signal_period: Periode für den Signal-EMA
    :return: DataFrame mit MACD-Linie, Signal-Linie und Histogramm
    """
    fast_ema = data.ewm(span=fast_period, adjust=False).mean()
    slow_ema = data.ewm(span=slow_period, adjust=False).mean()
    
    macd_line = fast_ema - slow_ema
    signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
    histogram = macd_line - signal_line
    
    return pd.DataFrame({
        'macd': macd_line,
        'signal': signal_line,
        'histogram': histogram
    })


def stochastic_oscillator(high, low, close, k_period=14, d_period=3, smooth_k=3):
    """
    Berechnet den Stochastischen Oszillator (%K und %D).

    :param high: Höchstkurse
    :param low: Tiefstkurse
    :param close: Schlusskurse
    :param k_period: Periode für %K
    :param d_period: Periode für %D
    :param smooth_k: Glättungsperiode für %K
    :return: DataFrame mit %K und %D
    """
    # Berechnung von %K
    lowest_low = low.rolling(window=k_period).min()
    highest_high = high.rolling(window=k_period).max()
    
    k = 100 * ((close - lowest_low) / (highest_high - lowest_low))
    
    # Glättung von %K
    if smooth_k > 1:
        k = k.rolling(window=smooth_k).mean()
    
    # Berechnung von %D
    d = k.rolling(window=d_period).mean()
    
    return pd.DataFrame({
        'k': k,
        'd': d
    })


def average_directional_index(high, low, close, period=14):
    """
    Berechnet den Average Directional Index (ADX).

    :param high: Höchstkurse
    :param low: Tiefstkurse
    :param close: Schlusskurse
    :param period: Zeitraum für ADX-Berechnung
    :return: DataFrame mit ADX, +DI und -DI
    """
    # True Range berechnen
    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    tr = pd.DataFrame({'tr1': tr1, 'tr2': tr2, 'tr3': tr3}).max(axis=1)
    atr = tr.rolling(window=period).mean()
    
    # +DM und -DM berechnen
    up_move = high - high.shift(1)
    down_move = low.shift(1) - low
    
    plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0)
    minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0)
    
    plus_dm = pd.Series(plus_dm)
    minus_dm = pd.Series(minus_dm)
    
    # +DI und -DI berechnen
    plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
    minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)
    
    # Directional Index berechnen
    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
    
    # ADX berechnen
    adx = dx.rolling(window=period).mean()
    
    return pd.DataFrame({
        'adx': adx,
        'plus_di': plus_di,
        'minus_di': minus_di
    })


def commodity_channel_index(high, low, close, period=20):
    """
    Berechnet den Commodity Channel Index (CCI).

    :param high: Höchstkurse
    :param low: Tiefstkurse
    :param close: Schlusskurse
    :param period: Zeitraum für CCI-Berechnung
    :return: CCI-Werte
    """
    typical_price = (high + low + close) / 3
    mean_deviation = pd.Series(np.zeros(len(typical_price)))
    
    sma = typical_price.rolling(window=period).mean()
    
    # Berechnung der mittleren Abweichung
    for i in range(period-1, len(typical_price)):
        mean_deviation.iloc[i] = np.sum(np.abs(typical_price.iloc[i-period+1:i+1] - sma.iloc[i])) / period
    
    cci = (typical_price - sma) / (0.015 * mean_deviation)
    
    return cci


def williams_r(high, low, close, period=14):
    """
    Berechnet den Williams %R Oszillator.

    :param high: Höchstkurse
    :param low: Tiefstkurse
    :param close: Schlusskurse
    :param period: Zeitraum für Williams %R
    :return: Williams %R Werte
    """
    highest_high = high.rolling(window=period).max()
    lowest_low = low.rolling(window=period).min()
    
    williams_r = -100 * ((highest_high - close) / (highest_high - lowest_low))
    
    return williams_r
