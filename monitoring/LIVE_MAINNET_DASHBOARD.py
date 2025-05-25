#!/usr/bin/env python3
"""
💰 LIVE MAINNET DASHBOARD - MIT ECHTEN $83.38 USDT BALANCE!
KEINE SIMULATION - NUR ECHTE BYBIT MAINNET DATEN!
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
import numpy as np
from live_bybit_api import LiveBybitAPI

# ============================================================================
# STREAMLIT CONFIGURATION - MAINNET MODE
# ============================================================================

st.set_page_config(
    page_title="💰 LIVE MAINNET Trading Bot",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# LIVE MAINNET CSS STYLES
# ============================================================================

st.markdown("""
<style>
    .mainnet-header {
        background: linear-gradient(90deg, #e74c3c, #c0392b);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        border: 3px solid #fff;
        box-shadow: 0 4px 15px rgba(231, 76, 60, 0.3);
        animation: pulse-red 3s infinite;
    }
    
    @keyframes pulse-red {
        0% { box-shadow: 0 4px 15px rgba(231, 76, 60, 0.3); }
        50% { box-shadow: 0 4px 25px rgba(231, 76, 60, 0.6); }
        100% { box-shadow: 0 4px 15px rgba(231, 76, 60, 0.3); }
    }
    
    .live-balance {
        background: linear-gradient(135deg, #2ecc71, #27ae60);
        color: white;
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        font-size: 1.5rem;
        font-weight: bold;
        margin: 1rem 0;
        border: 2px solid #fff;
        box-shadow: 0 6px 20px rgba(46, 204, 113, 0.4);
    }
    
    .api-status {
        background: linear-gradient(90deg, #2ecc71, #27ae60);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 10px;
        display: inline-block;
        font-weight: bold;
        margin: 0.5rem;
        animation: pulse-green 2s infinite;
    }
    
    @keyframes pulse-green {
        0% { opacity: 1; }
        50% { opacity: 0.8; }
        100% { opacity: 1; }
    }
    
    .real-price {
        background: linear-gradient(90deg, #3498db, #2980b9);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-size: 1.2rem;
        margin: 0.5rem 0;
    }
    
    .no-simulation {
        background: linear-gradient(90deg, #f39c12, #e67e22);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# LIVE DATA HANDLER - MAINNET ONLY
# ============================================================================

@st.cache_data(ttl=15)  # Refresh every 15 seconds
def get_live_mainnet_balance():
    """Holt ECHTE Mainnet Balance - KEINE SIMULATION!"""
    api = LiveBybitAPI()
    result = api.get_dashboard_data()
    
    if result['success']:
        return {
            'portfolio_value': result['portfolio_value'],
            'balances': result['balances'],
            'btc_price': result['btc_price'],
            'btc_change_24h': result['btc_change_24h'],
            'btc_high_24h': result['btc_high_24h'],
            'btc_low_24h': result['btc_low_24h'],
            'account_type': result['account_type'],
            'api_connected': True,
            'last_update': datetime.now(),
            'is_real': True
        }
    else:
        return {
            'api_connected': False,
            'error': 'API Connection failed',
            'is_real': False
        }

# ============================================================================
# DASHBOARD COMPONENTS - LIVE MAINNET
# ============================================================================

def render_mainnet_header():
    """MAINNET Warning Header"""
    
    st.markdown("""
    <div class="mainnet-header">
        <h1>💰 LIVE BYBIT MAINNET TRADING DASHBOARD 💰</h1>
        <h2>🔴 REAL MONEY - NO SIMULATION! 🔴</h2>
        <p style="font-size: 1.1rem; margin-top: 1rem;">
            Connected to your actual Bybit account with real USDT balance
        </p>
    </div>
    """, unsafe_allow_html=True)

def render_live_balance_section(data):
    """Echte Balance Anzeige"""
    
    if not data.get('api_connected', False):
        st.error("❌ API Connection Failed!")
        st.error(f"Error: {data.get('error', 'Unknown error')}")
        return
    
    # Real Portfolio Value
    portfolio_value = data['portfolio_value']
    account_type = data['account_type']
    
    st.markdown(f"""
    <div class="live-balance">
        💰 LIVE {account_type} PORTFOLIO: ${portfolio_value:.2f} USDT
        <br><small>🔄 Last Update: {data['last_update'].strftime('%H:%M:%S')}</small>
    </div>
    """, unsafe_allow_html=True)
    
    # Detailed Balance Breakdown
    st.markdown("### 💼 **LIVE BALANCE BREAKDOWN**")
    
    col1, col2, col3 = st.columns(3)
    
    balances = data['balances']
    
    with col1:
        usdt_balance = balances.get('USDT', 0)
        st.metric(
            label="💵 USDT Balance",
            value=f"{usdt_balance:.2f}",
            delta="Real Balance"
        )
    
    with col2:
        btc_balance = balances.get('BTC', 0)
        if btc_balance > 0:
            st.metric(
                label="₿ BTC Balance", 
                value=f"{btc_balance:.6f}",
                delta="Real Balance"
            )
        else:
            st.metric(
                label="₿ BTC Balance",
                value="0.000000",
                delta="No BTC"
            )
    
    with col3:
        st.metric(
            label="🏦 Account Type",
            value=account_type,
            delta="LIVE API"
        )

def render_live_btc_price(data):
    """Live BTC Preis von Bybit"""
    
    if not data.get('api_connected', False):
        return
    
    btc_price = data['btc_price']
    btc_change = data['btc_change_24h']
    btc_high = data['btc_high_24h']
    btc_low = data['btc_low_24h']
    
    st.markdown("### 📈 **LIVE BTC/USDT PRICE (Bybit)**")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        delta_color = "normal" if btc_change >= 0 else "inverse"
        st.metric(
            label="💎 Current Price",
            value=f"${btc_price:,.2f}",
            delta=f"{btc_change:+.2f}%",
            delta_color=delta_color
        )
    
    with col2:
        st.metric(
            label="📈 24h High",
            value=f"${btc_high:,.2f}",
            delta="Live Data"
        )
    
    with col3:
        st.metric(
            label="📉 24h Low", 
            value=f"${btc_low:,.2f}",
            delta="Live Data"
        )
    
    with col4:
        # Calculate range
        daily_range = ((btc_high - btc_low) / btc_low) * 100
        st.metric(
            label="📊 Daily Range",
            value=f"{daily_range:.2f}%",
            delta="Volatility"
        )

def render_no_simulation_notice():
    """Klarer Hinweis: KEINE SIMULATION"""
    
    st.markdown("""
    <div class="no-simulation">
        ⚠️ NO SIMULATION - ALL DATA IS REAL! ⚠️
        <br>This dashboard shows your actual Bybit Mainnet account data.
        <br>Portfolio values, balances, and prices are 100% real and live.
    </div>
    """, unsafe_allow_html=True)

def render_api_status(data):
    """Live API Status"""
    
    st.markdown("### 📡 **API CONNECTION STATUS**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if data.get('api_connected', False):
            st.markdown('<div class="api-status">✅ CONNECTED</div>', unsafe_allow_html=True)
        else:
            st.error("❌ DISCONNECTED")
    
    with col2:
        account_type = data.get('account_type', 'UNKNOWN')
        if account_type == 'MAINNET':
            st.markdown('<div class="api-status">💰 MAINNET</div>', unsafe_allow_html=True)
        else:
            st.warning(f"🧪 {account_type}")
    
    with col3:
        if data.get('is_real', False):
            st.markdown('<div class="api-status">🔴 LIVE DATA</div>', unsafe_allow_html=True)
        else:
            st.error("❌ NO LIVE DATA")

def render_trading_readiness():
    """Trading Readiness Check"""
    
    st.markdown("### 🚀 **TRADING READINESS STATUS**")
    
    # Get fresh data to check readiness
    data = get_live_mainnet_balance()
    
    readiness_checks = []
    
    if data.get('api_connected', False):
        readiness_checks.append(("✅", "API Connection", "Connected to Bybit Mainnet"))
    else:
        readiness_checks.append(("❌", "API Connection", "Failed to connect"))
    
    portfolio_value = data.get('portfolio_value', 0)
    if portfolio_value >= 50:
        readiness_checks.append(("✅", "Balance Check", f"${portfolio_value:.2f} USDT available"))
    elif portfolio_value > 0:
        readiness_checks.append(("⚠️", "Balance Check", f"Only ${portfolio_value:.2f} USDT (recommend 50+)"))
    else:
        readiness_checks.append(("❌", "Balance Check", "No USDT balance found"))
    
    if data.get('account_type') == 'MAINNET':
        readiness_checks.append(("✅", "Account Type", "Mainnet account confirmed"))
    else:
        readiness_checks.append(("⚠️", "Account Type", f"{data.get('account_type', 'Unknown')} account"))
    
    btc_price = data.get('btc_price', 0)
    if btc_price > 50000:
        readiness_checks.append(("✅", "Market Data", f"BTC price: ${btc_price:,.0f}"))
    else:
        readiness_checks.append(("❌", "Market Data", "Invalid BTC price data"))
    
    # Display readiness table
    readiness_df = pd.DataFrame(readiness_checks, columns=['Status', 'Check', 'Details'])
    st.dataframe(readiness_df, hide_index=True, use_container_width=True)
    
    # Overall readiness
    passed_checks = sum(1 for check in readiness_checks if check[0] == "✅")
    total_checks = len(readiness_checks)
    
    if passed_checks == total_checks:
        st.success(f"🚀 **READY FOR LIVE TRADING!** ({passed_checks}/{total_checks} checks passed)")
        st.balloons()
    elif passed_checks >= total_checks - 1:
        st.warning(f"⚠️ **MOSTLY READY** ({passed_checks}/{total_checks} checks passed)")
    else:
        st.error(f"❌ **NOT READY** ({passed_checks}/{total_checks} checks passed)")

def render_sidebar_live_controls(data):
    """Sidebar mit Live Controls"""
    
    st.sidebar.markdown("### 💰 **LIVE MAINNET CONTROLS**")
    
    # Auto-refresh
    auto_refresh = st.sidebar.checkbox("🔄 Auto-Refresh (15s)", value=True)
    
    if auto_refresh:
        st.sidebar.success("🔄 Live Updates: ON")
        time.sleep(0.1)
        st.rerun()
    else:
        if st.sidebar.button("🔄 Refresh Now"):
            st.cache_data.clear()
            st.rerun()
    
    # Connection Status
    st.sidebar.markdown("### 📡 **STATUS**")
    if data.get('api_connected', False):
        st.sidebar.success("✅ Bybit API: CONNECTED")
        st.sidebar.success(f"💰 Account: {data.get('account_type', 'UNKNOWN')}")
        st.sidebar.success("🔴 Data: LIVE & REAL")
    else:
        st.sidebar.error("❌ API: DISCONNECTED")
        st.sidebar.warning("⚠️ No live data available")
    
    # Balance Info
    if data.get('api_connected', False):
        st.sidebar.markdown("### 💼 **QUICK BALANCE**")
        portfolio_value = data.get('portfolio_value', 0)
        st.sidebar.metric("Total USDT", f"${portfolio_value:.2f}")
        
        balances = data.get('balances', {})
        for coin, amount in balances.items():
            if coin == 'USDT':
                st.sidebar.metric(f"{coin} Balance", f"{amount:.2f}")
            else:
                st.sidebar.metric(f"{coin} Balance", f"{amount:.6f}")
    
    # Emergency Controls
    st.sidebar.markdown("### 🚨 **EMERGENCY**")
    
    if st.sidebar.button("🛑 EMERGENCY STOP", type="primary"):
        st.sidebar.error("🚨 EMERGENCY STOP!")
        st.sidebar.warning("Trading would be halted!")
    
    # System Info
    st.sidebar.markdown("### ⚙️ **SYSTEM INFO**")
    st.sidebar.text("Mode: LIVE MAINNET")
    st.sidebar.text("Simulation: DISABLED")
    st.sidebar.text("Real Money: YES")
    
    if data.get('last_update'):
        st.sidebar.text(f"Last Update: {data['last_update'].strftime('%H:%M:%S')}")

# ============================================================================
# MAIN DASHBOARD FUNCTION
# ============================================================================

def main():
    """Main Dashboard - Live Mainnet Mode"""
    
    # Get live data
    data = get_live_mainnet_balance()
    
    # Render sidebar first
    render_sidebar_live_controls(data)
    
    # Main content
    render_mainnet_header()
    
    # No simulation notice
    render_no_simulation_notice()
    
    # API Status
    render_api_status(data)
    
    # Live balance section
    render_live_balance_section(data)
    
    # Live BTC price
    render_live_btc_price(data)
    
    # Trading readiness
    render_trading_readiness()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #e74c3c; font-weight: bold; font-size: 1.1rem;'>
        💰 LIVE BYBIT MAINNET DASHBOARD - NO SIMULATION! 💰<br>
        🚀 Enhanced Smart Money Trading Bot V2 | Ready for Real Trading<br>
        © 2025 Romain Hill | Mainnet Production System
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
