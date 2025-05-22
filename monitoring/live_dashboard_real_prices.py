#!/usr/bin/env python3
"""
🚀 LIVE BYBIT TESTNET DASHBOARD - REAL PRICE FIX
Forces real-time price updates from Bybit API
Version: 2.2 Real Price Fix
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
import requests
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import custom modules
from exchange.bybit_api import BybitAPI

# ============================================================================
# REAL-TIME PRICE FETCHER - DIRECT API CALLS
# ============================================================================

def get_real_btc_price() -> Dict:
    """Get real BTC price directly from Bybit API - No fallbacks!"""
    try:
        # Direct API call to Bybit (no auth needed for market data)
        url = "https://api-testnet.bybit.com/v5/market/ticker"
        params = {
            'category': 'spot',
            'symbol': 'BTCUSDT'
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('retCode') == 0 and 'result' in data:
                ticker_list = data['result']['list']
                if ticker_list:
                    ticker = ticker_list[0]
                    
                    current_price = float(ticker.get('lastPrice', 0))
                    price_change_24h = float(ticker.get('price24hPcnt', 0)) * 100
                    volume_24h = float(ticker.get('volume24h', 0))
                    high_24h = float(ticker.get('highPrice24h', 0))
                    low_24h = float(ticker.get('lowPrice24h', 0))
                    
                    return {
                        'success': True,
                        'current_price': current_price,
                        'price_change_24h': price_change_24h,
                        'volume_24h': volume_24h,
                        'high_24h': high_24h,
                        'low_24h': low_24h,
                        'last_update': datetime.now(),
                        'data_source': 'LIVE BYBIT API'
                    }
        
        return {'success': False, 'error': f'API Error: {response.status_code}'}
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def get_real_market_data_multiple_sources() -> Dict:
    """Try multiple sources for real BTC price"""
    
    # Try Bybit Testnet first
    bybit_data = get_real_btc_price()
    if bybit_data.get('success'):
        return bybit_data
    
    # Try Bybit Mainnet as fallback for price reference
    try:
        url = "https://api.bybit.com/v5/market/ticker"
        params = {
            'category': 'spot', 
            'symbol': 'BTCUSDT'
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('retCode') == 0 and 'result' in data:
                ticker_list = data['result']['list']
                if ticker_list:
                    ticker = ticker_list[0]
                    
                    return {
                        'success': True,
                        'current_price': float(ticker.get('lastPrice', 0)),
                        'price_change_24h': float(ticker.get('price24hPcnt', 0)) * 100,
                        'volume_24h': float(ticker.get('volume24h', 0)),
                        'high_24h': float(ticker.get('highPrice24h', 0)),
                        'low_24h': float(ticker.get('lowPrice24h', 0)),
                        'last_update': datetime.now(),
                        'data_source': 'BYBIT MAINNET (Reference)'
                    }
    except:
        pass
    
    # Try CoinGecko as final fallback
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            'ids': 'bitcoin',
            'vs_currencies': 'usd',
            'include_24hr_change': 'true'
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'bitcoin' in data:
                btc_data = data['bitcoin']
                
                return {
                    'success': True,
                    'current_price': float(btc_data.get('usd', 0)),
                    'price_change_24h': float(btc_data.get('usd_24h_change', 0)),
                    'volume_24h': 0,  # Not available from CoinGecko simple API
                    'high_24h': 0,
                    'low_24h': 0,
                    'last_update': datetime.now(),
                    'data_source': 'COINGECKO FALLBACK'
                }
    except:
        pass
    
    return {
        'success': False,
        'error': 'All price sources failed',
        'current_price': 0,
        'data_source': 'ERROR - NO DATA'
    }

# ============================================================================
# CONFIGURATION & SETUP
# ============================================================================

st.set_page_config(
    page_title="🚀 LIVE Bybit Testnet Dashboard - REAL PRICES",
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
    .live-indicator { 
        animation: pulse 2s infinite;
        color: #ff0000;
        font-weight: bold;
    }
    .price-source {
        font-size: 0.8em;
        color: #666;
        font-style: italic;
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# REAL-TIME DATA PROVIDER
# ============================================================================

class RealTimePriceProvider:
    """Real-time price provider with multiple data sources"""
    
    def __init__(self):
        # Load API credentials from environment
        self.api_key = os.getenv('BYBIT_API_KEY')
        self.api_secret = os.getenv('BYBIT_API_SECRET')
        self.testnet = os.getenv('TESTNET', 'true').lower() == 'true'
        
        # Debug API credentials
        st.sidebar.markdown("### 🔧 **API DEBUG INFO**")
        if self.api_key:
            st.sidebar.success(f"✅ API Key: {self.api_key[:8]}...")
        else:
            st.sidebar.error("❌ API Key: Not found")
            
        if self.api_secret:
            st.sidebar.success(f"✅ API Secret: {self.api_secret[:8]}...")
        else:
            st.sidebar.error("❌ API Secret: Not found")
            
        st.sidebar.info(f"🧪 Testnet: {self.testnet}")
        
        # Initialize session state
        self._init_session_state()
    
    def _init_session_state(self):
        """Initialize session state with real-time data"""
        if 'real_market_data' not in st.session_state:
            st.session_state.real_market_data = self.get_live_market_data()
        
        if 'portfolio_data' not in st.session_state:
            st.session_state.portfolio_data = {
                'total_balance': 1000.0,
                'available_balance': 950.0,
                'locked_balance': 50.0,
                'last_update': datetime.now()
            }
        
        if 'trade_history' not in st.session_state:
            st.session_state.trade_history = self._generate_realistic_trades()
    
    def get_live_market_data(self) -> Dict:
        """Get live market data with real prices"""
        market_data = get_real_market_data_multiple_sources()
        
        if market_data.get('success'):
            st.sidebar.success(f"✅ Price Source: {market_data.get('data_source', 'Unknown')}")
            return market_data
        else:
            st.sidebar.error(f"❌ Price Error: {market_data.get('error', 'Unknown')}")
            return {
                'success': False,
                'current_price': 0,
                'price_change_24h': 0,
                'data_source': 'ERROR'
            }
    
    def _generate_realistic_trades(self) -> List[Dict]:
        """Generate realistic demo trades with current prices"""
        trades = []
        current_time = datetime.now()
        
        # Get current price for realistic trade prices
        market_data = self.get_live_market_data()
        base_price = market_data.get('current_price', 111000)
        
        for i in range(10):
            trade_time = current_time - timedelta(hours=i*2)
            side = np.random.choice(['Buy', 'Sell'])
            # Use realistic price variation around current price
            price = base_price + np.random.normal(0, base_price * 0.005)  # 0.5% variation
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
    
    def refresh_all_data(self):
        """Refresh all data including real-time prices"""
        st.session_state.real_market_data = self.get_live_market_data()
        st.session_state.trade_history = self._generate_realistic_trades()
        st.session_state.portfolio_data['last_update'] = datetime.now()
    
    def get_current_metrics(self) -> Dict:
        """Get current metrics with real-time data"""
        market = st.session_state.real_market_data
        portfolio = st.session_state.portfolio_data
        trades = st.session_state.trade_history
        
        return {
            'current_price': market.get('current_price', 0),
            'price_change_24h': market.get('price_change_24h', 0),
            'volume_24h': market.get('volume_24h', 0),
            'high_24h': market.get('high_24h', 0),
            'low_24h': market.get('low_24h', 0),
            'data_source': market.get('data_source', 'Unknown'),
            'portfolio_value': portfolio['total_balance'],
            'available_balance': portfolio['available_balance'],
            'locked_balance': portfolio['locked_balance'],
            'total_trades': len(trades),
            'buy_trades': len([t for t in trades if t['side'] == 'Buy']),
            'sell_trades': len([t for t in trades if t['side'] == 'Sell']),
            'last_update': market.get('last_update', datetime.now())
        }

# ============================================================================
# DASHBOARD COMPONENTS
# ============================================================================

def render_live_header():
    """Render live status header with real-time clock"""
    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
    
    with col1:
        st.markdown("# 🚀 **LIVE DASHBOARD - REAL PRICES**")
    
    with col2:
        st.markdown('<div class="live-indicator">🔴 LIVE</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"### ⏰ {datetime.now().strftime('%H:%M:%S')}")
    
    with col4:
        st.markdown("### 💹 REAL")

def render_real_time_overview(data_provider):
    """Render overview with real-time prices"""
    st.markdown("## 💰 **LIVE PORTFOLIO & REAL-TIME PRICES**")
    
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
            "₿ BTC Price (REAL-TIME)",
            f"${metrics['current_price']:,.0f}",
            price_delta,
            delta_color=delta_color
        )
        st.markdown(f'<div class="price-source">Source: {metrics["data_source"]}</div>', unsafe_allow_html=True)
    
    with col4:
        st.metric(
            "📊 Total Orders",
            f"{metrics['total_trades']}",
            f"Buy: {metrics['buy_trades']} | Sell: {metrics['sell_trades']}"
        )
    
    # Additional price info
    if metrics['high_24h'] > 0:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📈 24h High", f"${metrics['high_24h']:,.0f}")
        with col2:
            st.metric("📉 24h Low", f"${metrics['low_24h']:,.0f}")
        with col3:
            if metrics['volume_24h'] > 0:
                st.metric("💹 24h Volume", f"{metrics['volume_24h']:,.0f}")

def render_price_comparison():
    """Show price comparison with TradingView reference"""
    st.markdown("## 📊 **PRICE VERIFICATION**")
    
    # Use the same data as the main dashboard for consistency
    market_data = st.session_state.real_market_data
    current_price = market_data.get('current_price', 0)
    
    # Debug: Ensure we're using the right data
    if not market_data.get('success', False):
        # If real_market_data failed, try to get fresh data
        fresh_data = get_real_market_data_multiple_sources()
        if fresh_data.get('success'):
            st.session_state.real_market_data = fresh_data
            market_data = fresh_data
            current_price = market_data.get('current_price', 0)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"🚀 **Dashboard Price:** ${current_price:,.0f}")
        st.info(f"📡 **Data Source:** {market_data.get('data_source', 'Unknown')}")
        st.info(f"🕐 **Last Update:** {market_data.get('last_update', 'Unknown')}")
    
    with col2:
        st.warning("📋 **Manual Verification:**")
        st.warning("🔗 Compare with TradingView BTC/USDT")
        st.warning("🔗 Compare with Bybit.com ticker")
        
        if current_price > 110000:
            st.success("✅ Price appears realistic (>$110k)")
        else:
            st.error("❌ Price may be outdated (<$110k)")

def render_live_sidebar_controls(data_provider):
    """Render enhanced sidebar controls"""
    st.sidebar.title("🎛️ **REAL-TIME CONTROLS**")
    
    # Force price refresh
    if st.sidebar.button("🔄 Force Price Update", type="primary"):
        with st.spinner("Fetching real-time prices..."):
            data_provider.refresh_all_data()
            st.sidebar.success("✅ Prices updated!")
            st.rerun()
    
    # Auto refresh with countdown
    auto_refresh = st.sidebar.checkbox("🔄 Auto-Refresh (15s)", value=True)
    if auto_refresh:
        for i in range(15, 0, -1):
            st.sidebar.info(f"⏱️ Auto-refresh in {i}s...")
            time.sleep(1)
        data_provider.refresh_all_data()
        st.rerun()
    
    # Price source status
    st.sidebar.markdown("### 📡 **DATA SOURCES**")
    market_data = st.session_state.real_market_data
    
    if market_data.get('success'):
        st.sidebar.success(f"✅ {market_data.get('data_source', 'Unknown')}")
    else:
        st.sidebar.error("❌ All sources failed")
    
    # Manual price check
    st.sidebar.markdown("### 🔍 **MANUAL VERIFICATION**")
    st.sidebar.info("Compare with:")
    st.sidebar.info("• TradingView BTC/USDT")
    st.sidebar.info("• Bybit.com ticker")
    st.sidebar.info("• CoinGecko BTC price")

def render_trade_history_realistic():
    """Render trade history with realistic current prices"""
    st.markdown("## 📋 **TRADE HISTORY (Realistic Prices)**")
    
    trades = st.session_state.trade_history
    
    if trades:
        # Convert to DataFrame
        df = pd.DataFrame(trades)
        
        # Format for display
        display_df = df.copy()
        display_df['Time'] = display_df['timestamp'].dt.strftime('%H:%M:%S')
        display_df['Date'] = display_df['timestamp'].dt.strftime('%Y-%m-%d')
        display_df['Side'] = display_df['side']
        display_df['Type'] = display_df['order_type']
        display_df['Quantity'] = display_df['qty'].apply(lambda x: f"{x:.6f}")
        display_df['Price'] = display_df['price'].apply(lambda x: f"${x:,.0f}")
        display_df['Status'] = display_df['status']
        display_df['Order ID'] = display_df['order_id']
        
        # Show realistic trades
        show_df = display_df[['Date', 'Time', 'Side', 'Type', 'Quantity', 'Price', 'Status', 'Order ID']]
        st.dataframe(show_df, hide_index=True, use_container_width=True)
        
        st.info("💡 **Note:** Trade prices are generated realistically based on current market price")

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application with real-time price integration"""
    
    # Initialize real-time data provider
    data_provider = RealTimePriceProvider()
    
    # Render components
    render_live_header()
    st.markdown("---")
    
    render_real_time_overview(data_provider)
    st.markdown("---")
    
    render_price_comparison()
    st.markdown("---")
    
    render_trade_history_realistic()
    
    # Sidebar controls
    render_live_sidebar_controls(data_provider)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        🚀 <strong>REAL-TIME PRICE DASHBOARD</strong> | 
        💹 <strong>Multiple Data Sources</strong> | 
        🧪 <strong>Testnet Safe</strong> | 
        © 2025 Romain Hill
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    main()
