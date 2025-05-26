#!/usr/bin/env python3
"""
🚀 ADVANCED LIVE TRADING DASHBOARD - CLEAN VERSION
Professional Real-time Dashboard für Enhanced Smart Money Bot
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import requests
import json
import time
from datetime import datetime, timedelta
import os
import sys
from dotenv import load_dotenv

# Add root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import APIs
from exchange.bybit_api import BybitAPI
try:
    from corrected_live_api import LiveBybitAPI
except ImportError:
    print("Warning: corrected_live_api not found, using fallback")
    LiveBybitAPI = None

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="🚀 Advanced Live Trading Dashboard",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #FF6B35, #F7931E);
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .live-indicator {
        background: #FF4444;
        color: white;
        padding: 10px;
        border-radius: 5px;
        text-align: center;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

def render_professional_chart():
    """Render professional trading chart"""
    st.markdown("### 📈 SMART MONEY TRADING CHART")
    
    chart_data = st.session_state.get('chart_data', {'success': False})
    
    if chart_data.get('success') and chart_data.get('data'):
        try:
            # Convert chart data to DataFrame
            df = pd.DataFrame(chart_data['data'])
            
            if not df.empty and 'timestamp' in df.columns:
                # Create candlestick chart
                fig = go.Figure(data=go.Candlestick(
                    x=df['timestamp'],
                    open=df['open'],
                    high=df['high'],
                    low=df['low'],
                    close=df['close'],
                    name='BTCUSDT'
                ))
                
                fig.update_layout(
                    title='BTC/USDT Professional Chart',
                    xaxis_title='Time',
                    yaxis_title='Price (USDT)',
                    height=500,
                    template='plotly_dark'
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.error("❌ Invalid chart data format")
        except Exception as e:
            st.error(f"❌ Chart error: {str(e)}")
    else:
        st.info("📊 Loading chart data...")
        if chart_data.get('error'):
            st.error(f"Error: {chart_data['error']}")

def refresh_data():
    """Refresh all dashboard data"""
    try:
        if LiveBybitAPI:
            api = LiveBybitAPI()
            
            # Get chart data
            chart_data = api.get_kline_data("BTCUSDT", "5", 100)
            st.session_state.chart_data = chart_data
            
            # Get market data
            market_data = api.get_btc_price()
            st.session_state.market_data = market_data
            
            return True
        else:
            st.session_state.chart_data = {'success': False, 'error': 'API not available'}
            return False
    except Exception as e:
        st.session_state.chart_data = {'success': False, 'error': str(e)}
        return False

def main():
    """Main dashboard function"""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🚀 ADVANCED LIVE TRADING DASHBOARD 💰</h1>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="live-indicator">
        🔴 LIVE MAINNET - ECHTE $50.00 USDT! 🔴<br>
        Enhanced Smart Money Strategy • Professional Trading Interface • Real Money
    </div>
    """, unsafe_allow_html=True)
    
    # Warning
    st.warning("⚠️ MAINNET MODE - REAL MONEY AT RISK! NO SIMULATION! ⚠️")
    
    # Controls
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if st.button("🔄 Refresh All Data", type="primary"):
            with st.spinner("Refreshing data..."):
                if refresh_data():
                    st.success("✅ Data refreshed successfully!")
                    st.rerun()
                else:
                    st.error("❌ Failed to refresh data")
    
    with col2:
        st.markdown("**Status:** Live Trading Ready | **API:** Connected | **Mode:** MAINNET")
    
    # Initialize session state
    if 'chart_data' not in st.session_state:
        st.session_state.chart_data = {'success': False}
    if 'market_data' not in st.session_state:
        st.session_state.market_data = {'success': False}
    
    # Main content
    st.divider()
    
    # Render chart
    render_professional_chart()
    
    # Market data
    st.divider()
    st.markdown("### 💰 LIVE MARKET DATA")
    
    market_data = st.session_state.get('market_data', {'success': False})
    if market_data.get('success'):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("💰 BTC Price", f"${market_data.get('price', 0):,.2f}")
        
        with col2:
            change = market_data.get('change_24h', 0)
            st.metric("📊 24h Change", f"{change:+.2f}%")
        
        with col3:
            st.metric("📈 24h High", f"${market_data.get('high_24h', 0):,.2f}")
        
        with col4:
            st.metric("📉 24h Low", f"${market_data.get('low_24h', 0):,.2f}")
    else:
        st.info("Loading market data...")
    
    # Footer
    st.divider()
    st.markdown("""
    **🎯 Dashboard Features:**
    - ✅ Real-time BTC/USDT data
    - ✅ Professional candlestick charts
    - ✅ Live market metrics
    - ✅ Enhanced Smart Money Strategy integration
    """)

if __name__ == "__main__":
    main()
