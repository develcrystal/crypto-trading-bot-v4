"""
Modul zum Laden und Verarbeiten von Backtest-Ergebnissen.
"""

import json
import logging
import pandas as pd
from typing import Dict, Optional

logger = logging.getLogger(__name__)

def load_backtest_results(file_path: str) -> Dict:
    """
    Lädt Backtest-Ergebnisse aus einer JSON-Datei.
    
    Args:
        file_path: Pfad zur JSON-Ergebnisdatei
        
    Returns:
        Dictionary mit Backtest-Ergebnissen
    """
    try:
        with open(file_path, 'r') as f:
            results = json.load(f)
        
        # Konvertiere Zeitstempel-Strings in datetime-Objekte
        if 'trades' in results:
            for trade in results['trades']:
                trade['entry_time'] = pd.to_datetime(trade['entry_time'])
                trade['exit_time'] = pd.to_datetime(trade['exit_time'])
        
        if 'equity_curve' in results:
            for point in results['equity_curve']:
                point['timestamp'] = pd.to_datetime(point['timestamp'])
        
        if 'signals' in results:
            for signal in results['signals']:
                signal['timestamp'] = pd.to_datetime(signal['timestamp'])
        
        results['start_date'] = pd.to_datetime(results['start_date'])
        results['end_date'] = pd.to_datetime(results['end_date'])
        
        logger.info(f"Ergebnisse geladen aus: {file_path}")
        return results
    
    except Exception as e:
        logger.error(f"Fehler beim Laden der Ergebnisse: {e}")
        raise
