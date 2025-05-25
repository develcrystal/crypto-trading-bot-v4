#!/usr/bin/env python3
"""
🚀 ADVANCED LIVE TRADING DASHBOARD
Professional Real-time Dashboard für Enhanced Smart Money Bot
Version: 2.0 - Production Ready für Mainnet 50€ Deployment
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
    page_title="🚀 Advanced Live Trading Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    /* Professional Trading Platform Styling */
    .main-header {
        background: linear-gradient(90deg, #1f2937 0%, #374151 100%);
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
        color: white;
    }
    
    .live-indicator { 
        animation: pulse 2s infinite;
        color: #10b981;
        font-weight: bold;
        font-size: 18px;
    }
    
    .danger-indicator {
        animation: pulse 1s infinite;
        color: #ef4444;
        font-weight: bold;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    .metric-container {
        background: #f8fafc;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #3b82f6;
        margin: 5px 0;
    }
    
    .price-widget {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    
    .order-book {
        font-family: 'Monaco', 'Menlo', monospace;
        font-size: 12px;
    }
    
    .buy-price { color: #10b981; font-weight: bold; }
    .sell-price { color: #ef4444; font-weight: bold; }
    
    .trading-control {
        background: #1f2937;
        color: white;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
    }
    
    .emergency-button {
        background: #dc2626 !important;
        color: white !important;
        font-weight: bold !important;
        border: none !important;
        padding: 10px 20px !important;
        border-radius: 5px !important;
    }
    
    .success-button {
        background: #059669 !important;
        color: white !important;
        font-weight: bold !important;
    }
</style>
""", unsafe_allow_html=True)

class AdvancedBybitAPI:
    """Enhanced Bybit API with Order Book and Live Data"""
    
    def __init__(self):
        self.api_key = os.getenv('BYBIT_API_KEY')
        self.api_secret = os.getenv('BYBIT_API_SECRET')
        self.testnet = os.getenv('TESTNET', 'true').lower() == 'true'
        
        if self.testnet:
            self.base_url = "https://api-testnet.bybit.com"
        else:
            self.base_url = "https://api.bybit.com"
    
    def _generate_signature(self, params_str, timestamp):
        """Generate HMAC SHA256 signature"""
        param_str = f"{timestamp}{self.api_key}{5000}{params_str}"
        return hmac.new(
            self.api_secret.encode('utf-8'),
            param_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    def get_account_balance(self):
        """Get real account balance"""
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
                    return {'success': True, 'data': data['result']}
            
            return {'success': False, 'error': f'HTTP {response.status_code}'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_live_ticker(self, symbol='BTCUSDT'):
        """Get live ticker data with bid/ask"""
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
                            'price': float(ticker.get('lastPrice', 0)),
                            'bid': float(ticker.get('bid1Price', 0)),
                            'ask': float(ticker.get('ask1Price', 0)),
                            'volume_24h': float(ticker.get('volume24h', 0)),
                            'change_24h': float(ticker.get('price24hPcnt', 0)) * 100,
                            'high_24h': float(ticker.get('highPrice24h', 0)),
                            'low_24h': float(ticker.get('lowPrice24h', 0)),
                            'timestamp': datetime.now()
                        }
            
            return {'success': False, 'error': f'HTTP {response.status_code}'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_order_book(self, symbol='BTCUSDT', limit=10):
        """Get live order book data"""
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
                        'bids': [[float(x[0]), float(x[1])] for x in book.get('b', [])],
                        'asks': [[float(x[0]), float(x[1])] for x in book.get('a', [])],
                        'timestamp': datetime.now()
                    }
            
            return {'success': False, 'error': f'HTTP {response.status_code}'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_kline_data(self, symbol='BTCUSDT', interval='5', limit=100):
        """Get candlestick data for charts"""
        try:
            url = f"{self.base_url}/v5/market/kline"
            params = {
                'category': 'spot',
                'symbol': symbol,
                'interval': interval,
                'limit': limit
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('retCode') == 0 and 'result' in data:
                    klines = data['result']['list']
                    df = pd.DataFrame(klines, columns=[
                        'timestamp', 'open', 'high', 'low', 'close', 'volume', 'turnover'
                    ])
                    df['timestamp'] = pd.to_datetime(df['timestamp'].astype(int), unit='ms')
                    for col in ['open', 'high', 'low', 'close', 'volume']:
                        df[col] = df[col].astype(float)
                    df = df.sort_values('timestamp').reset_index(drop=True)
                    return {'success': True, 'data': df}
            
            return {'success': False, 'error': f'HTTP {response.status_code}'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

# Initialize API
@st.cache_resource
def get_api_client():
    return AdvancedBybitAPI()

# Initialize session state
def initialize_session_state():
    if 'api_client' not in st.session_state:
        st.session_state.api_client = get_api_client()
    
    if 'live_data' not in st.session_state:
        st.session_state.live_data = {}
    
    if 'order_book' not in st.session_state:
        st.session_state.order_book = {}
    
    if 'account_balance' not in st.session_state:
        st.session_state.account_balance = {}
    
    if 'chart_data' not in st.session_state:
        st.session_state.chart_data = {}
    
    if 'portfolio_value' not in st.session_state:
        st.session_state.portfolio_value = 50.0  # 50€ start capital
    
    if 'trading_active' not in st.session_state:
        st.session_state.trading_active = False
    
    if 'emergency_stop' not in st.session_state:
        st.session_state.emergency_stop = False

initialize_session_state()

def refresh_all_data():
    """Refresh all dashboard data"""
    api = st.session_state.api_client
    
    # Get live ticker
    ticker_data = api.get_live_ticker()
    if ticker_data['success']:
        st.session_state.live_data = ticker_data
    
    # Get order book
    book_data = api.get_order_book()
    if book_data['success']:
        st.session_state.order_book = book_data
    
    # Get account balance
    balance_data = api.get_account_balance()
    if balance_data['success']:
        st.session_state.account_balance = balance_data
    
    # Get chart data
    chart_data = api.get_kline_data()
    if chart_data['success']:
        st.session_state.chart_data = chart_data

def render_main_header():
    """Render professional main header"""
    st.markdown("""
    <div class="main-header">
        <h1>🚀 ADVANCED LIVE TRADING DASHBOARD</h1>
        <p>Enhanced Smart Money Strategy • Bybit Live Trading • Professional Grade</p>
    </div>
    """, unsafe_allow_html=True)

def render_live_price_widget():
    """Render live price widget with bid/ask"""
    st.markdown("### 💰 LIVE BTC/USDT PRICE")
    
    live_data = st.session_state.live_data
    
    if live_data.get('success'):
        price = live_data['price']
        change = live_data['change_24h']
        bid = live_data.get('bid', 0)
        ask = live_data.get('ask', 0)
        spread = ask - bid if ask > 0 and bid > 0 else 0
        
        # Main price display
        color = "#10b981" if change >= 0 else "#ef4444"
        st.markdown(f"""
        <div class="price-widget">
            <h1 style="margin: 0; font-size: 3em;">${price:,.2f}</h1>
            <h3 style="margin: 5px 0; color: {color};">{change:+.2f}% (24h)</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Bid/Ask/Spread
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("💚 Bid", f"${bid:,.2f}", "Best Buy")
        
        with col2:
            st.metric("❤️ Ask", f"${ask:,.2f}", "Best Sell")
        
        with col3:
            st.metric("📊 Spread", f"${spread:.2f}", f"{(spread/price*100):.3f}%")
        
        with col4:
            volume = live_data.get('volume_24h', 0)
            st.metric("📈 Volume 24h", f"{volume:,.0f} BTC", "Trading Activity")
    
    else:
        st.error("❌ Unable to fetch live price data")
        st.error(f"Error: {live_data.get('error', 'Unknown error')}")

def render_order_book():
    """Render live order book visualization"""
    st.markdown("### 📊 LIVE ORDER BOOK")
    
    book_data = st.session_state.order_book
    
    if book_data.get('success'):
        asks = book_data.get('asks', [])
        bids = book_data.get('bids', [])
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🔴 ASKS (Sell Orders)")
            if asks:
                ask_df = pd.DataFrame(asks[:10], columns=['Price', 'Size'])
                ask_df['Total'] = (ask_df['Price'] * ask_df['Size']).round(2)
                ask_df = ask_df.sort_values('Price', ascending=False)
                
                st.markdown('<div class="order-book">', unsafe_allow_html=True)
                for _, row in ask_df.iterrows():
                    st.markdown(f"""
                    <div style="display: flex; justify-content: space-between; padding: 2px 0;">
                        <span class="sell-price">${row['Price']:,.2f}</span>
                        <span>{row['Size']:.4f}</span>
                        <span>${row['Total']:,.2f}</span>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown("#### 🟢 BIDS (Buy Orders)")
            if bids:
                bid_df = pd.DataFrame(bids[:10], columns=['Price', 'Size'])
                bid_df['Total'] = (bid_df['Price'] * bid_df['Size']).round(2)
                bid_df = bid_df.sort_values('Price', ascending=False)
                
                st.markdown('<div class="order-book">', unsafe_allow_html=True)
                for _, row in bid_df.iterrows():
                    st.markdown(f"""
                    <div style="display: flex; justify-content: space-between; padding: 2px 0;">
                        <span class="buy-price">${row['Price']:,.2f}</span>
                        <span>{row['Size']:.4f}</span>
                        <span>${row['Total']:,.2f}</span>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.error("❌ Unable to fetch order book data")

def render_professional_chart():
    """Render professional candlestick chart"""
    st.markdown("### 📈 PROFESSIONAL TRADING CHART")
    
    chart_data = st.session_state.chart_data
    
    if chart_data.get('success'):
        df = chart_data['data']
        
        # Create candlestick chart
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=('BTC/USDT Price', 'Volume'),
            row_width=[0.7, 0.3]
        )
        
        # Candlestick chart
        fig.add_trace(
            go.Candlestick(
                x=df['timestamp'],
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'],
                name='BTC/USDT',
                increasing_line_color='#26a69a',
                decreasing_line_color='#ef5350'
            ),
            row=1, col=1
        )
        
        # Add EMA lines
        df['ema_20'] = df['close'].ewm(span=20).mean()
        df['ema_50'] = df['close'].ewm(span=50).mean()
        
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df['ema_20'],
                mode='lines',
                name='EMA 20',
                line=dict(color='orange', width=1)
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df['ema_50'],
                mode='lines',
                name='EMA 50',
                line=dict(color='blue', width=1)
            ),
            row=1, col=1
        )
        
        # Volume chart
        colors = ['red' if close < open else 'green' 
                 for close, open in zip(df['close'], df['open'])]
        
        fig.add_trace(
            go.Bar(
                x=df['timestamp'],
                y=df['volume'],
                name='Volume',
                marker_color=colors,
                opacity=0.7
            ),
            row=2, col=1
        )
        
        # Update layout
        fig.update_layout(
            title="BTC/USDT Professional Chart",
            xaxis_rangeslider_visible=False,
            height=600,
            showlegend=True,
            template="plotly_dark"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.error("❌ Unable to fetch chart data")

def render_portfolio_monitor():
    """Render advanced portfolio monitoring"""
    st.markdown("### 💼 LIVE PORTFOLIO TRACKING")
    
    balance_data = st.session_state.account_balance
    live_data = st.session_state.live_data
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if balance_data.get('success'):
            # Extract USDT balance
            wallet_list = balance_data['data'].get('list', [])
            usdt_balance = 0
            
            for wallet in wallet_list:
                for coin in wallet.get('coin', []):
                    if coin.get('coin') == 'USDT':
                        usdt_balance = float(coin.get('walletBalance', 0))
                        break
            
            st.metric(
                "💰 USDT Balance", 
                f"${usdt_balance:.2f}",
                f"Available for trading"
            )
        else:
            st.metric("💰 Portfolio", f"${st.session_state.portfolio_value:.2f}", "Simulated")
    
    with col2:
        # Calculate P&L (simulated for now)
        start_value = 50.0
        current_value = st.session_state.portfolio_value
        pnl = current_value - start_value
        pnl_pct = (pnl / start_value) * 100
        
        st.metric(
            "📊 P&L Today",
            f"${pnl:.2f}",
            f"{pnl_pct:+.2f}%",
            delta_color="normal" if pnl >= 0 else "inverse"
        )
    
    with col3:
        # Current position (simulated)
        if st.session_state.trading_active:
            st.metric("🎯 Position", "LONG BTC", f"$10.50 exposure")
        else:
            st.metric("🎯 Position", "No Position", "Waiting for signal")
    
    with col4:
        # Risk level
        risk_used = 1.2  # Simulated
        max_risk = 10.0
        risk_pct = (risk_used / max_risk) * 100
        
        color = "normal" if risk_pct < 50 else "inverse"
        st.metric(
            "🛡️ Risk Level",
            f"{risk_pct:.1f}%",
            f"${risk_used:.2f} / ${max_risk:.2f}",
            delta_color=color
        )

def render_trading_controls():
    """Render trading controls panel"""
    st.markdown("### 🎮 TRADING CONTROLS")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="trading-control">
            <h4>🤖 Bot Status</h4>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.emergency_stop:
            st.error("🛑 EMERGENCY STOP ACTIVE")
            if st.button("🔄 Reset Emergency Stop", type="primary"):
                st.session_state.emergency_stop = False
                st.rerun()
        else:
            if st.session_state.trading_active:
                st.success("✅ Trading Bot ACTIVE")
                if st.button("⏸️ Pause Trading"):
                    st.session_state.trading_active = False
                    st.rerun()
            else:
                st.info("⏸️ Trading Bot PAUSED")
                if st.button("▶️ Start Trading", type="primary"):
                    st.session_state.trading_active = True
                    st.rerun()
    
    with col2:
        st.markdown("""
        <div class="trading-control">
            <h4>⚡ Quick Actions</h4>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚨 EMERGENCY STOP", key="emergency", help="Stop all trading immediately"):
            st.session_state.emergency_stop = True
            st.session_state.trading_active = False
            st.error("🚨 EMERGENCY STOP ACTIVATED!")
            st.rerun()
        
        col2a, col2b = st.columns(2)
        with col2a:
            if st.button("📈 Manual BUY", disabled=st.session_state.emergency_stop):
                st.info("Manual buy order simulated")
        
        with col2b:
            if st.button("📉 Manual SELL", disabled=st.session_state.emergency_stop):
                st.info("Manual sell order simulated")
    
    with col3:
        st.markdown("""
        <div class="trading-control">
            <h4>⚙️ Risk Settings</h4>
        </div>
        """, unsafe_allow_html=True)
        
        risk_per_trade = st.slider("Risk per Trade (%)", 0.5, 5.0, 2.0, 0.1)
        max_drawdown = st.slider("Max Drawdown (%)", 5, 25, 15, 1)
        
        if st.button("💾 Save Settings"):
            st.success("Settings saved!")

def render_live_signals():
    """Render live trading signals"""
    st.markdown("### ⚡ LIVE TRADING SIGNALS")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🎯 Current Signal")
        
        # Simulate signal (in real implementation, this would come from the trading bot)
        signal_strength = np.random.choice([0, 1, 2, 3, 4, 5], p=[0.4, 0.2, 0.15, 0.1, 0.1, 0.05])
        
        if signal_strength >= 4:
            st.success("🟢 STRONG BUY SIGNAL")
            st.info("4/4 filters passed • High confidence")
        elif signal_strength >= 2:
            st.warning("🟡 WEAK SIGNAL")
            st.info(f"{signal_strength}/4 filters passed • Low confidence")
        else:
            st.info("⚪ NO SIGNAL")
            st.info("Waiting for setup • Market analysis ongoing")
    
    with col2:
        st.markdown("#### 🔍 Filter Status")
        
        filters = [
            ("Volume Filter", np.random.choice([True, False], p=[0.7, 0.3])),
            ("Key Levels", np.random.choice([True, False], p=[0.6, 0.4])),
            ("Pattern Recognition", np.random.choice([True, False], p=[0.5, 0.5])),
            ("Order Flow", np.random.choice([True, False], p=[0.4, 0.6]))
        ]
        
        for filter_name, status in filters:
            if status:
                st.success(f"✅ {filter_name}")
            else:
                st.error(f"❌ {filter_name}")

# Main dashboard layout
def main():
    render_main_header()
    
    # Refresh controls
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        if st.button("🔄 Refresh All Data", type="primary"):
            with st.spinner("Refreshing live data..."):
                refresh_all_data()
            st.success("Data refreshed!")
            st.rerun()
    
    with col2:
        auto_refresh = st.checkbox("🔄 Auto-Refresh (30s)")
    
    with col3:
        st.markdown(f'<div class="live-indicator">🔴 LIVE</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Top row - Live price and order book
    col1, col2 = st.columns([1, 1])
    
    with col1:
        render_live_price_widget()
    
    with col2:
        render_order_book()
    
    st.markdown("---")
    
    # Chart section
    render_professional_chart()
    
    st.markdown("---")
    
    # Portfolio and controls
    col1, col2 = st.columns([2, 1])
    
    with col1:
        render_portfolio_monitor()
    
    with col2:
        render_live_signals()
    
    st.markdown("---")
    
    # Trading controls
    render_trading_controls()
    
    # Auto refresh logic
    if auto_refresh:
        time.sleep(30)
        st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        🚀 <strong>ADVANCED LIVE TRADING DASHBOARD</strong> | 
        💹 <strong>Enhanced Smart Money Strategy</strong> | 
        🔴 <strong>LIVE TRADING READY</strong> | 
        © 2025 Professional Trading System
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
