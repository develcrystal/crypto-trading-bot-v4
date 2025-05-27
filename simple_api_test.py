#!/usr/bin/env python3
"""
Simple API Test für Live Bybit API
"""

import os
import requests
import hashlib
import hmac
import time
from dotenv import load_dotenv

load_dotenv()

def main():
    # API-Konfiguration
    api_key = os.getenv('BYBIT_API_KEY')
    secret_key = os.getenv('BYBIT_API_SECRET')
    testnet = os.getenv('TESTNET', 'true').lower() == 'true'
    
    base_url = "https://api-testnet.bybit.com" if testnet else "https://api.bybit.com"
    recv_window = str(5000)
    
    print(f"API Key: {api_key[:5]}...{api_key[-3:]}")
    print(f"Secret Key: {secret_key[:5]}...{secret_key[-3:]}")
    print(f"Testnet: {testnet}")
    print(f"Base URL: {base_url}")
    
    # 1. Test BTC Price
    try:
        url = f"{base_url}/v5/market/tickers"
        params = {'category': 'spot', 'symbol': 'BTCUSDT'}
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('retCode') == 0:
                ticker = data['result']['list'][0]
                print(f"\nBTC Price: ${float(ticker['lastPrice']):,.2f}")
                print(f"24h Change: {float(ticker['price24hPcnt']) * 100:+.2f}%")
                print(f"24h High: ${float(ticker['highPrice24h']):,.2f}")
                print(f"24h Low: ${float(ticker['lowPrice24h']):,.2f}")
            else:
                print(f"API Error: {data.get('retMsg', 'Unknown error')}")
        else:
            print(f"HTTP Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Price API Error: {str(e)}")
    
    # 2. Test Wallet Balance
    try:
        timestamp = str(int(time.time() * 1000))
        payload = "accountType=UNIFIED"
        
        param_str = timestamp + api_key + recv_window + payload
        signature = hmac.new(bytes(secret_key, "utf-8"), param_str.encode("utf-8"), hashlib.sha256).hexdigest()
        
        headers = {
            'X-BAPI-API-KEY': api_key,
            'X-BAPI-SIGN': signature,
            'X-BAPI-SIGN-TYPE': '2',
            'X-BAPI-TIMESTAMP': timestamp,
            'X-BAPI-RECV-WINDOW': recv_window,
            'Content-Type': 'application/json'
        }
        
        url = f"{base_url}/v5/account/wallet-balance?{payload}"
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('retCode') == 0:
                account = data['result']['list'][0]
                coins = account['coin']
                
                balances = {}
                for coin in coins:
                    balance = float(coin['walletBalance'])
                    if balance > 0:
                        balances[coin['coin']] = balance
                
                print("\nWallet Balances:")
                for coin, amount in balances.items():
                    if coin == 'USDT':
                        print(f"   {coin}: {amount:.2f}")
                    else:
                        print(f"   {coin}: {amount:.8f}")
            else:
                print(f"API Error: {data.get('retMsg', 'Unknown error')}")
        else:
            print(f"HTTP Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Balance API Error: {str(e)}")
    
    # 3. Test Spot Orders
    try:
        timestamp = str(int(time.time() * 1000))
        payload = "category=spot"
        
        param_str = timestamp + api_key + recv_window + payload
        signature = hmac.new(bytes(secret_key, "utf-8"), param_str.encode("utf-8"), hashlib.sha256).hexdigest()
        
        headers = {
            'X-BAPI-API-KEY': api_key,
            'X-BAPI-SIGN': signature,
            'X-BAPI-SIGN-TYPE': '2',
            'X-BAPI-TIMESTAMP': timestamp,
            'X-BAPI-RECV-WINDOW': recv_window,
            'Content-Type': 'application/json'
        }
        
        url = f"{base_url}/v5/order/realtime?{payload}"
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('retCode') == 0:
                orders = data['result']['list']
                
                if orders:
                    print("\nOpen Orders:")
                    for order in orders:
                        print(f"   Symbol: {order.get('symbol', 'N/A')}, Side: {order.get('side', 'N/A')}, Status: {order.get('orderStatus', 'N/A')}")
                else:
                    print("\nNo open orders found.")
            else:
                print(f"API Error: {data.get('retMsg', 'Unknown error')}")
        else:
            print(f"HTTP Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Orders API Error: {str(e)}")

if __name__ == "__main__":
    main()
