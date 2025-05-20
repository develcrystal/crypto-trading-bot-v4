"""
Konfigurationsdatei für den Crypto Trading Bot V2.

Diese Datei enthält alle Konfigurationseinstellungen für den Bot, aufgeteilt in
verschiedene Kategorien wie API, Trading-Parameter, Risikomanagement, etc.
"""

import os
from datetime import datetime
from dotenv import load_dotenv

# Lade Umgebungsvariablen aus .env-Datei
load_dotenv()

# Standardmäßige Konfiguration
config = {
    # API Konfiguration
    'API_KEY': os.getenv('BYBIT_API_KEY', ''),
    'API_SECRET': os.getenv('BYBIT_API_SECRET', ''),
    'USE_TESTNET': os.getenv('TESTNET', 'true').lower() == 'true',
    'USE_EXCHANGE_API': True,
    
    # API URLs
    'REST_URL': 'https://api-testnet.bybit.com' if os.getenv('TESTNET', 'true').lower() == 'true' else 'https://api.bybit.com',
    'WS_URL': 'wss://stream-testnet.bybit.com' if os.getenv('TESTNET', 'true').lower() == 'true' else 'wss://stream.bybit.com',
    
    # Trading Parameter
    'SYMBOL': 'BTCUSDT',
    'TIMEFRAME': '5m',  # 5-Minuten-Zeitrahmen für die Optimierung
    'DEFAULT_QUANTITY': 0.01,
    'LEVERAGE': 10,
    'COMMISSION': 0.075/100,  # 0.075% Maker/Taker Fee
    'SLIPPAGE': 0.05/100,     # 0.05% geschätzte Slippage
    
    # Risikomanagement
    'RISK_PERCENTAGE': 2.0,    # Risiko pro Trade in %
    'MAX_DRAWDOWN': 10.0,      # Maximaler Drawdown in %
    'RISK_REWARD_RATIO': 1.5,  # Minimales Risiko/Ertrags-Verhältnis
    'MAX_CONCURRENT_TRADES': 3,# Maximale offene Positionen
    'POSITION_SIZE': 0.01,     # Basis-Positionsgröße
    'MIN_POSITION_SIZE': 0.001,
    'MAX_POSITION_SIZE': 0.1,
    'DAILY_RISK_LIMIT': 10.0,  # Maximaler täglicher Risikoprozentsatz
    
    # Smart Money Strategie Parameter
    'LIQUIDITY_FACTOR': 1.0,
    'SESSION_MULTIPLIER': {
        'asian': 0.8,
        'london': 1.2,
        'new_york': 1.5
    },
    'VOLUME_THRESHOLD': 10000,  # Standard-Volumenschwelle
    'MIN_LIQUIDITY_THRESHOLD': 1000,
    'MIN_PORTFOLIO_VALUE': 500,
    'MAX_PORTFOLIO_VALUE': 1000000,
    
    # Technische Indikatoren
    'RSI_PERIOD': 14,
    'RSI_OVERSOLD': 35,
    'RSI_OVERBOUGHT': 65,
    'MACD_FAST': 9,
    'MACD_SLOW': 21,
    'MACD_SIGNAL': 9,
    'ATR_PERIOD': 14,
    'VOLATILITY_THRESHOLD': 0.03,
    'SR_LOOKBACK': 14,
    
    # Daten Parameter
    'MAX_CANDLES': 1000,
    'DATA_LIMIT': 500,
    'MIN_DATA_POINTS': 30,
    
    # Backtest Parameter
    'INITIAL_BALANCE': 10000,  # USD
    'START_DATE': (datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).timestamp() - (30 * 24 * 60 * 60)) * 1000,  # 30 Tage zurück
    'END_DATE': datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).timestamp() * 1000,
    
    # Market Maker Strategie Filter
    'FILTERS': {
        'VOLUME_ONLY': {
            'active': True,
            'description': 'Nur Volumen-Filter aktiviert'
        },
        'KEY_LEVELS': {
            'active': False,
            'description': 'Volumen + Key Levels'
        },
        'PATTERN': {
            'active': False,
            'description': 'Volumen + Key Levels + Pattern'
        },
        'ORDER_FLOW': {
            'active': False,
            'description': 'Volumen + Key Levels + Pattern + Order Flow'
        },
        'LIQUIDITY_SWEEP': {
            'active': False,
            'description': 'Volumen + Key Levels + Pattern + Order Flow + Liquidity Sweep'
        }
    },
    
    # Volumen-Schwellen für Tests
    'VOLUME_THRESHOLDS': [10000, 50000, 100000, 250000, 500000, 1000000],
    
    # Debug-Modus
    'DEBUG': os.getenv('DEBUG', 'true').lower() == 'true',
    
    # Logging-Einstellungen
    'LOG_LEVEL': os.getenv('LOG_LEVEL', 'INFO'),
    'LOG_FILE': os.getenv('LOG_FILE', 'trading_bot.log'),
}

# Market Maker Strategie Aktivierungsstufen
ACTIVATION_STEPS = [
    {
        'step': 1,
        'filters': ['VOLUME_ONLY'],
        'description': 'Nur Volumen'
    },
    {
        'step': 2,
        'filters': ['VOLUME_ONLY', 'KEY_LEVELS'],
        'description': '+ Key Levels'
    },
    {
        'step': 3,
        'filters': ['VOLUME_ONLY', 'KEY_LEVELS', 'PATTERN'],
        'description': '+ Pattern'
    },
    {
        'step': 4,
        'filters': ['VOLUME_ONLY', 'KEY_LEVELS', 'PATTERN', 'ORDER_FLOW'],
        'description': '+ Order Flow'
    },
    {
        'step': 5,
        'filters': ['VOLUME_ONLY', 'KEY_LEVELS', 'PATTERN', 'ORDER_FLOW', 'LIQUIDITY_SWEEP'],
        'description': '+ Liquidity Sweep'
    }
]

# Füge Aktivierungsstufen zur Konfiguration hinzu
config['ACTIVATION_STEPS'] = ACTIVATION_STEPS

# Exportiere die Konfiguration
def get_config():
    """Gibt die aktuelle Konfiguration zurück."""
    return config

# Erlaube direkten Zugriff auf Konfigurationsparameter
def get(key, default=None):
    """Gibt den Wert für den angegebenen Konfigurationsschlüssel zurück oder den Standardwert, wenn der Schlüssel nicht existiert."""
    return config.get(key, default)

# Erlaubt das Aktualisieren der Konfiguration zur Laufzeit
def update(key, value):
    """Aktualisiert einen Konfigurationsparameter zur Laufzeit."""
    config[key] = value
    return config
