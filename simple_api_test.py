import requests
import json

print("TESTING BYBIT API CONNECTION...")

# Test Bybit Testnet API
try:
    print("\n1. Testing Bybit Testnet API:")
    url = "https://api-testnet.bybit.com/v5/market/tickers?category=spot&symbol=BTCUSDT"
    response = requests.get(url, timeout=10)
    print(f"   Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if data.get('result') and data['result'].get('list'):
            price = data['result']['list'][0]['lastPrice']
            print(f"   SUCCESS: BTC Price: ${price}")
        else:
            print(f"   ERROR: No price data: {data}")
    else:
        print(f"   ERROR: {response.text}")
except Exception as e:
    print(f"   EXCEPTION: {e}")

# Test Bybit Mainnet API
try:
    print("\n2. Testing Bybit Mainnet API:")
    url = "https://api.bybit.com/v5/market/tickers?category=spot&symbol=BTCUSDT"
    response = requests.get(url, timeout=10)
    print(f"   Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if data.get('result') and data['result'].get('list'):
            price = data['result']['list'][0]['lastPrice']
            print(f"   SUCCESS: BTC Price: ${price}")
        else:
            print(f"   ERROR: No price data: {data}")
    else:
        print(f"   ERROR: {response.text}")
except Exception as e:
    print(f"   EXCEPTION: {e}")

print("\nAPI TEST COMPLETE")
