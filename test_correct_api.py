#!/usr/bin/env python
import os
import requests
import hmac
import hashlib
import time
from dotenv import load_dotenv

load_dotenv()

def correct_bybit_signature():
    """Korrekte Bybit V5 API Signatur-Methode"""
    api_key = os.getenv('BYBIT_API_KEY')
    api_secret = os.getenv('BYBIT_API_SECRET')
    
    print("Testing CORRECTED Bybit V5 API Authentication...")
    print(f"API Key: {api_key[:8]}...")
    
    # Korrekte V5 API Parameter-Struktur
    timestamp = str(int(time.time() * 1000))
    recv_window = "5000"
    
    # V5 API verwendet andere Header-Struktur
    headers = {
        'X-BAPI-API-KEY': api_key,
        'X-BAPI-TIMESTAMP': timestamp,
        'X-BAPI-RECV-WINDOW': recv_window
    }
    
    # Query Parameter
    query_params = 'accountType=UNIFIED'
    
    # Korrekte V5 Signatur-String: timestamp + api_key + recv_window + query_string
    param_str = timestamp + api_key + recv_window + query_params
    print(f"Signature String: {param_str}")
    
    # HMAC SHA256 Signatur
    signature = hmac.new(
        api_secret.encode('utf-8'),
        param_str.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    headers['X-BAPI-SIGN'] = signature
    
    # API Call mit korrekten Headern
    url = "https://api-testnet.bybit.com/v5/account/wallet-balance"
    params = {'accountType': 'UNIFIED'}
    
    print(f"Headers: {headers}")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        print(f"Response Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('retCode') == 0:
                print("SUCCESS: Account Balance Retrieved!")
                
                # Balance extrahieren
                result = data.get('result', {})
                accounts = result.get('list', [])
                if accounts:
                    coins = accounts[0].get('coin', [])
                    print("Your Balances:")
                    for coin in coins:
                        balance = float(coin.get('walletBalance', 0))
                        if balance > 0:
                            print(f"  {coin['coin']}: {balance}")
                return True
            else:
                print(f"API Error: {data.get('retMsg')}")
                return False
        else:
            print(f"HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Request Error: {e}")
        return False

if __name__ == "__main__":
    success = correct_bybit_signature()
    if success:
        print("\n✅ API Authentication working! Ready for live trading!")
    else:
        print("\n❌ API Authentication failed - check permissions!")
