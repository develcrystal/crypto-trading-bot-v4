import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time

# Set page config for wide layout and dark theme
st.set_page_config(
    page_title="Advanced Live Trading Dashboard",
    page_icon="🚀", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #e74c3c 0%, #c0392b 100%);
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
        color: white;
        text-align: center;
        border: 2px solid #fff;
        box-shadow: 0 4px 15px rgba(231, 76, 60, 0.4);
    }
    
    .mainnet-warning {
        background: linear-gradient(90deg, #f39c12, #e67e22);
        color: white;
        padding: 10px;
        border-radius: 8px;
        text-align: center;
        font-weight: bold;
        margin: 10px 0;
        animation: pulse 3s infinite;
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
        text-align: center;
        padding: 20px;
        border-radius: 10px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin: 10px 0;
    }
    
    .order-book {
        font-family: monospace;
        font-size: 12px;
    }
    
    .buy-price {
        color: #10b981;
        font-weight: bold;
    }
    
    .sell-price {
        color: #ef4444;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Initialize API with correct import handling
@st.cache_resource
def get_api_client():
    try:
        from corrected_live_api import LiveBybitAPI
        return LiveBybitAPI()
    except ImportError as e:
        print(f"Warning: corrected_live_api import failed: {str(e)}")
        try:
            from live_bybit_api import LiveBybitAPI
            print("Using live_bybit_api as fallback")
            return LiveBybitAPI()
        except ImportError as e:
            print(f"Error: Both API imports failed: {str(e)}")
            return None

# Get LIVE account data
@st.cache_data(ttl=30)
def get_live_account_data():
    """Get REAL account data - NO SIMULATION!"""
    try:
        api_client = get_api_client()
        if api_client is None:
            return {'success': False, 'error': 'API client not available'}
        dashboard_data = api_client.get_dashboard_data()
        print(f"Dashboard data received: {dashboard_data}")  # Debug output
        return dashboard_data
    except Exception as e:
        print(f"Error in get_live_account_data: {str(e)}")  # Debug output
        return {'success': False, 'error': str(e)}

def apply_theme(dark_mode):
    """Apply theme to the app"""
    if dark_mode:
        st.markdown("""
        <style>
            .stApp {
                background-color: #0E1117;
                color: #FFFFFF;
            }
            .css-1d391kg, .css-1y4q8m0 {
                background-color: #1E1E1E !important;
                color: #FFFFFF !important;
            }
        </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
            .stApp {
                background-color: #FFFFFF;
                color: #000000;
            }
            .css-1d391kg, .css-1y4q8m0 {
                background-color: #F8FAFC !important;
                color: #1E293B !important;
            }
        </style>
        """, unsafe_allow_html=True)

# Initialize session state
def initialize_session_state():
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.live_data = {}
        st.session_state.account_balance = {}
        st.session_state.order_book = {}
        st.session_state.chart_data = {}
        st.session_state.last_update = None
        st.session_state.refresh_interval = 5  # seconds
        st.session_state.auto_refresh = True
        st.session_state.trading_enabled = False
        st.session_state.emergency_stop = False
        st.session_state.dark_mode = True  # Default to dark mode
    
    if 'live_data' not in st.session_state:
        st.session_state.live_data = {'success': False}
    
    if 'order_book' not in st.session_state:
        st.session_state.order_book = {'success': False}
    
    if 'account_balance' not in st.session_state:
        st.session_state.account_balance = {'success': False}
    
    if 'chart_data' not in st.session_state:
        st.session_state.chart_data = {'success': False}
    
    if 'trading_active' not in st.session_state:
        st.session_state.trading_active = False
    
    if 'emergency_stop' not in st.session_state:
        st.session_state.emergency_stop = False

def refresh_all_data():
    """Refresh all dashboard data using LiveBybitAPI"""
    try:
        # Get live account data
        dashboard_data = get_live_account_data()
        print(f"Dashboard data received: {dashboard_data}")  # Debug output
        
        if dashboard_data['success']:
            # Store live ticker data
            st.session_state.live_data = {
                'success': True,
                'price': dashboard_data.get('btc_price', 0),
                'change_24h': dashboard_data.get('btc_change_24h', 0),
                'high_24h': dashboard_data.get('btc_high_24h', 0),
                'low_24h': dashboard_data.get('btc_low_24h', 0),
                'volume_24h': dashboard_data.get('btc_volume_24h', 0),
                'bid': dashboard_data.get('bid', 0),
                'ask': dashboard_data.get('ask', 0),
                'timestamp': datetime.now()
            }
            
            # Store account balance
            st.session_state.account_balance = {
                'success': True,
                'portfolio_value': dashboard_data.get('portfolio_value', 0),
                'balances': dashboard_data.get('balances', {})
            }
            
            # Store order book
            st.session_state.order_book = {
                'success': True,
                'bids': dashboard_data.get('order_book_bids', []),
                'asks': dashboard_data.get('order_book_asks', []),
                'timestamp': datetime.now()
            }
            
            # Load chart data
            try:
                api_client = get_api_client()
                if api_client:
                    chart_data = api_client.get_kline_data("BTCUSDT", "5", 100)
                    print(f"Chart data received: {chart_data}")  # Debug output
                    
                    if chart_data.get('success'):
                        st.session_state.chart_data = chart_data
                    else:
                        st.session_state.chart_data = {'success': False, 'error': 'Failed to load chart data'}
                else:
                    st.session_state.chart_data = {'success': False, 'error': 'API client not available'}
            except Exception as e:
                st.session_state.chart_data = {'success': False, 'error': str(e)}
                print(f"Chart data error: {str(e)}")  # Debug output
        else:
            error_msg = dashboard_data.get('error', 'Unknown API error')
            st.session_state.live_data = {'success': False, 'error': error_msg}
            st.session_state.account_balance = {'success': False, 'error': error_msg}
            st.session_state.order_book = {'success': False, 'error': error_msg}
            st.session_state.chart_data = {'success': False, 'error': error_msg}
            print(f"Dashboard data error: {error_msg}")  # Debug output
            
    except Exception as e:
        print(f"Error in refresh_all_data: {str(e)}")  # Debug output
        st.session_state.live_data = {'success': False, 'error': str(e)}
        st.session_state.account_balance = {'success': False, 'error': str(e)}
        st.session_state.order_book = {'success': False, 'error': str(e)}
        st.session_state.chart_data = {'success': False, 'error': str(e)}

def render_main_header():
    """Render professional main header with MAINNET warning"""
    st.markdown("""
    <div class="main-header">
        <h1>🚀 ADVANCED LIVE TRADING DASHBOARD 💰</h1>
        <h2>🔴 LIVE MAINNET - ECHTE $83.38 USDT! 🔴</h2>
        <p style="font-size: 1.1rem; margin-top: 10px;">
            Enhanced Smart Money Strategy • Professional Trading Interface • Real Money
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # MAINNET warning
    st.markdown("""
    <div class="mainnet-warning">
        ⚠️ MAINNET MODE - REAL MONEY AT RISK! NO SIMULATION! ⚠️
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

def render_account_overview():
    """Render account balance and portfolio overview"""
    st.markdown("### 💼 LIVE PORTFOLIO OVERVIEW")
    
    account_data = st.session_state.account_balance
    
    if account_data.get('success'):
        portfolio_value = account_data.get('portfolio_value', 0)
        balances = account_data.get('balances', {})
        
        # Main portfolio value
        st.markdown(f"""
        <div class="metric-container">
            <h2>💰 Portfolio Value: ${portfolio_value:.2f} USDT</h2>
            <p>Live Balance - Real Money Trading Account</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Balance breakdown
        if balances:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                usdt_balance = balances.get('USDT', 0)
                st.metric("💵 USDT Balance", f"${usdt_balance:.2f}", "Available for Trading")
            
            with col2:
                btc_balance = balances.get('BTC', 0)
                st.metric("₿ BTC Balance", f"{btc_balance:.8f}", "Bitcoin Holdings")
            
            with col3:
                # Calculate total value in USDT
                total_crypto = sum(balances.values()) - balances.get('USDT', 0)
                st.metric("🔄 Crypto Value", f"${total_crypto:.2f}", "Non-USDT Assets")
    else:
        st.error("❌ Unable to fetch account data")
        st.error(f"Error: {account_data.get('error', 'Unknown error')}")

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
    """Render professional trading chart with candlestick data"""
    st.markdown("### 📈 LIVE TRADING CHART")
    
    chart_data = st.session_state.get('chart_data', {'success': False})
    
    if chart_data.get('success') and chart_data.get('data') is not None:
        # Create simple candlestick chart with plotly
        try:
            import pandas as pd
            
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
                    title='BTC/USDT Live Chart',
                    xaxis_title='Time',
                    yaxis_title='Price (USDT)',
                    height=400,
                    template='plotly_dark'
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.error("❌ Invalid chart data format")
        except Exception as e:
            st.error(f"❌ Chart rendering error: {str(e)}")
    else:
        st.warning("📊 Chart data loading...")
        if chart_data.get('error'):
            st.error(f"Error: {chart_data['error']}")

def render_trading_controls():
    """Render trading bot controls"""
    st.markdown("### 🎮 TRADING CONTROLS")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🟢 START BOT", key="start_bot"):
            st.session_state.trading_active = True
            st.success("✅ Trading Bot Started!")
    
    with col2:
        if st.button("🔴 STOP BOT", key="stop_bot"):
            st.session_state.trading_active = False
            st.warning("⚠️ Trading Bot Stopped!")
    
    with col3:
        if st.button("🚨 EMERGENCY STOP", key="emergency_stop_button"):
         st.session_state.trading_active = False
         st.error("🚨 EMERGENCY STOP ACTIVATED!")
    
    with col4:
        if st.button("🔄 REFRESH DATA", key="refresh_data"):
            refresh_all_data()
            st.info("🔄 Data refreshed!")
    
    # Status indicators
    st.markdown("#### 📊 Status")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status = "🟢 AKTIV" if st.session_state.get('trading_active', False) else "🔴 INAKTIV"
        st.markdown(f"**Bot Status:** {status}")
    
    with col2:
        emergency = "🚨 JA" if st.session_state.get('emergency_stop', False) else "✅ NEIN"
        st.markdown(f"**Emergency Stop:** {emergency}")
    
    with col3:
        last_update = st.session_state.get('last_update', 'Never')
        st.markdown(f"**Last Update:** {last_update}")

# Main App
def main():
    # Initialize session state
    initialize_session_state()
    
    # Apply theme
    apply_theme(st.session_state.get('dark_mode', True))
    
    # Render main header
    render_main_header()
    
    # Auto-refresh logic
    if st.session_state.get('auto_refresh', True):
        refresh_all_data()
        st.session_state.last_update = datetime.now().strftime("%H:%M:%S")
    
    # Main content layout
    tab1, tab2, tab3, tab4 = st.tabs(["Live Data", "Portfolio", "Charts", "Controls"])
    current_tab = st.session_state.get('current_tab', 'Live Data')
    
    if current_tab == "Live Data":
        with tab1:
            render_live_price_widget()
            st.markdown("---")
            render_order_book()
    elif current_tab == "Portfolio":
        with tab2:
            render_account_overview()
    elif current_tab == "Charts":
        with tab3:
            render_professional_chart()
    elif current_tab == "Controls":
        with tab4:
            render_trading_controls()
    
    st.session_state.current_tab = current_tab
    
    # Auto-refresh mechanism
    time.sleep(5)
    st.rerun()

if __name__ == "__main__":
    main()
