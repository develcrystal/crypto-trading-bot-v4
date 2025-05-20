"""
Support- und Resistance-Level-Erkennungsfunktionen.
"""
import numpy as np
import pandas as pd
from scipy.signal import argrelextrema


def find_peaks_and_valleys(data, order=5):
    """
    Identifiziert lokale Maxima und Minima in den Kursdaten.

    :param data: Preisdaten (üblicherweise Schlusskurse)
    :param order: Anzahl der Punkte auf jeder Seite für Vergleiche
    :return: Indizes von Hochs und Tiefs
    """
    # Finde lokale Maxima
    highs = argrelextrema(data.values, np.greater, order=order)[0]
    
    # Finde lokale Minima
    lows = argrelextrema(data.values, np.less, order=order)[0]
    
    return highs, lows


def identify_support_resistance(high, low, close, lookback=100, min_points=2, tolerance_pct=0.02):
    """
    Identifiziert Support- und Resistance-Levels basierend auf Preisbewegungen.

    :param high: Höchstkurse
    :param low: Tiefstkurse
    :param close: Schlusskurse
    :param lookback: Anzahl der historischen Punkte, die berücksichtigt werden
    :param min_points: Minimale Anzahl an Berührungspunkten für ein gültiges Level
    :param tolerance_pct: Toleranzbereich in Prozent für Preisniveaus
    :return: Dictionary mit Support- und Resistance-Levels und deren Stärke
    """
    # Aktuelle Daten auf den Lookback-Zeitraum beschränken
    if len(close) > lookback:
        high = high[-lookback:]
        low = low[-lookback:]
        close = close[-lookback:]
    
    # Finde Hochs und Tiefs
    highs_idx, lows_idx = find_peaks_and_valleys(close)
    
    # Definiere Price-Levels anhand von Hochs und Tiefs
    resistance_levels = [high.iloc[idx] for idx in highs_idx]
    support_levels = [low.iloc[idx] for idx in lows_idx]
    
    # Gruppiere nahe beieinander liegende Levels
    tolerance = close.mean() * tolerance_pct
    
    # Gruppen für Resistance-Levels
    resistance_groups = []
    for level in resistance_levels:
        added = False
        for i, group in enumerate(resistance_groups):
            if abs(level - np.mean(group)) < tolerance:
                resistance_groups[i].append(level)
                added = True
                break
        if not added:
            resistance_groups.append([level])
    
    # Gruppen für Support-Levels
    support_groups = []
    for level in support_levels:
        added = False
        for i, group in enumerate(support_groups):
            if abs(level - np.mean(group)) < tolerance:
                support_groups[i].append(level)
                added = True
                break
        if not added:
            support_groups.append([level])
    
    # Berechne mittlere Levels und Stärke (Anzahl der Punkte)
    resistance_levels_with_strength = {
        np.mean(group): len(group) for group in resistance_groups if len(group) >= min_points
    }
    
    support_levels_with_strength = {
        np.mean(group): len(group) for group in support_groups if len(group) >= min_points
    }
    
    return {
        'resistance': resistance_levels_with_strength,
        'support': support_levels_with_strength
    }


def identify_key_levels(high, low, close, volume=None, lookback=100, min_touches=2, 
                        tolerance_pct=0.02, volume_factor=1.5):
    """
    Identifiziert wichtige Preisniveaus unter Berücksichtigung von Volumen.

    :param high: Höchstkurse
    :param low: Tiefstkurse
    :param close: Schlusskurse
    :param volume: Volumen (optional)
    :param lookback: Anzahl der historischen Punkte, die berücksichtigt werden
    :param min_touches: Minimale Anzahl an Berührungen für ein gültiges Level
    :param tolerance_pct: Toleranzbereich in Prozent für Preisniveaus
    :param volume_factor: Faktor für Volumengewichtung
    :return: Dictionary mit Key-Levels und deren Stärke
    """
    # Basis-Levels finden
    levels = identify_support_resistance(high, low, close, lookback, min_touches, tolerance_pct)
    
    # Wenn kein Volumen angegeben, verwenden wir die Anzahl der Berührungen als Stärke
    if volume is None:
        return levels
    
    # Finde durchschnittliches Volumen
    avg_volume = volume[-lookback:].mean()
    
    # Initialisiere Volumen-gewichtete Levels
    volume_weighted_levels = {
        'resistance': {},
        'support': {}
    }
    
    # Gewichte Resistance-Levels basierend auf Volumen
    for level, strength in levels['resistance'].items():
        # Finde Indizes, an denen der Preis nahe am Level ist
        close_to_level = (abs(high - level) / level < tolerance_pct)
        
        if sum(close_to_level) > 0:
            # Berechne durchschnittliches Volumen an diesen Punkten
            level_volume = volume[close_to_level].mean() if sum(close_to_level) > 0 else avg_volume
            
            # Volumengewichtete Stärke berechnen
            volume_strength = strength * (level_volume / avg_volume) if level_volume > avg_volume * volume_factor else strength
            
            volume_weighted_levels['resistance'][level] = volume_strength
    
    # Gewichte Support-Levels basierend auf Volumen
    for level, strength in levels['support'].items():
        # Finde Indizes, an denen der Preis nahe am Level ist
        close_to_level = (abs(low - level) / level < tolerance_pct)
        
        if sum(close_to_level) > 0:
            # Berechne durchschnittliches Volumen an diesen Punkten
            level_volume = volume[close_to_level].mean() if sum(close_to_level) > 0 else avg_volume
            
            # Volumengewichtete Stärke berechnen
            volume_strength = strength * (level_volume / avg_volume) if level_volume > avg_volume * volume_factor else strength
            
            volume_weighted_levels['support'][level] = volume_strength
    
    return volume_weighted_levels


def fibonacci_retracement(high, low, is_uptrend=True):
    """
    Berechnet Fibonacci-Retracement-Levels.

    :param high: Höchstkurs
    :param low: Tiefstkurs
    :param is_uptrend: True für Aufwärtstrend (Low-to-High), False für Abwärtstrend (High-to-Low)
    :return: Dictionary mit Fibonacci-Levels
    """
    diff = high - low
    
    if is_uptrend:
        levels = {
            '0.0': low,
            '0.236': low + 0.236 * diff,
            '0.382': low + 0.382 * diff,
            '0.5': low + 0.5 * diff,
            '0.618': low + 0.618 * diff,
            '0.786': low + 0.786 * diff,
            '1.0': high
        }
    else:
        levels = {
            '0.0': high,
            '0.236': high - 0.236 * diff,
            '0.382': high - 0.382 * diff,
            '0.5': high - 0.5 * diff,
            '0.618': high - 0.618 * diff,
            '0.786': high - 0.786 * diff,
            '1.0': low
        }
    
    return levels


def fibonacci_extension(start, middle, end, is_uptrend=True):
    """
    Berechnet Fibonacci-Extensions für Preisziele.

    :param start: Startpunkt der Bewegung
    :param middle: Umkehrpunkt
    :param end: Endpunkt der Bewegung
    :param is_uptrend: True für Aufwärtstrend, False für Abwärtstrend
    :return: Dictionary mit Fibonacci-Extension-Levels
    """
    if is_uptrend:
        diff = middle - start
        extensions = {
            '0.0': end,
            '1.0': end + 1.0 * diff,
            '1.272': end + 1.272 * diff,
            '1.414': end + 1.414 * diff,
            '1.618': end + 1.618 * diff,
            '2.0': end + 2.0 * diff,
            '2.618': end + 2.618 * diff
        }
    else:
        diff = start - middle
        extensions = {
            '0.0': end,
            '1.0': end - 1.0 * diff,
            '1.272': end - 1.272 * diff,
            '1.414': end - 1.414 * diff,
            '1.618': end - 1.618 * diff,
            '2.0': end - 2.0 * diff,
            '2.618': end - 2.618 * diff
        }
    
    return extensions


def pivot_points(high, low, close, method='standard'):
    """
    Berechnet verschiedene Arten von Pivot-Points.

    :param high: Höchstkurs des vorherigen Zeitraums
    :param low: Tiefstkurs des vorherigen Zeitraums
    :param close: Schlusskurs des vorherigen Zeitraums
    :param method: Methode zur Berechnung ('standard', 'fibonacci', 'woodie', 'camarilla', 'demark')
    :return: Dictionary mit Pivot-Points
    """
    if method == 'standard':
        pivot = (high + low + close) / 3
        s1 = 2 * pivot - high
        s2 = pivot - (high - low)
        s3 = low - 2 * (high - pivot)
        r1 = 2 * pivot - low
        r2 = pivot + (high - low)
        r3 = high + 2 * (pivot - low)
        
        return {
            'pivot': pivot,
            'r1': r1,
            'r2': r2,
            'r3': r3,
            's1': s1,
            's2': s2,
            's3': s3
        }
    
    elif method == 'fibonacci':
        pivot = (high + low + close) / 3
        r1 = pivot + 0.382 * (high - low)
        r2 = pivot + 0.618 * (high - low)
        r3 = pivot + 1.0 * (high - low)
        s1 = pivot - 0.382 * (high - low)
        s2 = pivot - 0.618 * (high - low)
        s3 = pivot - 1.0 * (high - low)
        
        return {
            'pivot': pivot,
            'r1': r1,
            'r2': r2,
            'r3': r3,
            's1': s1,
            's2': s2,
            's3': s3
        }
    
    elif method == 'woodie':
        pivot = (high + low + 2 * close) / 4
        r1 = 2 * pivot - low
        r2 = pivot + (high - low)
        s1 = 2 * pivot - high
        s2 = pivot - (high - low)
        
        return {
            'pivot': pivot,
            'r1': r1,
            'r2': r2,
            's1': s1,
            's2': s2
        }
    
    elif method == 'camarilla':
        pivot = (high + low + close) / 3
        r1 = close + 1.1 * (high - low) / 12
        r2 = close + 1.1 * (high - low) / 6
        r3 = close + 1.1 * (high - low) / 4
        r4 = close + 1.1 * (high - low) / 2
        s1 = close - 1.1 * (high - low) / 12
        s2 = close - 1.1 * (high - low) / 6
        s3 = close - 1.1 * (high - low) / 4
        s4 = close - 1.1 * (high - low) / 2
        
        return {
            'pivot': pivot,
            'r1': r1,
            'r2': r2,
            'r3': r3,
            'r4': r4,
            's1': s1,
            's2': s2,
            's3': s3,
            's4': s4
        }
    
    elif method == 'demark':
        x = close * 2 + high + low
        
        if close < open:
            x = close + high + low * 2
        elif close > open:
            x = close * 2 + high + low
        else:  # close == open
            x = close + high + low + close
        
        pivot = x / 4
        r1 = x / 2 - low
        s1 = x / 2 - high
        
        return {
            'pivot': pivot,
            'r1': r1,
            's1': s1
        }
    
    else:
        raise ValueError(f"Unbekannte Pivot-Point-Methode: {method}")
