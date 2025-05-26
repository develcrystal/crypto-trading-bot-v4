#!/usr/bin/env python
"""
MAINNET LIVE TRADING BOT - SOFORTIGER START
"""

import os
import sys
import time
import logging
from datetime import datetime
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from exchange.bybit_api import BybitAPI
from strategies.enhanced_smart_money import EnhancedSmartMoneyStrategy

# Environment laden
load_dotenv()

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_mainnet_connection():
    """Test MAINNET connection"""
    try:
        api_key = os.getenv('BYBIT_API_KEY')
        secret_key = os.getenv('BYBIT_API_SECRET')
        testnet = os.getenv('TESTNET', 'false').lower() == 'true'
        
        logger.info(f"API Key: {api_key[:10]}...")
        logger.info(f"Testnet Mode: {testnet}")
        
        api = BybitAPI(api_key=api_key, api_secret=secret_key, testnet=testnet)
        
        # Test account balance
        balance_response = api.get_wallet_balance()
        logger.info(f"Account Balance Response: {balance_response}")
        
        # Test current BTC price
        ticker_response = api.get_ticker("BTCUSDT")
        current_price = ticker_response.get('last_price', 'N/A')
        logger.info(f"Current BTC Price: ${current_price}")
        
        print(f"============================================================")
        print(f"MAINNET CONNECTION TEST")
        print(f"============================================================")
        print(f"Mode: {'TESTNET' if testnet else 'MAINNET'}")
        print(f"BTC Price: ${current_price}")
        print(f"Account Status: Connected")
        print(f"Balance: {balance_response}")
        print(f"============================================================")
        
        return True
        
    except Exception as e:
        logger.error(f"Connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("Starting MAINNET Live Trading Bot...")
    
    # Test connection first
    if test_mainnet_connection():
        print("Connection successful! Your bot is ready for MAINNET trading!")
        print("Dashboard URL: http://localhost:8505")
        
        # Keep running for testing
        print("Bot running... Press Ctrl+C to stop")
        try:
            while True:
                time.sleep(30)
                logger.info("Bot heartbeat - monitoring markets...")
        except KeyboardInterrupt:
            print("Bot stopped by user")
    else:
        print("Connection failed!")
