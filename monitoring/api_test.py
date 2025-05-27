#!/usr/bin/env python3
"""
Simple API Test Script
"""
import os
import sys
import time
from datetime import datetime

# Ensure we can import from current directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Try to import LiveBybitAPI from corrected_live_api
try:
    from corrected_live_api import LiveBybitAPI
    print("✅ Successfully imported LiveBybitAPI from corrected_live_api")
except Exception as e:
    print(f"❌ Error importing from corrected_live_api: {str(e)}")
    sys.exit(1)

def test_api():
    """Test API connection"""
    print("\n======= Testing API Connection =======")
    
    # Create API instance
    try:
        api = LiveBybitAPI()
        print(f"✅ Created API instance")
        print(f"🔗 Base URL: {api.base_url}")
        print(f"🧪 Testnet: {api.testnet}")
    except Exception as e:
        print(f"❌ Error creating API instance: {str(e)}")
        return
    
    # Test Dashboard Data
    try:
        print("\n📊 Fetching dashboard data...")
        start_time = time.time()
        result = api.get_dashboard_data()
        elapsed = time.time() - start_time
        print(f"⏱️ API request took {elapsed:.2f} seconds")
    except Exception as e:
        print(f"❌ Error getting dashboard data: {str(e)}")
        return
    
    # Process results
    if result.get('success', False):
        print("\n✅ API CONNECTION SUCCESSFUL!")
        print(f"💰 Portfolio Value: ${result.get('portfolio_value', 0):.2f}")
        print(f"📈 BTC Price: ${result.get('btc_price', 0):,.2f}")
        print(f"📊 24h Change: {result.get('btc_change_24h', 0):+.2f}%")
        print(f"🏦 Account: {result.get('account_type', 'Unknown')}")
        
        print("\n💼 Balances:")
        for coin, amount in result.get('balances', {}).items():
            if coin == 'USDT':
                print(f"   {coin}: {amount:.2f}")
            else:
                print(f"   {coin}: {amount:.6f}")
        
        # Check for additional data
        if 'bid' in result and 'ask' in result:
            print("\n🔄 Live Ticker Data:")
            print(f"  Bid: ${result.get('bid', 0):,.2f}")
            print(f"  Ask: ${result.get('ask', 0):,.2f}")
        
        # Check order book data
        if 'order_book_bids' in result and len(result['order_book_bids']) > 0:
            print("\n📗 Order Book Bids (first 3):")
            for bid in result.get('order_book_bids', [])[:3]:
                print(f"  ${bid[0]:,.2f} - Size: {bid[1]:.4f}")
            
        if 'order_book_asks' in result and len(result['order_book_asks']) > 0:
            print("\n📕 Order Book Asks (first 3):")
            for ask in result.get('order_book_asks', [])[:3]:
                print(f"  ${ask[0]:,.2f} - Size: {ask[1]:.4f}")
        
        # Check kline data
        if 'kline_data' in result and not result['kline_data'].empty:
            print("\n🕯️ Kline Data (last 3 rows):")
            print(result['kline_data'].tail(3))

        # Check positions
        if 'open_positions' in result:
            print(f"\n📊 Open Positions: {result['open_positions']}")
        
        # Check bot status
        bot_status = result.get('bot_status', {})
        if bot_status:
            print("\n🤖 Bot Status:")
            print(f"  Running: {bot_status.get('running', False)}")
            if bot_status.get('running', False):
                print(f"  Process ID: {bot_status.get('process_id')}")
                print(f"  Uptime: {bot_status.get('uptime')}")
                print(f"  Market Regime: {bot_status.get('market_regime')}")
                print(f"  Last Signal: {bot_status.get('last_signal')}")
    else:
        print("\n❌ API CONNECTION FAILED!")
        print(f"Error: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    print(f"🚀 API Test started at {datetime.now()}")
    test_api()
    print(f"\n✅ Test completed at {datetime.now()}")
