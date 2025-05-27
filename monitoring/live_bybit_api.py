#!/usr/bin/env python3
"""
🚀 LIVE BYBIT API INTEGRATION FÜR DASHBOARD
Echte Balance und Live Preise für das Dashboard
"""

# Redirect zur korrigierten API-Implementierung
from corrected_live_api import LiveBybitAPI

# Test function wird beibehalten
def test_api():
    """Testet die API-Verbindung"""
    api = LiveBybitAPI()
    
    print("Testing Live Bybit API...")
    print(f"API Base URL: {api.base_url}")
    print(f"Testnet Mode: {api.testnet}")
    
    # Test Dashboard Data
    result = api.get_dashboard_data()
    
    if result['success']:
        print("\nAPI Connection Successful!")
        print(f"Portfolio Value: ${result.get('portfolio_value', 0):.2f}")
        print(f"BTC Price: ${result.get('btc_price', 0):,.2f}")
        print(f"24h Change: {result.get('btc_change_24h', 0):+.2f}%")
        print(f"Account: {result.get('account_type', 'Unknown')}")
        
        print("\nBalances:")
        for coin, amount in result.get('balances', {}).items():
            if coin == 'USDT':
                print(f"   {coin}: {amount:.2f}")
            else:
                print(f"   {coin}: {amount:.6f}")
        
        if 'bid' in result and 'ask' in result:
            print("\nLive Ticker Data:")
            print(f"  Bid: {result.get('bid', 0):.2f}")
            print(f"  Ask: {result.get('ask', 0):.2f}")
        
        if 'order_book_bids' in result:
            print("\nOrder Book Bids (first 5):")
            for bid in result.get('order_book_bids', [])[:5]:
                print(f"  Price: {bid[0]:.2f}, Size: {bid[1]:.4f}")
            
        if 'order_book_asks' in result:
            print("\nOrder Book Asks (first 5):")
            for ask in result.get('order_book_asks', [])[:5]:
                print(f"  Price: {ask[0]:.2f}, Size: {ask[1]:.4f}")
            
        if 'kline_data' in result and not result['kline_data'].empty:
            print("\nKline Data (last 5 rows):")
            print(result['kline_data'].tail())

        if 'open_positions' in result:
            print(f"\nOpen Positions: {result['open_positions']}")
            
    else:
        print("\nAPI Connection Failed!")
        print(f"Error: {result.get('error', 'Unknown error')}")


if __name__ == "__main__":
    test_api()
