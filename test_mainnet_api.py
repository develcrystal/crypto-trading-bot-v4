#!/usr/bin/env python
"""
BYBIT MAINNET API TEST
Testet die Verbindung zu deinem echten Bybit Account
"""

import os
import sys
import requests
import hashlib
import hmac
import time
from datetime import datetime
from dotenv import load_dotenv

# Load your API credentials
load_dotenv()

def test_bybit_mainnet_connection():
    """Testet Verbindung zu deinem Bybit Mainnet Account"""
    
    api_key = os.getenv('BYBIT_API_KEY')
    api_secret = os.getenv('BYBIT_API_SECRET')
    testnet = os.getenv('TESTNET', 'false').lower() == 'true'
    
    print("=" * 60)
    print("BYBIT MAINNET API CONNECTION TEST")
    print("=" * 60)
    print(f"API Key: {api_key[:8] if api_key else 'MISSING'}...")
    print(f"API Secret: {api_secret[:8] if api_secret else 'MISSING'}...")
    print(f"Testnet Mode: {testnet}")
    
    if testnet:
        base_url = "https://api-testnet.bybit.com"
        print("WARNING: Noch im TESTNET-Modus!")
    else:
        base_url = "https://api.bybit.com"
        print("MAINNET-Modus: ECHTES TRADING AKTIV!")
    
    print("=" * 60)
    
    if not api_key or not api_secret:
        print("FEHLER: API Credentials fehlen!")
        return False
    
    # Test 1: Public Market Data
    print("\nTEST 1: Market Data (Public)")
    try:
        url = f"{base_url}/v5/market/tickers"
        params = {'category': 'spot', 'symbol': 'BTCUSDT'}
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('retCode') == 0:
                ticker = data['result']['list'][0]
                price = float(ticker['lastPrice'])
                change = float(ticker['price24hPcnt']) * 100
                print(f"SUCCESS: BTC Price: ${price:,.0f} ({change:+.2f}%)")
            else:
                print(f"API Error: {data.get('retMsg')}")
                return False
        else:
            print(f"HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Connection Error: {e}")
        return False
    
    # Test 2: Account Balance
    print("\nTEST 2: Account Balance (Private)")
    try:
        timestamp = str(int(time.time() * 1000))
        recv_window = "5000"
        
        # Generiere Signatur für V5 API
        param_str = f"{timestamp}{api_key}{recv_window}accountType=UNIFIED"
        signature = hmac.new(
            api_secret.encode('utf-8'),
            param_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        headers = {
            'X-BAPI-API-KEY': api_key,
            'X-BAPI-SIGN': signature,
            'X-BAPI-SIGN-TYPE': '2',
            'X-BAPI-TIMESTAMP': timestamp,
            'X-BAPI-RECV-WINDOW': recv_window,
            'Content-Type': 'application/json'
        }
        
        url = f"{base_url}/v5/account/wallet-balance"
        params = {'accountType': 'UNIFIED'}
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Text: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"API Response: {data}")
            
            if data.get('retCode') == 0:
                accounts = data['result']['list']
                if accounts:
                    coins = accounts[0]['coin']
                    usdt_balance = next((coin for coin in coins if coin['coin'] == 'USDT'), None)
                    
                    if usdt_balance:
                        balance = float(usdt_balance['walletBalance'])
                        available_str = usdt_balance.get('availableToWithdraw', '0')
                        available = float(available_str) if available_str else balance
                        print(f"SUCCESS: USDT Balance: ${balance:.2f}")
                        print(f"Available: ${available:.2f}")
                        
                        if balance >= 50:
                            print("READY: Genug Balance fuer 50 EUR Trading!")
                        else:
                            print("WARNING: Balance unter 50 USD!")
                    else:
                        print("No USDT balance found")
                else:
                    print("No account data found")
            else:
                print(f"API Auth Error: {data.get('retMsg')} (Code: {data.get('retCode')})")
                return False
        else:
            print(f"HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Auth Error: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED - READY FOR LIVE TRADING!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = test_bybit_mainnet_connection()
    
    if success:
        print("\nNext Steps:")
        print("1. python enhanced_live_bot.py")
        print("2. streamlit run monitoring/bybit_focused_dashboard.py")
        print("\nReady to trade with real money!")
    else:
        print("\nPlease fix API issues before live trading!")
    
    input("\nPress Enter to exit...")
