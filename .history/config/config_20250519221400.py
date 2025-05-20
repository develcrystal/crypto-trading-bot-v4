class Config:
    # Bybit API Configuration
    BYBIT_API_KEY = "YOUR_BYBIT_API_KEY"
    BYBIT_API_SECRET = "YOUR_BYBIT_API_SECRET"
    
    # Trading Parameters
    SYMBOL = "BTCUSDT"
    TIMEFRAME = "5m"
    
    # Risk Management Parameters
    RISK_PER_TRADE = 0.01
    STOP_LOSS_MULTIPLIER = 2
    TAKE_PROFIT_MULTIPLIER = 3
    
    # Smart Money Strategy Filter Configuration
    USE_VOLUME_FILTER = False
    VOLUME_THRESHOLD = 10000
    USE_KEY_LEVELS_FILTER = False
    USE_PATTERN_FILTER = False
    USE_ORDER_FLOW_FILTER = False
    USE_LIQUIDITY_SWEEP_FILTER = False

config = Config()
