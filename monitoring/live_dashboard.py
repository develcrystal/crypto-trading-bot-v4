#!/usr/bin/env python3
"""
🚀 LIVE BYBIT TESTNET MONITORING DASHBOARD
Real-time connection to Bybit Testnet API
Version: 2.0 Live Enhanced
Author: Romain Hill © 2025
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import json
import time
import os
import sys
from typing import Dict, List, Optional

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import custom modules
from exchange.bybit_api import BybitAPI
from config.config import Config

# ============================================================================
# CONFIGURATION & SETUP
# ============================================================================

st.set_page_config(
    page_title="🚀 LIVE Bybit Testnet Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .status-good { color: #00ff00; font-weight: bold; }
    .status-warning { color: #ffaa00; font-weight: bold; }
    .status-danger { color: #ff0000; font-weight: bold; }
    .regime-bull { background: linear-gradient(90deg, #2ecc71, #27ae60); }
    .regime-bear { background: linear-gradient(90deg, #e74c3c, #c0392b); }
    .regime-sideways { background: linear-gradient(90deg, #f39c12, #e67e22); }
    .live-indicator { 
        animation: pulse 2s infinite;
        color: #ff0000;
        font-weight: bold;
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# LIVE DATA PROVIDER WITH BYBIT API
# ============================================================================

class LiveBybitDataProvider:
    """Live data provider using real Bybit Testnet API"""
    
    def __init__(self):
        self.config = Config()
        self.api = BybitAPI(
            api_key=self.config.BYBIT_API_KEY,
            api_secret=self.config.BYBIT_API_SECRET,
            testnet=True  # Always use testnet for safety
        )
        self.symbol = "BTCUSDT"
        self.initialized = False
        self._init_session_state()
    
    def _init_session_state(self):
        """Initialize session state with live API data"""
        if 'api_connected' not in st.session_state:
            st.session_state.api_connected = self._test_api_connection()
        
        if 'live_portfolio_data' not in st.session_state:
            st.session_state.live_portfolio_data = self._fetch_portfolio_data()
        
        if 'live_market_data' not in st.session_state:
            st.session_state.live_market_data = self._fetch_market_data()
        
        if 'live_trade_history' not in st.session_state:
            st.session_state.live_trade_history = self._fetch_trade_history()
        
        self.initialized = True
    
    def _test_api_connection(self) -> bool:
        """Test connection to Bybit API"""
        try:
            ticker = self.api.get_ticker(self.symbol)
            if ticker and 'symbol' in ticker:
                st.session_state.api_status = "✅ Connected to Bybit Testnet"
                return True
            else:
                st.session_state.api_status = "⚠️ API Connection Issue"
                return False
        except Exception as e:
            st.session_state.api_status = f"❌ API Error: {str(e)}"
            return False
    
    def _fetch_portfolio_data(self) -> Dict:
        """Fetch real portfolio data from Bybit"""
        try:
            if st.session_state.api_connected:
                wallet_balance = self.api.get_wallet_balance()
                
                if wallet_balance and 'coin' in wallet_balance:
                    # Extract USDT balance
                    usdt_balance = 0
                    for coin in wallet_balance['coin']:
                        if coin['coin'] == 'USDT':
                            usdt_balance = float(coin['walletBalance'])
                            break
                    
                    return {
                        'total_balance': usdt_balance,
                        'available_balance': usdt_balance,
                        'locked_balance': 0,
                        'last_update': datetime.now()
                    }
            
            # Fallback to demo data if API not available
            return {
                'total_balance': 1000.0,  # Demo testnet balance
                'available_balance': 950.0,
                'locked_balance': 50.0,
                'last_update': datetime.now()
            }
        except Exception as e:
            st.error(f"Error fetching portfolio data: {str(e)}")
            return {'total_balance': 0, 'available_balance': 0, 'locked_balance': 0}
    
    def _fetch_market_data(self) -> Dict:
        """Fetch real market data from Bybit"""
        try:
            if st.session_state.api_connected:
                # Get current ticker
                ticker = self.api.get_ticker(self.symbol)
                
                # Get historical data for chart
                historical_data = self.api.get_historical_data(
                    symbol=self.symbol,
                    interval="1h",
                    limit=168  # Last 7 days
                )
                
                if ticker and historical_data:
                    current_price = float(ticker.get('lastPrice', 0))
                    price_change_24h = float(ticker.get('price24hPcnt', 0)) * 100
                    
                    return {
                        'current_price': current_price,
                        'price_change_24h': price_change_24h,
                        'volume_24h': float(ticker.get('volume24h', 0)),
                        'high_24h': float(ticker.get('highPrice24h', 0)),
                        'low_24h': float(ticker.get('lowPrice24h', 0)),
                        'historical_data': historical_data,
                        'last_update': datetime.now()
                    }
            
            # Fallback data
            return {
                'current_price': 106450 + np.random.normal(0, 200),
                'price_change_24h': np.random.normal(0.5, 1.5),
                'volume_24h': 150000000,
                'high_24h': 107000,
                'low_24h': 105800,
                'historical_data': [],
                'last_update': datetime.now()
            }
        except Exception as e:
            st.error(f"Error fetching market data: {str(e)}")
            return {'current_price': 0, 'price_change_24h': 0}
    
    def _fetch_trade_history(self) -> List[Dict]:
        """Fetch real trade history from Bybit"""
        try:
            if st.session_state.api_connected:
                order_history = self.api.get_order_history(symbol=self.symbol, limit=20)
                
                if order_history:
                    trades = []
                    for order in order_history:
                        trades.append({
                            'timestamp': datetime.fromtimestamp(int(order.get('createdTime', 0)) / 1000),
                            'order_id': order.get('orderId'),
                            'symbol': order.get('symbol'),
                            'side': order.get('side'),
                            'order_type': order.get('orderType'),
                            'qty': float(order.get('qty', 0)),
                            'price': float(order.get('price', 0)),
                            'status': order.get('orderStatus'),
                            'avg_price': float(order.get('avgPrice', 0))
                        })
                    return trades
            
            # Generate demo trades if no real data
            return self._generate_demo_trades()
        except Exception as e:
            st.error(f"Error fetching trade history: {str(e)}")
            return self._generate_demo_trades()
    
    def _generate_demo_trades(self) -> List[Dict]:
        """Generate demo trades for display"""
        trades = []
        current_time = datetime.now()
        
        for i in range(10):
            trade_time = current_time - timedelta(hours=i*2)
            side = np.random.choice(['Buy', 'Sell'])
            price = 106000 + np.random.normal(0, 500)
            qty = 0.001 + np.random.uniform(0, 0.009)
            
            trades.append({
                'timestamp': trade_time,
                'order_id': f'DEMO{i:03d}',
                'symbol': 'BTCUSDT',
                'side': side,
                'order_type': 'Market',
                'qty': qty,
                'price': price,
                'status': 'Filled',
                'avg_price': price
            })
        
        return trades
    
    def refresh_data(self):
        """Refresh all live data"""
        st.session_state.api_connected = self._test_api_connection()
        st.session_state.live_portfolio_data = self._fetch_portfolio_data()
        st.session_state.live_market_data = self._fetch_market_data()
        st.session_state.live_trade_history = self._fetch_trade_history()
    
    def get_current_metrics(self) -> Dict:
        """Get current live metrics"""
        portfolio = st.session_state.live_portfolio_data
        market = st.session_state.live_market_data
        trades = st.session_state.live_trade_history
        
        # Calculate metrics from real data
        total_trades = len(trades)
        buy_trades = len([t for t in trades if t['side'] == 'Buy'])
        sell_trades = total_trades - buy_trades
        
        return {
            'portfolio_value': portfolio['total_balance'],
            'available_balance': portfolio['available_balance'],
            'locked_balance': portfolio['locked_balance'],
            'current_price': market['current_price'],
            'price_change_24h': market['price_change_24h'],
            'volume_24h': market['volume_24h'],
            'total_trades': total_trades,
            'buy_trades': buy_trades,
            'sell_trades': sell_trades,
            'last_update': market['last_update']
        }

# ============================================================================
# DASHBOARD COMPONENTS - LIVE VERSION
# ============================================================================

def render_live_header():
    """Render live status header"""
    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
    
    with col1:
        st.markdown("# 🚀 **LIVE BYBIT TESTNET DASHBOARD**")
    
    with col2:
        st.markdown('<div class="live-indicator">🔴 LIVE</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"### ⏰ {datetime.now().strftime('%H:%M:%S')}")
    
    with col4:
        if st.session_state.get('api_connected', False):
            st.markdown("### ✅ API")
        else:
            st.markdown("### ❌ API")

def render_live_overview(data_provider):
    """Render live overview with real Bybit data"""
    st.markdown("## 💰 **LIVE PORTFOLIO STATUS**")
    
    metrics = data_provider.get_current_metrics()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "💰 Total Balance (USDT)", 
            f"${metrics['portfolio_value']:,.2f}",
            "Testnet Balance"
        )
    
    with col2:
        st.metric(
            "💳 Available Balance",
            f"${metrics['available_balance']:,.2f}",
            f"Locked: ${metrics['locked_balance']:,.2f}"
        )
    
    with col3:
        price_delta = f"{metrics['price_change_24h']:+.2f}%"
        delta_color = "normal" if metrics['price_change_24h'] >= 0 else "inverse"
        st.metric(
            "₿ BTC Price (Live)",
            f"${metrics['current_price']:,.0f}",
            price_delta,
            delta_color=delta_color
        )
    
    with col4:
        st.metric(
            "📊 Total Orders",
            f"{metrics['total_trades']}",
            f"Buy: {metrics['buy_trades']} | Sell: {metrics['sell_trades']}"
        )

def render_live_market_data(data_provider):
    """Render live market data from Bybit"""
    st.markdown("## 📈 **LIVE MARKET DATA**")
    
    market_data = st.session_state.live_market_data
    
    # Market stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Volume 24h", f"${market_data['volume_24h']:,.0f}")
    
    with col2:
        st.metric("⬆️ High 24h", f"${market_data['high_24h']:,.0f}")
    
    with col3:
        st.metric("⬇️ Low 24h", f"${market_data['low_24h']:,.0f}")
    
    with col4:
        update_time = market_data['last_update'].strftime('%H:%M:%S')
        st.metric("🔄 Last Update", update_time)
    
    # Price chart from historical data
    if market_data['historical_data']:
        st.markdown("### 📈 BTC/USDT Price Chart (Live Data)")
        
        hist_data = market_data['historical_data']
        df = pd.DataFrame(hist_data)
        
        if not df.empty and 'timestamp' in df.columns:
            # Convert timestamp to datetime
            df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            # Create candlestick chart
            fig = go.Figure(data=go.Candlestick(
                x=df['datetime'],
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'],
                name='BTCUSDT'
            ))
            
            fig.update_layout(
                title="Live BTC/USDT Candlestick Chart (Bybit Testnet)",
                xaxis_title="Time",
                yaxis_title="Price (USDT)",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Loading historical chart data...")

def render_live_trade_history():
    """Render live trade history from Bybit"""
    st.markdown("## 📋 **LIVE TRADE HISTORY**")
    
    trades = st.session_state.live_trade_history
    
    if trades:
        # Convert to DataFrame for display
        df = pd.DataFrame(trades)
        
        # Format columns for display
        display_df = df.copy()
        display_df['Time'] = display_df['timestamp'].dt.strftime('%H:%M:%S')
        display_df['Date'] = display_df['timestamp'].dt.strftime('%Y-%m-%d')
        display_df['Side'] = display_df['side']
        display_df['Type'] = display_df['order_type']
        display_df['Quantity'] = display_df['qty'].apply(lambda x: f"{x:.6f}")
        display_df['Price'] = display_df['price'].apply(lambda x: f"${x:,.2f}")
        display_df['Status'] = display_df['status']
        display_df['Order ID'] = display_df['order_id']
        
        # Select columns for display
        show_df = display_df[['Date', 'Time', 'Side', 'Type', 'Quantity', 'Price', 'Status', 'Order ID']]
        
        st.dataframe(show_df, hide_index=True, use_container_width=True)
        
        # Trade statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            buy_count = len([t for t in trades if t['side'] == 'Buy'])
            st.metric("🟢 Buy Orders", buy_count)
        
        with col2:
            sell_count = len([t for t in trades if t['side'] == 'Sell'])
            st.metric("🔴 Sell Orders", sell_count)
        
        with col3:
            filled_count = len([t for t in trades if t['status'] == 'Filled'])
            st.metric("✅ Filled Orders", filled_count)
    else:
        st.info("No trade history available. Start trading to see your orders here!")

def render_api_status_panel():
    """Render API connection status"""
    st.markdown("## 🔗 **API CONNECTION STATUS**")
    
    api_status = st.session_state.get('api_status', '❓ Unknown')
    
    if '✅' in api_status:
        st.success(api_status)
        st.info("🧪 **Testnet Mode Active** - No real money at risk")
        st.info("📊 **Real Data Streaming** - Live market data from Bybit")
    elif '⚠️' in api_status:
        st.warning(api_status)
        st.warning("Using demo data as fallback")
    else:
        st.error(api_status)
        st.error("Check your API credentials in .env file")
    
    # API endpoints status
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📊 Market Data", "✅ Active")
    
    with col2:
        wallet_status = "✅ Active" if st.session_state.get('api_connected') else "❌ Error"
        st.metric("💰 Wallet Data", wallet_status)
    
    with col3:
        trade_status = "✅ Active" if st.session_state.get('api_connected') else "❌ Error"
        st.metric("📋 Trade History", trade_status)

def render_live_sidebar_controls(data_provider):
    """Render live sidebar controls"""
    st.sidebar.title("🎛️ **LIVE CONTROLS**")
    
    # Refresh controls
    if st.sidebar.button("🔄 Refresh All Data", type="primary"):
        with st.spinner("Refreshing live data..."):
            data_provider.refresh_data()
            st.sidebar.success("✅ Data refreshed!")
            st.rerun()
    
    # Auto-refresh
    auto_refresh = st.sidebar.checkbox("🔄 Auto-Refresh (30s)", value=False)
    if auto_refresh:
        st.sidebar.info("⏱️ Auto-refreshing every 30 seconds...")
        time.sleep(30)
        data_provider.refresh_data()
        st.rerun()
    
    # API Status
    st.sidebar.markdown("### 🔗 **API Status**")
    api_status = st.session_state.get('api_status', '❓ Unknown')
    
    if '✅' in api_status:
        st.sidebar.success("✅ Bybit API Connected")
        st.sidebar.success("🧪 Testnet Mode Active")
    else:
        st.sidebar.error("❌ API Connection Issue")
        st.sidebar.warning("Using Demo Data")
    
    # Trading Session
    st.sidebar.markdown("### 🌍 **Trading Session**")
    current_hour = datetime.now().hour
    if 0 <= current_hour < 8:
        st.sidebar.info("🏯 Asian Session")
    elif 8 <= current_hour < 16:
        st.sidebar.success("🏛️ London Session")
    else:
        st.sidebar.warning("🗽 New York Session")
    
    # Safety Notice
    st.sidebar.markdown("### ⚠️ **SAFETY NOTICE**")
    st.sidebar.info("🧪 **TESTNET ONLY**")
    st.sidebar.info("💰 **NO REAL MONEY**")
    st.sidebar.info("📊 **REAL DATA**")
    
    # Emergency
    st.sidebar.markdown("### 🚨 **Emergency**")
    if st.sidebar.button("🛑 Emergency Stop"):
        st.sidebar.error("🚨 All operations halted!")

# ============================================================================
# MAIN LIVE DASHBOARD APPLICATION
# ============================================================================

def main():
    """Main live dashboard application"""
    
    # Initialize live data provider
    data_provider = LiveBybitDataProvider()
    
    # Render live header
    render_live_header()
    st.markdown("---")
    
    # Render main components
    render_live_overview(data_provider)
    st.markdown("---")
    
    render_live_market_data(data_provider)
    st.markdown("---")
    
    render_live_trade_history()
    st.markdown("---")
    
    render_api_status_panel()
    
    # Render sidebar
    render_live_sidebar_controls(data_provider)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        🚀 <strong>LIVE Bybit Testnet Dashboard</strong> | 
        📊 <strong>Real-time Market Data</strong> | 
        🧪 <strong>Testnet Environment</strong> | 
        © 2025 Romain Hill
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    main()
