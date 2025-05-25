#!/usr/bin/env python3
"""
🔧 BYBIT API CONNECTION DEBUG TOOL
Direct test of Bybit API connection with your credentials
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import API module
from exchange.bybit_api import BybitAPI

def test_api_connection():
    """Test API connection step by step"""
    
    print("🔧 BYBIT API CONNECTION DEBUG")
    print("=" * 50)
    
    # Step 1: Check credentials
    print("\n1️⃣ CHECKING CREDENTIALS:")
    api_key = os.getenv('BYBIT_API_KEY')
    api_secret = os.getenv('BYBIT_API_SECRET')
    testnet = os.getenv('TESTNET', 'true').lower() == 'true'
    
    if api_key:
        print(f"   ✅ API Key found: {api_key[:8]}...")
    else:
        print("   ❌ API Key not found in .env")
        return False
        
    if api_secret:
        print(f"   ✅ API Secret found: {api_secret[:8]}...")
    else:
        print("   ❌ API Secret not found in .env")
        return False
        
    print(f"   🧪 Testnet mode: {testnet}")
    
    # Step 2: Initialize API
    print("\n2️⃣ INITIALIZING API:")
    try:
        api = BybitAPI(
            api_key=api_key,
            api_secret=api_secret,
            testnet=testnet
        )
        print("   ✅ API instance created successfully")
    except Exception as e:
        print(f"   ❌ API initialization failed: {e}")
        return False
    
    # Step 3: Test public endpoint
    print("\n3️⃣ TESTING PUBLIC ENDPOINT (No auth required):")
    try:
        ticker = api.get_ticker("BTCUSDT")
        if ticker and 'symbol' in ticker:
            print(f"   ✅ Public API working - BTC price: ${float(ticker.get('lastPrice', 0)):,.2f}")
        else:
            print(f"   ⚠️ Public API response unexpected: {ticker}")
            return False
    except Exception as e:
        print(f"   ❌ Public API failed: {e}")
        return False
    
    # Step 4: Test private endpoint
    print("\n4️⃣ TESTING PRIVATE ENDPOINT (Auth required):")
    try:
        wallet_balance = api.get_wallet_balance()
        print(f"   📊 Wallet API response: {wallet_balance}")
        
        if wallet_balance and isinstance(wallet_balance, dict):
            if 'coin' in wallet_balance and wallet_balance['coin']:
                print("   ✅ Private API working - Wallet data retrieved:")
                for coin in wallet_balance['coin']:
                    if coin['coin'] == 'USDT':
                        balance = float(coin['walletBalance'])
                        print(f"      💰 USDT Balance: ${balance:,.2f}")
                        break
            else:
                print("   ⚠️ Private API responded but no coin data found")
                print(f"      Response structure: {list(wallet_balance.keys())}")
        else:
            print(f"   ❌ Private API failed - Response: {wallet_balance}")
            return False
    except Exception as e:
        print(f"   ❌ Private API failed: {e}")
        return False
    
    # Step 5: Test order history
    print("\n5️⃣ TESTING ORDER HISTORY:")
    try:
        order_history = api.get_order_history(symbol="BTCUSDT", limit=5)
        if order_history:
            print(f"   ✅ Order history retrieved: {len(order_history)} orders")
            for i, order in enumerate(order_history[:3]):
                print(f"      📋 Order {i+1}: {order.get('side')} {order.get('qty')} @ ${order.get('price')}")
        else:
            print("   ℹ️ No order history found (normal for new account)")
    except Exception as e:
        print(f"   ❌ Order history failed: {e}")
    
    print("\n🏆 FINAL RESULT:")
    print("   ✅ API CONNECTION SUCCESSFUL!")
    print("   🔴 Ready for live dashboard integration!")
    return True

if __name__ == "__main__":
    print("🚀 Starting Bybit API Connection Test...")
    success = test_api_connection()
    
    if success:
        print("\n🎯 NEXT STEPS:")
        print("   1. Run START_LIVE_FIXED.bat for corrected dashboard")
        print("   2. Dashboard should now show live Testnet data")
        print("   3. Check sidebar for API credential verification")
    else:
        print("\n🚨 TROUBLESHOOTING NEEDED:")
        print("   1. Check .env file has correct API credentials")
        print("   2. Verify API keys are for Testnet (not Mainnet)")
        print("   3. Ensure API permissions include wallet access")
    
    input("\nPress Enter to continue...")
