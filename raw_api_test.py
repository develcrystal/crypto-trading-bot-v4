import os
import requests
import hmac
import hashlib
import time
from dotenv import load_dotenv

load_dotenv()

def raw_bybit_api_test():
    """Direkter Test der Bybit API ohne unsere Wrapper-Klasse"""
    
    api_key = os.getenv('BYBIT_API_KEY')
    api_secret = os.getenv('BYBIT_API_SECRET')
    testnet = os.getenv('TESTNET', 'false').lower() == 'true'
    
    # URL basierend auf Testnet/Mainnet
    base_url = "https://api-testnet.bybit.com" if testnet else "https://api.bybit.com"
    
    print(f"=== RAW BYBIT API TEST ===")
    print(f"API Key: {api_key[:10]}...")
    print(f"Testnet: {testnet}")
    print(f"Base URL: {base_url}")
    
    # Test 1: Public Market Data (no auth needed)
    print(f"\n=== TEST 1: Public Market Data ===")
    try:
        url = f"{base_url}/v5/market/tickers"
        params = {"category": "spot", "symbol": "BTCUSDT"}
        response = requests.get(url, params=params)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:500]}...")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data.get('retCode') == 0}")
            if data.get('result', {}).get('list'):
                ticker = data['result']['list'][0]
                print(f"BTC Price: ${ticker.get('lastPrice', 'N/A')}")
        
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Authenticated Request - Account Balance
    print(f"\n=== TEST 2: Account Balance (Auth Required) ===")
    try:
        timestamp = str(int(time.time() * 1000))
        params = {
            'api_key': api_key,
            'timestamp': timestamp,
            'accountType': 'UNIFIED'  # Try UNIFIED instead of SPOT
        }
        
        # Create signature
        param_str = '&'.join([f"{k}={v}" for k, v in sorted(params.items())])
        signature = hmac.new(
            api_secret.encode('utf-8'),
            param_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        params['sign'] = signature
        
        url = f"{base_url}/v5/account/wallet-balance"
        response = requests.get(url, params=params)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:500]}...")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    raw_bybit_api_test()
