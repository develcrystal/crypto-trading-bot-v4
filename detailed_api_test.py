import os
from dotenv import load_dotenv
from exchange.bybit_api import BybitAPI

# Load .env file
load_dotenv()

def detailed_api_test():
    """Detaillierter Test der Bybit API mit vollständiger Response-Anzeige"""
    try:
        api_key = os.getenv('BYBIT_API_KEY')
        secret_key = os.getenv('BYBIT_API_SECRET')
        testnet = os.getenv('TESTNET', 'false').lower() == 'true'
        
        print(f"=== DETAILED API TEST ===")
        print(f"API Key: {api_key[:10]}...")
        print(f"Testnet Mode: {testnet}")
        print(f"Expected Mode: {'TESTNET' if testnet else 'MAINNET'}")
        
        api_client = BybitAPI(api_key=api_key, api_secret=secret_key, testnet=testnet)
        print(f"Base URL: {api_client.base_url}")
        
        # Test 1: Market Data (should work without auth)
        print(f"\n=== TEST 1: Market Data ===")
        try:
            ticker = api_client.get_ticker("BTCUSDT")
            print(f"Ticker Response: {ticker}")
        except Exception as e:
            print(f"Ticker Error: {e}")
        
        # Test 2: Account Balance (requires auth)
        print(f"\n=== TEST 2: Account Balance ===")
        try:
            balance = api_client.get_wallet_balance()
            print(f"Balance Response: {balance}")
        except Exception as e:
            print(f"Balance Error: {e}")
        
        # Test 3: Small Order Test (Minimum 5 USDT)
        print(f"\n=== TEST 3: Order Placement ===")
        print(f"Attempting to place 6 USDT order...")
        
        try:
            # Place a small test order
            order_response = api_client.place_order(
                symbol="BTCUSDT",
                side="Buy",
                order_type="Market",
                qty=6.0  # 6 USDT - über dem 5 USDT Minimum
            )
            
            print(f"Full Order Response: {order_response}")
            print(f"Order Success: {order_response.get('success', False)}")
            
            if order_response.get('success'):
                print(f"ORDER PLACED! Order ID: {order_response.get('order_id')}")
                return True
            else:
                print(f"ORDER FAILED! Error: {order_response.get('error')}")
                return False
                
        except Exception as e:
            print(f"Order Exception: {e}")
            return False
            
    except Exception as e:
        print(f"General Exception: {e}")
        return False

if __name__ == "__main__":
    success = detailed_api_test()
    print(f"\n=== FINAL RESULT ===")
    print(f"Test Result: {'SUCCESS' if success else 'FAILED'}")
