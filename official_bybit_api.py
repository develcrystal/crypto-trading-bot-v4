#!/usr/bin/env python
"""
OFFIZIELLE BYBIT V5 API IMPLEMENTIERUNG
Basierend auf dem exakten Code aus bybit-exchange/api-usage-examples
"""

import requests
import time
import hashlib
import hmac
import os
from dotenv import load_dotenv

# Environment laden
load_dotenv()

# Offizielle Bybit API Configuration
api_key = os.getenv('BYBIT_API_KEY')
secret_key = os.getenv('BYBIT_API_SECRET')
httpClient = requests.Session()
recv_window = str(5000)
url = "https://api-testnet.bybit.com"  # Testnet endpoint

def HTTP_Request(endPoint, method, payload, Info):
    """Offizielle Bybit HTTP Request Funktion"""
    global time_stamp
    time_stamp = str(int(time.time() * 10 ** 3))
    signature = genSignature(payload)
    headers = {
        'X-BAPI-API-KEY': api_key,
        'X-BAPI-SIGN': signature,
        'X-BAPI-SIGN-TYPE': '2',
        'X-BAPI-TIMESTAMP': time_stamp,
        'X-BAPI-RECV-WINDOW': recv_window,
        'Content-Type': 'application/json'
    }
    if(method == "POST"):
        response = httpClient.request(method, url + endPoint, headers=headers, data=payload)
    else:
        response = httpClient.request(method, url + endPoint + "?" + payload, headers=headers)
    
    print(f"\n{Info}:")
    print(f"Response Status: {response.status_code}")
    print(f"Response: {response.text}")
    print(f"Headers: {dict(response.headers)}")
    print(f"Elapsed Time: {response.elapsed}")
    
    return response.json() if response.status_code == 200 else None

def genSignature(payload):
    """Offizielle Bybit Signature Generation"""
    param_str = str(time_stamp) + api_key + recv_window + payload
    hash = hmac.new(bytes(secret_key, "utf-8"), param_str.encode("utf-8"), hashlib.sha256)
    signature = hash.hexdigest()
    print(f"Signature String: '{param_str}'")
    print(f"Generated Signature: {signature}")
    return signature

def test_official_api():
    """Test mit der offiziellen Bybit Implementierung"""
    print("OFFICIAL BYBIT V5 API TEST")
    print("=" * 50)
    print(f"API Key: {api_key}")
    print(f"Secret Key: {secret_key[:8]}...")
    print(f"Endpoint: {url}")
    
    # Test 1: Get Account Balance (wie im offiziellen Beispiel)
    print("\nTesting Account Balance (Official Implementation)...")
    payload = "accountType=UNIFIED"
    result = HTTP_Request("/v5/account/wallet-balance", "GET", payload, "Account Balance")
    
    if result and result.get('retCode') == 0:
        print("\n[SUCCESS] Account Balance Retrieved!")
        accounts = result.get('result', {}).get('list', [])
        for account in accounts:
            coins = account.get('coin', [])
            for coin in coins:
                balance = float(coin.get('walletBalance', 0))
                if balance > 0:
                    print(f"  {coin.get('coin')}: {balance}")
    else:
        print("\n[FAILED] Account Balance Failed")
        if result:
            print(f"Error: {result.get('retMsg', 'Unknown error')}")
    
    # Test 2: Get Server Time (Public API)
    print("\nTesting Server Time...")
    try:
        server_response = requests.get(f"{url}/v5/market/time")
        if server_response.status_code == 200:
            server_data = server_response.json()
            print(f"Server Time: {server_data}")
        else:
            print(f"Server Time Failed: {server_response.text}")
    except Exception as e:
        print(f"Server Time Error: {e}")

if __name__ == "__main__":
    if not api_key or not secret_key:
        print("ERROR: API Key and Secret must be set in .env file")
        exit(1)
    
    test_official_api()
