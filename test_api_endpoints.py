#!/usr/bin/env python3
"""
API Endpoint Tester for Dashboard Fix
Tests Bybit API endpoints to diagnose price fetching issues
"""

import requests
import json
from datetime import datetime

def test_bybit_testnet():
    """Test Bybit Testnet API"""
    print("🧪 Testing Bybit Testnet API...")
    print("-" * 40)
    
    try:
        url = "https://api-testnet.bybit.com/v5/market/ticker"
        params = {
            'category': 'spot',
            'symbol': 'BTCUSDT'
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response Keys: {list(data.keys())}")
            print(f"Return Code: {data.get('retCode')}")
            print(f"Return Message: {data.get('retMsg')}")
            
            if data.get('retCode') == 0 and 'result' in data:
                result = data['result']
                print(f"Result Keys: {list(result.keys())}")
                
                ticker_list = result.get('list', [])
                print(f"Ticker Count: {len(ticker_list)}")
                
                if ticker_list:
                    ticker = ticker_list[0]
                    print("First Ticker Data:")
                    for key, value in ticker.items():
                        print(f"  {key}: {value}")
                    
                    price = ticker.get('lastPrice', 'N/A')
                    print(f"\n✅ TESTNET BTC PRICE: ${price}")
                    return True, float(price) if price != 'N/A' else 0
                else:
                    print("❌ No ticker data found")
                    return False, 0