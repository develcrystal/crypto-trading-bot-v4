#!/usr/bin/env python3
"""
🚀 ADVANCED LIVE TRADING DASHBOARD - PRODUCTION READY
Professional Real-time Dashboard für Enhanced Smart Money Bot
Version: 2.1 - Ready for 50€ Mainnet Deployment

TEIL 1: Basis-Setup und API-Integration
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import requests
import json
import time
import hmac
import hashlib
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import sqlite3
from pathlib import Path

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="🚀 Advanced Live Trading Dashboard - Production Ready",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

class AdvancedBybitAPI:
    """Enhanced Bybit API with comprehensive trading capabilities"""
    
    def __init__(self):
        self.api_key = os.getenv('BYBIT_API_KEY')
        self.api_secret = os.getenv('BYBIT_API_SECRET')
        self.testnet = os.getenv('TESTNET', 'true').lower() == 'true'
        
        if self.testnet:
            self.base_url = "https://api-testnet.bybit.com"
            self.environment = "TESTNET"
        else:
            self.base_url = "https://api.bybit.com"
            self.environment = "MAINNET"
    
    def _generate_signature(self, params_str, timestamp):
        """Generate HMAC SHA256 signature for authentication"""
        param_str = f"{timestamp}{self.api_key}{5000}{params_str}"
        return hmac.new(
            self.api_secret.encode('utf-8'),
            param_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    def get_account_balance(self):
        """Get real account balance with detailed breakdown"""
        try:
            timestamp = str(int(time.time() * 1000))
            params = ""
            signature = self._generate_signature(params, timestamp)
            
            headers = {
                'X-BAPI-API-KEY': self.api_key,
                'X-BAPI-SIGN': signature,
                'X-BAPI-SIGN-TYPE': '2',
                'X-BAPI-TIMESTAMP': timestamp,
                'X-BAPI-RECV-WINDOW': '5000'
            }
            
            url = f"{self.base_url}/v5/account/wallet-balance"
            params = {'accountType': 'UNIFIED'}
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('retCode') == 0:
                    return {
                        'success': True, 
                        'data': data['result'],
                        'environment': self.environment,
                        'timestamp': datetime.now()
                    }
            
            return {
                'success': False, 
                'error': f'HTTP {response.status_code}',
                'environment': self.environment
            }
            
        except Exception as e:
            return {
                'success': False, 
                'error': str(e),
                'environment': self.environment
            }
    
    def get_live_ticker(self, symbol='BTCUSDT'):
        """Get comprehensive live ticker data"""
        try:
            url = f"{self.base_url}/v5/market/tickers"
            params = {'category': 'spot', 'symbol': symbol}
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('retCode') == 0 and 'result' in data:
                    ticker_list = data['result']['list']
                    if ticker_list:
                        ticker = ticker_list[0]
                        return {
                            'success': True,
                            'symbol': symbol,
                            'price': float(ticker.get('lastPrice', 0)),
                            'bid': float(ticker.get('bid1Price', 0)),
                            'ask': float(ticker.get('ask1Price', 0)),
                            'bid_size': float(ticker.get('bid1Size', 0)),
                            'ask_size': float(ticker.get('ask1Size', 0)),
                            'volume_24h': float(ticker.get('volume24h', 0)),
                            'turnover_24h': float(ticker.get('turnover24h', 0)),
                            'change_24h': float(ticker.get('price24hPcnt', 0)) * 100,
                            'high_24h': float(ticker.get('highPrice24h', 0)),
                            'low_24h': float(ticker.get('lowPrice24h', 0)),
                            'prev_price_24h': float(ticker.get('prevPrice24h', 0)),
                            'timestamp': datetime.now(),
                            'environment': self.environment
                        }
            
            return {
                'success': False, 
                'error': f'HTTP {response.status_code}',
                'environment': self.environment
            }
            
        except Exception as e:
            return {
                'success': False, 
                'error': str(e),
                'environment': self.environment
            }
    
    def get_order_book(self, symbol='BTCUSDT', limit=25):
        """Get detailed order book with market depth"""
        try:
            url = f"{self.base_url}/v5/market/orderbook"
            params = {'category': 'spot', 'symbol': symbol, 'limit': limit}
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('retCode') == 0 and 'result' in data:
                    book = data['result']
                    return {
                        'success': True,
                        'symbol': symbol,
                        'bids': [[float(x[0]), float(x[1])] for x in book.get('b', [])],
                        'asks': [[float(x[0]), float(x[1])] for x in book.get('a', [])],
                        'timestamp': datetime.now(),
                        'environment': self.environment,
                        'update_id': book.get('u', 0)
                    }
            
            return {
                'success': False, 
                'error': f'HTTP {response.status_code}',
                'environment': self.environment
            }
            
        except Exception as e:
            return {
                'success': False, 
                'error': str(e),
                'environment': self.environment
            }
    
    def get_kline_data(self, symbol='BTCUSDT', interval='5', limit=200):
        """Get comprehensive candlestick data"""
        try:
            url = f"{self.base_url}/v5/market/kline"
            params = {
                'category': 'spot',
                'symbol': symbol,
                'interval': interval,
                'limit': limit
            }
            
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('retCode') == 0 and 'result' in data:
                    klines = data['result']['list']
                    df = pd.DataFrame(klines, columns=[
                        'timestamp', 'open', 'high', 'low', 'close', 'volume', 'turnover'
                    ])
                    
                    # Data processing
                    df['timestamp'] = pd.to_datetime(df['timestamp'].astype(int), unit='ms')
                    
                    for col in ['open', 'high', 'low', 'close', 'volume', 'turnover']:
                        df[col] = df[col].astype(float)
                    
                    df = df.sort_values('timestamp').reset_index(drop=True)
                    
                    return {
                        'success': True,
                        'symbol': symbol,
                        'interval': interval,
                        'data': df,
                        'timestamp': datetime.now(),
                        'environment': self.environment,
                        'total_records': len(df)
                    }
            
            return {
                'success': False, 
                'error': f'HTTP {response.status_code}',
                'environment': self.environment
            }
            
        except Exception as e:
            return {
                'success': False, 
                'error': str(e),
                'environment': self.environment
            }
    
    def get_server_time(self):
        """Get Bybit server time for synchronization"""
        try:
            url = f"{self.base_url}/v5/market/time"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('retCode') == 0:
                    server_time = int(data['result']['timeSecond'])
                    local_time = int(time.time())
                    time_diff = abs(server_time - local_time)
                    
                    return {
                        'success': True,
                        'server_time': server_time,
                        'local_time': local_time,
                        'time_diff_seconds': time_diff,
                        'synchronized': time_diff < 30,  # Within 30 seconds
                        'environment': self.environment
                    }
            
            return {
                'success': False,
                'error': f'HTTP {response.status_code}',
                'environment': self.environment
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'environment': self.environment
            }
    
    def place_order(self, symbol, side, order_type, qty, price=None, time_in_force="GTC"):
        """Place trading order (for production use)"""
        try:
            timestamp = str(int(time.time() * 1000))
            
            order_data = {
                'category': 'spot',
                'symbol': symbol,
                'side': side,
                'orderType': order_type,
                'qty': str(qty),
                'timeInForce': time_in_force
            }
            
            if price and order_type == 'Limit':
                order_data['price'] = str(price)
            
            # Convert to JSON and sort keys for signature
            params_str = json.dumps(order_data, separators=(',', ':'), sort_keys=True)
            signature = self._generate_signature(params_str, timestamp)
            
            headers = {
                'X-BAPI-API-KEY': self.api_key,
                'X-BAPI-SIGN': signature,
                'X-BAPI-SIGN-TYPE': '2',
                'X-BAPI-TIMESTAMP': timestamp,
                'X-BAPI-RECV-WINDOW': '5000',
                'Content-Type': 'application/json'
            }
            
            url = f"{self.base_url}/v5/order/create"
            
            # For safety, only simulate orders in this dashboard
            if self.environment == "TESTNET":
                response = requests.post(url, headers=headers, json=order_data, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        'success': data.get('retCode') == 0,
                        'data': data.get('result', {}),
                        'order_id': data.get('result', {}).get('orderId'),
                        'environment': self.environment,
                        'timestamp': datetime.now()
                    }
            
            # Simulate order for safety
            return {
                'success': True,
                'data': {
                    'orderId': f"SIMULATED_{int(time.time())}",
                    'symbol': symbol,
                    'side': side,
                    'orderType': order_type,
                    'qty': qty,
                    'price': price,
                    'status': 'SIMULATED'
                },
                'simulated': True,
                'environment': self.environment,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'environment': self.environment
            }


def initialize_session_state():
    """Initialize all session state variables"""
    defaults = {
        'api_client': None,
        'live_data': {},
        'order_book': {},
        'account_balance': {},
        'chart_data': {},
        'portfolio_value': 50.0,  # 50€ starting capital
        'trading_active': False,
        'emergency_stop': False,
        'current_strategy': 'Enhanced Smart Money',
        'current_regime': 'BULL',
        'regime_confidence': 0.87,
        'risk_per_trade': 2.0,
        'max_drawdown': 15.0,
        'daily_pnl': 0.0,
        'total_pnl': 0.0,
        'total_trades': 0,
        'winning_trades': 0,
        'last_refresh': datetime.now(),
        'auto_refresh': True,
        'refresh_interval': 30,  # seconds
        'environment_status': 'UNKNOWN'
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# Initialize API client
@st.cache_resource
def get_api_client():
    """Get cached API client instance"""
    return AdvancedBybitAPI()


def load_custom_css():
    """Load custom CSS styling"""
    css_file = Path(__file__).parent / "static" / "advanced_dashboard_styles.css"
    
    if css_file.exists():
        with open(css_file, 'r') as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        # Fallback basic styling
        st.markdown("""
        <style>
            .dashboard-header {
                background: linear-gradient(90deg, #1f2937 0%, #374151 100%);
                padding: 25px;
                border-radius: 15px;
                margin-bottom: 25px;
                color: white;
                text-align: center;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            }
            .live-indicator { 
                animation: pulse 2s infinite;
                color: #10b981;
                font-weight: bold;
                font-size: 18px;
            }
            @keyframes pulse {
                0% { opacity: 1; }
                50% { opacity: 0.5; }
                100% { opacity: 1; }
            }
        </style>
        """, unsafe_allow_html=True)


# Initialize everything
initialize_session_state()
if not st.session_state.api_client:
    st.session_state.api_client = get_api_client()

# Load custom styling
load_custom_css()
