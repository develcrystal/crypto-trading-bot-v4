from indicators.oscillators import macd

def macd_strategy(data):
    macd_line, signal_line = macd(data['Close'])
    # Implement strategy logic here
    pass