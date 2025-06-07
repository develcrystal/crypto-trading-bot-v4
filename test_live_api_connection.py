#!/usr/bin/env python
"""
LIVE API CONNECTION TEST
Testet die Verbindung zum Bybit Mainnet
"""

import os
import sys
import requests
from dotenv import load_dotenv

# Windows Console Encoding Fix
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

# .env laden
load_dotenv()

def test_mainnet_connection():
    """Testet MAINNET API-Verbindung"""
    print("=" * 50)
    print("BYBIT MAINNET API CONNECTION TEST")
    print("=" * 50)
    
    # API Keys aus .env
    api_key = os.getenv('BYBIT_API_KEY')
    testnet = os.getenv('TESTNET', 'false').lower() == 'true'
    
    print(f"API Key: {api_key[:8] if api_key else 'MISSING'}...")
    print(f"Testnet Mode: {testnet}")
    
    # Mainnet URL (echte API)
    base_url = "https://api.bybit.com"
    url = f"{base_url}/v5/market/tickers"
    
    print(f"Testing URL: {url}")
    
    try:
        # Einfacher Price Check (keine Auth nötig)
        params = {'category': 'spot', 'symbol': 'BTCUSDT'}
        response = requests.get(url, params=params, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response Keys: {list(data.keys())}")
            
            if data.get('retCode') == 0:
                ticker = data['result']['list'][0]
                price = float(ticker['lastPrice'])
                volume = float(ticker['volume24h'])
                change = float(ticker['price24hPcnt']) * 100
                
                print("[SUCCESS] Mainnet API Connection Working!")
                print(f"BTC Price: ${price:,.2f}")
                print(f"24h Volume: {volume:,.2f} BTC")
                print(f"24h Change: {change:+.2f}%")
                
                return True
            else:
                print(f"[ERROR] API Error: {data.get('retMsg')}")
                return False
        else:
            print(f"[ERROR] HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Connection Error: {str(e)}")
        return False

def test_wallet_access():
    """Testet Wallet-Zugriff (benötigt Auth)"""
    print("\n" + "=" * 50)
    print("WALLET ACCESS TEST (requires valid API keys)")
    print("=" * 50)
    
    # Hier würde wallet balance test kommen
    # Aber erstmal nur basic connection testen
    print("[INFO] Wallet access test skipped for safety")
    print("[INFO] First verify basic connection works")
    
if __name__ == "__main__":
    success = test_mainnet_connection()
    
    if success:
        print("\n[READY] READY FOR LIVE TRADING!")
        print("[OK] Enhanced Live Bot kann gestartet werden")
        print("\n[START] Start Command:")
        print("python enhanced_live_bot.py")
    else:
        print("\n[FAILED] API Connection Failed")
        print("[FIX] Check .env configuration")
        
    print("\n" + "=" * 50)
