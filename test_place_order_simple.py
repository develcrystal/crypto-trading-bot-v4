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
        
        api_client = BybitAPI(api_key=api_key, api_secret=secret_key, testnet=testnet)
        order_response = api_client.place_order(
            symbol="BTCUSDT",
            side="Buy",
            order_type="Market",
            qty=0.01
        )
        if order_response['success']:
            print(f"Manual buy order executed: {order_response['result']}")
        else:
            print(f"Failed to execute buy order: {order_response['error']}")
    except Exception as e:
        print(f"Error placing buy order: {str(e)}")

if __name__ == "__main__":
    test_place_order()