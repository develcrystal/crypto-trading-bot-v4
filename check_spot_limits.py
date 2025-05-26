import os
from dotenv import load_dotenv
from exchange.bybit_api import BybitAPI
import requests

# Load .env file
load_dotenv()

def test_instrument_info():
    """Test um die aktuellen BTCUSDT Spot Trading Limits zu ermitteln"""
    try:
        api_key = os.getenv('BYBIT_API_KEY')
        secret_key = os.getenv('BYBIT_API_SECRET')
        testnet = os.getenv('TESTNET', 'true').lower() == 'true'
        
        print(f"Checking BTCUSDT Spot Trading Limits on {'TESTNET' if testnet else 'MAINNET'}")
        
        api_client = BybitAPI(api_key=api_key, api_secret=secret_key, testnet=testnet)
        
        # Query instrument info for BTCUSDT spot
        url = f"{api_client.base_url}/v5/market/instruments-info"
        params = {
            "category": "spot",
            "symbol": "BTCUSDT"
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        print(f"Raw Response: {data}")
        
        if data.get('retCode') == 0:
            instruments = data.get('result', {}).get('list', [])
            if instruments:
                instrument = instruments[0]
                print(f"\nBTCUSDT Spot Trading Info:")
                print(f"Symbol: {instrument.get('symbol')}")
                
                lot_filter = instrument.get('lotSizeFilter', {})
                print(f"Min Order Qty: {lot_filter.get('minOrderQty', 'N/A')}")
                print(f"Max Order Qty: {lot_filter.get('maxOrderQty', 'N/A')}")
                print(f"Qty Step: {lot_filter.get('qtyStep', 'N/A')}")
                print(f"Min Order Value: {lot_filter.get('minOrderAmt', 'N/A')}")
                print(f"Max Order Value: {lot_filter.get('maxOrderAmt', 'N/A')}")
                
                # Extract specific values for trading
                min_qty = float(lot_filter.get('minOrderQty', '0'))
                min_value = float(lot_filter.get('minOrderAmt', '0'))
                
                print(f"\nTRADING LIMITS:")
                print(f"   Minimum Quantity: {min_qty} BTC")
                print(f"   Minimum Value: {min_value} USDT")
                
                return min_qty, min_value
            else:
                print("No instrument data found")
                return None, None
        else:
            print(f"API Error: {data}")
            return None, None
            
    except Exception as e:
        print(f"Exception: {str(e)}")
        return None, None

if __name__ == "__main__":
    min_qty, min_value = test_instrument_info()
    if min_qty and min_value:
        print(f"\nSUCCESS! Current BTC price ~$100k means minimum order = max({min_qty} BTC, ${min_value} USDT)")
        current_btc_price = 100000  # Approximate
        min_btc_value = min_qty * current_btc_price
        effective_minimum = max(min_btc_value, min_value)
        print(f"Effective minimum order value: ${effective_minimum:.2f} USDT")
