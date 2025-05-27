# 💰 50€ MAINNET DEPLOYMENT KONFIGURATION
# Diese Datei enthält optimierte Parameter für das 50€ Mainnet Deployment

# ===========================================================
# RISIKOMANAGEMENT FÜR 50€ KAPITAL
# ===========================================================

# Risiko pro Trade: 2% von 50€ = 1€
RISK_PERCENTAGE = 2.0

# Maximaler Drawdown: 15% von 50€ = 7.5€
MAX_DRAWDOWN = 15.0

# Position Size für kleine BTC-Trades
POSITION_SIZE = 0.0001

# Minimum Trade Size in USDT
MIN_TRADE_SIZE = 5.0

# Maximum offene Positionen gleichzeitig
MAX_CONCURRENT_TRADES = 2

# Tägliches Risikolimit (10% von 50€ = 5€)
DAILY_RISK_LIMIT = 5.0

# ===========================================================
# SMART MONEY STRATEGIE PARAMETER
# ===========================================================

# Standard Smart Money Parameter
LIQUIDITY_FACTOR = 1.0
MIN_LIQUIDITY_THRESHOLD = 1000

# Session-Multiplikatoren
SESSION_MULTIPLIER_ASIAN = 0.8
SESSION_MULTIPLIER_LONDON = 1.2
SESSION_MULTIPLIER_NEW_YORK = 1.5

# Volumen-Schwelle (optimiert durch Backtests)
VOLUME_THRESHOLD = 100000

# ===========================================================
# REGIME-SPEZIFISCHE PARAMETER
# ===========================================================

# Bull Market Parameter
BULL_VOLUME_THRESHOLD_MULTIPLIER = 0.8  # 20% weniger restriktiv
BULL_RISK_REWARD_MULTIPLIER = 1.2       # 20% höhere Targets

# Bear Market Parameter
BEAR_VOLUME_THRESHOLD_MULTIPLIER = 1.2  # 20% restriktiver
BEAR_RISK_REWARD_MULTIPLIER = 0.9       # 10% konservativer

# Sideways Market Parameter
SIDEWAYS_VOLUME_THRESHOLD_MULTIPLIER = 1.5  # 50% sehr selektiv
SIDEWAYS_RISK_REWARD_MULTIPLIER = 1.0       # Standard Targets

# ===========================================================
# HINWEIS: Diese Konfiguration ist speziell für das 50€
# Mainnet Deployment optimiert und balanciert Risiko mit
# Performance für ein optimales Lernerlebnis mit echtem Geld.
# ===========================================================