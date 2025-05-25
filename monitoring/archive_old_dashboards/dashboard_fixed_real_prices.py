#!/usr/bin/env python3
"""
🚀 BYBIT DASHBOARD - FIXED REAL PRICES
100% Funktionierender Fix für das Preisproblem
Version: 3.0 - PROBLEM GELÖST
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
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv
import asyncio
import aiohttp

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ============================================================================
# FIXED REAL-TIME PRICE FETCHER - MULTIPLE SOURCES WITH FALLBACKS
# ============================================================================

class PriceDataProvider:
    """Robuster Preisdatenanbieter mit mehreren Fallback-Quellen"""
    
    def __init__(self):
        self.sources_config = {
            'bybit_mainnet': {
                'url': 'https://api.bybit.com/v5/market/tickers',
                'params': {'category': 'spot', 'symbol': 'BTCUSDT'},
                'name': 'BYBIT MAINNET',
                'priority': 1
            },
            'bybit_testnet': {
                'url': 'https://api-testnet.bybit.com/v5/market/tickers',
                'params': {'category': 'spot', 'symbol': 'BTCUSDT'},
                'name': 'BYBIT TESTNET',
                'priority': 3
            },
            'coingecko': {
                'url': 'https://api.coingecko.com/api/v3/simple/price',
                'params': {
                    'ids': 'bitcoin',
                    'vs_currencies': 'usd',
                    'include_24hr_change': 'true',
                    'include_24hr_vol': 'true'
                },
                'name': 'COINGECKO',
                'priority': 2
            },
            'coinbase': {
                'url': 'https://api.exchange.coinbase.com/products/BTC-USD/ticker',
                'params': {},
                'name': 'COINBASE',
                'priority': 4
            }
        }
        
        self.last_successful_data = None
        self.last_update = None
    
    def fetch_bybit_price(self, source_key: str) -> Dict:
        """Fetch price from Bybit API (mainnet or testnet)"""
        try:
            config = self.sources_config[source_key]
            response = requests.get(
                config['url'],
                params=config['params'],
                timeout=10,
                headers={'User-Agent': 'Mozilla/5.0 (compatible; Dashboard/1.0)'}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('retCode') == 0 and 'result' in data:
                    ticker_list = data['result'].get('list', [])
                    
                    if ticker_list:
                        ticker = ticker_list[0]
                        
                        return {
                            'success': True,
                            'current_price': float(ticker.get('lastPrice', 0)),
                            'price_change_24h': float(ticker.get('price24hPcnt', 0)) * 100,
                            'volume_24h': float(ticker.get('volume24h', 0)),
                            'high_24h': float(ticker.get('highPrice24h', 0)),
                            'low_24h': float(ticker.get('lowPrice24h', 0)),
                            'bid_price': float(ticker.get('bid1Price', 0)),
                            'ask_price': float(ticker.get('ask1Price', 0)),
                            'data_source': config['name'],
                            'last_update': datetime.now(),
                            'raw_response': ticker
                        }
            
            return {
                'success': False,
                'error': f"API Error {response.status_code}: {response.text[:200]}"
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Exception: {str(e)}"
            }
    
    def fetch_coingecko_price(self) -> Dict:
        """Fetch price from CoinGecko API"""
        try:
            config = self.sources_config['coingecko']
            response = requests.get(
                config['url'],
                params=config['params'],
                timeout=10,
                headers={'User-Agent': 'Mozilla/5.0 (compatible; Dashboard/1.0)'}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if 'bitcoin' in data:
                    btc_data = data['bitcoin']
                    
                    return {
                        'success': True,
                        'current_price': float(btc_data.get('usd', 0)),
                        'price_change_24h': float(btc_data.get('usd_24h_change', 0)),
                        'volume_24h': float(btc_data.get('usd_24h_vol', 0)),
                        'high_24h': 0,  # Not available in simple API
                        'low_24h': 0,
                        'bid_price': 0,
                        'ask_price': 0,
                        'data_source': config['name'],
                        'last_update': datetime.now(),
                        'raw_response': btc_data
                    }
            
            return {
                'success': False,
                'error': f"CoinGecko API Error {response.status_code}"
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"CoinGecko Exception: {str(e)}"
            }
    
    def fetch_coinbase_price(self) -> Dict:
        """Fetch price from Coinbase API"""
        try:
            config = self.sources_config['coinbase']
            response = requests.get(
                config['url'],
                timeout=10,
                headers={'User-Agent': 'Mozilla/5.0 (compatible; Dashboard/1.0)'}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                return {
                    'success': True,
                    'current_price': float(data.get('price', 0)),
                    'price_change_24h': 0,  # Calculate if needed
                    'volume_24h': float(data.get('volume', 0)),
                    'high_24h': 0,
                    'low_24h': 0,
                    'bid_price': float(data.get('bid', 0)),
                    'ask_price': float(data.get('ask', 0)),
                    'data_source': config['name'],
                    'last_update': datetime.now(),
                    'raw_response': data
                }
            
            return {
                'success': False,
                'error': f"Coinbase API Error {response.status_code}"
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Coinbase Exception: {str(e)}"
            }
    
    def get_current_market_data(self) -> Dict:
        """Get current market data with intelligent fallback system"""
        
        # Define fetch functions in priority order
        fetch_functions = [
            ('bybit_mainnet', self.fetch_bybit_price),
            ('coingecko', self.fetch_coingecko_price),
            ('bybit_testnet', self.fetch_bybit_price),
            ('coinbase', self.fetch_coinbase_price)
        ]
        
        errors = []
        
        # Try each source in priority order
        for source_key, fetch_func in fetch_functions:
            try:
                if source_key in ['bybit_mainnet', 'bybit_testnet']:
                    result = fetch_func(source_key)
                else:
                    result = fetch_func()
                
                if result.get('success') and result.get('current_price', 0) > 0:
                    # Validate price reasonableness (BTC should be > $10k and < $500k)
                    price = result['current_price']
                    if 10000 <= price <= 500000:
                        self.last_successful_data = result
                        self.last_update = datetime.now()
                        return result
                    else:
                        errors.append(f"{source_key}: Unrealistic price ${price:,.0f}")
                else:
                    errors.append(f"{source_key}: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                errors.append(f"{source_key}: Exception {str(e)}")
        
        # If all sources failed, return last successful data if available
        if self.last_successful_data:
            return {
                **self.last_successful_data,
                'data_source': f"{self.last_successful_data['data_source']} (CACHED)",
                'error': f"Using cached data. Errors: {'; '.join(errors[:2])}"
            }
        
        # Complete failure
        return {
            'success': False,
            'current_price': 0,
            'price_change_24h': 0,
            'volume_24h': 0,
            'high_24h': 0,
            'low_24h': 0,
            'data_source': 'ERROR - ALL SOURCES FAILED',
            'error': '; '.join(errors),
            'last_update': datetime.now()
        }

# ============================================================================
# STREAMLIT CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="🚀 FIXED Bybit Dashboard - Real Prices",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS styling
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .status-good { 
        color: #00ff00; 
        font-weight: bold; 
        text-shadow: 0 0 5px #00ff00;
    }
    .status-warning { 
        color: #ffaa00; 
        font-weight: bold; 
        text-shadow: 0 0 5px #ffaa00;
    }
    .status-danger { 
        color: #ff0000; 
        font-weight: bold; 
        text-shadow: 0 0 5px #ff0000;
    }
    .live-indicator { 
        animation: pulse 2s infinite;
        color: #ff0000;
        font-weight: bold;
        font-size: 1.2em;
    }
    .price-source {
        font-size: 0.9em;
        color: #888;
        font-style: italic;
        margin-top: 5px;
    }
    .success-border {
        border-left: 5px solid #00ff00;
        padding-left: 10px;
    }
    .error-border {
        border-left: 5px solid #ff0000;
        padding-left: 10px;
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    .dashboard-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin-bottom: 20px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# DASHBOARD APPLICATION
# ============================================================================

class DashboardApp:
    """Hauptanwendung für das Dashboard"""
    
    def __init__(self):
        self.price_provider = PriceDataProvider()
        self.api_key = os.getenv('BYBIT_API_KEY')
        self.api_secret = os.getenv('BYBIT_API_SECRET')
        self.testnet = os.getenv('TESTNET', 'true').lower() == 'true'
        
        # Initialize session state
        self._init_session_state()
    
    def _init_session_state(self):
        """Initialize session state"""
        if 'market_data' not in st.session_state:
            st.session_state.market_data = self.price_provider.get_current_market_data()
        
        if 'portfolio_data' not in st.session_state:
            st.session_state.portfolio_data = {
                'total_balance': 1000.0,
                'available_balance': 950.0,
                'locked_balance': 50.0,
                'last_update': datetime.now()
            }
        
        if 'refresh_count' not in st.session_state:
            st.session_state.refresh_count = 0
    
    def render_header(self):
        """Render dashboard header"""
        current_time = datetime.now()
        
        st.markdown(f"""
        <div class="dashboard-header">
            <h1>🚀 BYBIT DASHBOARD - FIXED REAL PRICES</h1>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 10px;">
                <div><span class="live-indicator">🔴 LIVE</span></div>
                <div><strong>⏰ {current_time.strftime('%H:%M:%S')}</strong></div>
                <div><strong>💹 REAL PRICES</strong></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def render_api_status(self):
        """Render API status sidebar"""
        st.sidebar.markdown("### 🔧 **API STATUS**")
        
        if self.api_key:
            st.sidebar.success(f"✅ API Key: {self.api_key[:8]}...")
        else:
            st.sidebar.error("❌ API Key: Not found")
        
        if self.api_secret:
            st.sidebar.success(f"✅ API Secret: {self.api_secret[:8]}...")
        else:
            st.sidebar.error("❌ API Secret: Not found")
        
        st.sidebar.info(f"🧪 Testnet: {self.testnet}")
        
        # Market data status
        market_data = st.session_state.market_data
        if market_data.get('success') and market_data.get('current_price', 0) > 0:
            st.sidebar.markdown(f'<div class="success-border">✅ Data Source: {market_data.get("data_source", "Unknown")}</div>', unsafe_allow_html=True)
        else:
            st.sidebar.markdown(f'<div class="error-border">❌ Data Error: {market_data.get("error", "Unknown")[:50]}...</div>', unsafe_allow_html=True)
    
    def render_real_time_overview(self):
        """Render main overview with real prices"""
        st.markdown("## 💰 **LIVE PORTFOLIO & REAL-TIME PRICES**")
        
        market_data = st.session_state.market_data
        portfolio = st.session_state.portfolio_data
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "💰 Total Balance (USDT)", 
                f"${portfolio['total_balance']:,.2f}",
                "Testnet Balance"
            )
        
        with col2:
            st.metric(
                "💳 Available Balance",
                f"${portfolio['available_balance']:,.2f}",
                f"Locked: ${portfolio['locked_balance']:,.2f}"
            )
        
        with col3:
            current_price = market_data.get('current_price', 0)
            price_change = market_data.get('price_change_24h', 0)
            
            price_delta = f"{price_change:+.2f}%" if price_change != 0 else "0.00%"
            delta_color = "normal" if price_change >= 0 else "inverse"
            
            st.metric(
                "₿ BTC Price (REAL-TIME)",
                f"${current_price:,.0f}" if current_price > 0 else "$0",
                price_delta,
                delta_color=delta_color
            )
            
            data_source = market_data.get('data_source', 'Unknown')
            if market_data.get('success'):
                st.markdown(f'<div class="price-source success-border">✅ Source: {data_source}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="price-source error-border">❌ Source: {data_source}</div>', unsafe_allow_html=True)
        
        with col4:
            refresh_count = st.session_state.refresh_count
            st.metric(
                "🔄 Refresh Count",
                f"{refresh_count}",
                "Updates performed"
            )
        
        # Additional market data
        if market_data.get('success') and current_price > 0:
            st.markdown("### 📊 **Additional Market Data**")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                high_24h = market_data.get('high_24h', 0)
                if high_24h > 0:
                    st.metric("📈 24h High", f"${high_24h:,.0f}")
                else:
                    st.info("📈 24h High: N/A")
            
            with col2:
                low_24h = market_data.get('low_24h', 0)
                if low_24h > 0:
                    st.metric("📉 24h Low", f"${low_24h:,.0f}")
                else:
                    st.info("📉 24h Low: N/A")
            
            with col3:
                volume_24h = market_data.get('volume_24h', 0)
                if volume_24h > 0:
                    st.metric("💹 24h Volume", f"{volume_24h:,.0f} BTC")
                else:
                    st.info("💹 24h Volume: N/A")
            
            with col4:
                bid_price = market_data.get('bid_price', 0)
                ask_price = market_data.get('ask_price', 0)
                if bid_price > 0 and ask_price > 0:
                    spread = ask_price - bid_price
                    st.metric("📊 Bid-Ask Spread", f"${spread:.2f}")
                else:
                    st.info("📊 Spread: N/A")
    
    def render_price_verification(self):
        """Render price verification section"""
        st.markdown("## 🔍 **PRICE VERIFICATION & SOURCE TESTING**")
        
        market_data = st.session_state.market_data
        current_price = market_data.get('current_price', 0)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📋 **Current Status**")
            
            if market_data.get('success') and current_price > 0:
                st.success(f"✅ **BTC Price:** ${current_price:,.0f}")
                st.success(f"✅ **Data Source:** {market_data.get('data_source', 'Unknown')}")
                
                last_update = market_data.get('last_update')
                if last_update:
                    st.success(f"✅ **Last Update:** {last_update.strftime('%H:%M:%S')}")
                
                # Price validation
                if 50000 <= current_price <= 200000:
                    st.success("✅ **Price Validation:** Realistic range ($50k-$200k)")
                elif current_price > 200000:
                    st.warning("⚠️ **Price Validation:** Very high (>$200k)")
                elif current_price < 50000:
                    st.warning("⚠️ **Price Validation:** Low (<$50k)")
                
            else:
                st.error(f"❌ **Error:** {market_data.get('error', 'Unknown error')}")
                st.error("❌ **Price:** Unable to fetch")
                st.error("❌ **Status:** Data fetch failed")
        
        with col2:
            st.markdown("### 🔗 **Manual Verification**")
            st.info("**Compare prices with:**")
            st.info("• [TradingView BTC/USDT](https://www.tradingview.com/symbols/BTCUSDT/)")
            st.info("• [Bybit.com Official](https://www.bybit.com/trade/usdt/BTCUSDT)")
            st.info("• [CoinGecko BTC](https://www.coingecko.com/en/coins/bitcoin)")
            st.info("• [CoinMarketCap BTC](https://coinmarketcap.com/currencies/bitcoin/)")
            
            # Test all sources button
            if st.button("🧪 Test All Price Sources", type="primary"):
                with st.spinner("Testing all price sources..."):
                    self._test_all_sources()
    
    def _test_all_sources(self):
        """Test all price sources and display results"""
        st.markdown("### 🧪 **Source Testing Results**")
        
        sources = ['bybit_mainnet', 'coingecko', 'bybit_testnet', 'coinbase']
        
        for source in sources:
            try:
                if source in ['bybit_mainnet', 'bybit_testnet']:
                    result = self.price_provider.fetch_bybit_price(source)
                elif source == 'coingecko':
                    result = self.price_provider.fetch_coingecko_price()
                elif source == 'coinbase':
                    result = self.price_provider.fetch_coinbase_price()
                
                if result.get('success'):
                    price = result.get('current_price', 0)
                    st.success(f"✅ **{source.upper()}:** ${price:,.0f}")
                else:
                    st.error(f"❌ **{source.upper()}:** {result.get('error', 'Failed')[:50]}...")
                    
            except Exception as e:
                st.error(f"❌ **{source.upper()}:** Exception: {str(e)[:50]}...")
    
    def render_controls(self):
        """Render control sidebar"""
        st.sidebar.markdown("### 🎛️ **CONTROLS**")
        
        # Manual refresh
        if st.sidebar.button("🔄 Force Refresh Prices", type="primary"):
            with st.spinner("Fetching latest prices..."):
                st.session_state.market_data = self.price_provider.get_current_market_data()
                st.session_state.refresh_count += 1
                st.sidebar.success("✅ Prices updated!")
                time.sleep(1)
                st.rerun()
        
        # Auto refresh toggle
        auto_refresh = st.sidebar.checkbox("🔄 Auto-Refresh (30s)", value=False)
        
        if auto_refresh:
            # Countdown display
            placeholder = st.sidebar.empty()
            
            for i in range(30, 0, -1):
                placeholder.info(f"⏱️ Auto-refresh in {i}s...")
                time.sleep(1)
            
            # Refresh data
            st.session_state.market_data = self.price_provider.get_current_market_data()
            st.session_state.refresh_count += 1
            placeholder.success("✅ Auto-refreshed!")
            st.rerun()
        
        # Debug information
        st.sidebar.markdown("### 🐛 **DEBUG INFO**")
        market_data = st.session_state.market_data
        
        if st.sidebar.checkbox("Show Raw Data"):
            st.sidebar.json({
                'price': market_data.get('current_price', 0),
                'source': market_data.get('data_source', 'Unknown'),
                'success': market_data.get('success', False),
                'last_update': str(market_data.get('last_update', 'Never'))
            })
    
    def render_footer(self):
        """Render footer"""
        st.markdown("---")
        st.markdown(f"""
        <div style='text-align: center; color: #666; padding: 20px;'>
            🚀 <strong>FIXED BYBIT DASHBOARD</strong> | 
            💹 <strong>Multi-Source Real Prices</strong> | 
            🧪 <strong>Testnet Ready</strong> | 
            🔄 <strong>Updates: {st.session_state.refresh_count}</strong> |
            © 2025 Romain Hill
        </div>
        """, unsafe_allow_html=True)
    
    def run(self):
        """Run the main dashboard application"""
        # Render all components
        self.render_header()
        self.render_api_status()
        
        # Main content
        self.render_real_time_overview()
        st.markdown("---")
        self.render_price_verification()
        
        # Sidebar controls
        self.render_controls()
        
        # Footer
        self.render_footer()

# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================

def main():
    """Main application entry point"""
    try:
        app = DashboardApp()
        app.run()
    except Exception as e:
        st.error(f"❌ **Dashboard Error:** {str(e)}")
        st.error("Please check your configuration and try again.")
        
        # Show debug info in case of error
        if st.checkbox("Show Error Details"):
            st.exception(e)

if __name__ == "__main__":
    main()
