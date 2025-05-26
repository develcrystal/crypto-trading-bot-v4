import os
from dotenv import load_dotenv
from exchange.bybit_api import BybitAPI

# Load .env file
load_dotenv()

def test_place_order():
    try:
        # Get testnet value from .env
        api_key = os.getenv('BYBIT_API_KEY')
        secret_key = os.getenv('BYBIT_API_SECRET')
        testnet = os.getenv('TESTNET', 'true').lower() == 'true'
        
        print(f"Testing Order Placement on {'TESTNET' if testnet else 'MAINNET'}")
        
        api_client = BybitAPI(api_key=api_key, api_secret=secret_key, testnet=testnet)
        
        # Bybit Spot Minimum: 5 USDT oder 0.000011 BTC
        # Test mit 10 USDT um sicher über dem Minimum zu sein
        order_response = api_client.place_order(
            symbol="BTCUSDT",
            side="Buy",
            order_type="Market",
            qty=10.0  # 10 USDT - deutlich über dem 5 USDT Minimum
        )
        
        print(f"Order Response: {order_response}")
        
        if order_response and order_response.get('success'):
            # Angepasst für korrektes Response Format
            order_id = order_response.get('order_id')
            print(f"SUCCESS! Buy order executed with Order ID: {order_id}")
            print(f"Full response: {order_response}")
            return True
        else:
            print(f"FAILED! Error: {order_response.get('error', 'Unknown error') if order_response else 'No response'}")
            print(f"Full response: {order_response}")
            return False
            
    except Exception as e:
        print(f"Exception Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_place_order()
    print(f"\n{'🎉 ECHTER TRADE ERFOLGREICH!' if success else '❌ Test FAILED!'}")
