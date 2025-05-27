class Config:
    # Bybit API Configuration
    BYBIT_API_KEY = "8oOSGgMwmw0Jp5P9at"
    BYBIT_API_SECRET = "C6KoXzH7IzyXehoADScSkzk686ekobeNBfsU"
    
    # Trading Parameters
    SYMBOL = "BTCUSDT"
    TIMEFRAME = "5m"
    
    # Risk Management Parameters
    RISK_PER_TRADE = 0.01
    STOP_LOSS_MULTIPLIER = 2
    TAKE_PROFIT_MULTIPLIER = 3
    
    # Smart Money Strategy Filter Configuration - OPTIMIERT NACH FILTER-AKTIVIERUNGSSTUDIE
    # 🏆 SIEGER-KONFIGURATION (20.05.2025): Volumen + Key Levels + Pattern @ 100k Volumen
    # Performance: $4.595 Profit, 77.5% Win Rate, 27 Trades
    USE_VOLUME_FILTER = True  # ✅ Aktiviert - Basis-Filter
    VOLUME_THRESHOLD = 100000  # ✅ Optimiert - 100k Volumen-Schwelle
    USE_KEY_LEVELS = True  # ✅ Aktiviert - Verbessert Signalqualität
    USE_PATTERN_RECOGNITION = True  # ✅ Aktiviert - Maximiert Profit
    USE_ORDER_FLOW = False  # ❌ Deaktiviert - Für optimale Balance
    USE_LIQUIDITY_SWEEP = False  # ❌ Deaktiviert - Für optimale Balance
    
    # Alternative Konfigurationen (auskommentiert):
    # Für höhere Aktivität: VOLUME_THRESHOLD = 50000
    # Für maximale Präzision: USE_ORDER_FLOW = True, USE_LIQUIDITY_SWEEP = True
    
    # Technische Indikator-Parameter
    RSI_PERIOD = 14
    RSI_OVERBOUGHT = 70
    RSI_OVERSOLD = 30
    MACD_FAST = 9
    MACD_SLOW = 21
    MACD_SIGNAL = 9
    ATR_PERIOD = 14
    VOLATILITY_THRESHOLD = 0.03
    SR_LOOKBACK = 14
    
    # Smart Money spezifische Parameter
    LIQUIDITY_FACTOR = 1.0
    MIN_LIQUIDITY_THRESHOLD = 1000
    SESSION_MULTIPLIER = {
        'asian': 0.8,
        'london': 1.2,
        'new_york': 1.5
    }
    
    # Risk Reward Verhältnis
    RISK_REWARD_RATIO = 1.5
    POSITION_SIZE = 0.01
    RISK_PERCENTAGE = 2.0  # 2% Risiko pro Trade
    
    # Stop-Loss und Take-Profit Parameter
    STOP_LOSS_BUFFER = 0.001  # 0.1% Buffer
    STOP_LOSS_ATR_MULTIPLIER = 1.5
    DEFAULT_STOP_LOSS_PERCENT = 0.01  # 1% Default Stop-Loss

config = Config()
