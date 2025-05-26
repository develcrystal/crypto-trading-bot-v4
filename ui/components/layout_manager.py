#!/usr/bin/env python3
"""
🚀 Layout Manager Component
Professional UI Layout and Styling for Trading Dashboard
"""

import streamlit as st


def apply_professional_styling():
    """Apply comprehensive professional trading platform styling"""
    st.markdown("""
    <style>
        /* Professional Trading Platform Styling */
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
        
        /* Dark mode optimizations */
        .dark-mode {
            background-color: #0E1117;
            color: #FFFFFF;
        }
        
        .dark-mode .metric-container {
            background: #1E1E1E;
            border-left-color: #3b82f6;
        }
        
        /* Responsive design */
        @media (max-width: 768px) {
            .main-header h1 {
                font-size: 1.5rem;
            }
            .main-header h2 {
                font-size: 1.2rem;
            }
            .price-widget h1 {
                font-size: 2em !important;
            }
        }
    </style>
    """, unsafe_allow_html=True)


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


def render_main_header():
    """Render professional main header with MAINNET warning"""
    st.markdown("""
    <div class="main-header">
        <h1>🚀 ADVANCED LIVE TRADING DASHBOARD 💰</h1>
        <h2>🔴 LIVE MAINNET - ECHTE $50.00 USDT! 🔴</h2>
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


def render_sidebar_controls(session_state):
    """Render sidebar with theme and refresh controls"""
    with st.sidebar:
        st.markdown("### ⚙️ Dashboard Controls")
        
        # Theme toggle - with safe access
        col1, col2 = st.columns([1, 2])
        with col1:
            # Safe access to dark_mode
            dark_mode = getattr(session_state, 'dark_mode', True)
            st.markdown("🌓" if dark_mode else "☀️", unsafe_allow_html=True)
        with col2:
            if st.button("Dark Mode" if not dark_mode else "Light Mode"):
                session_state.dark_mode = not dark_mode
                st.rerun()
        
        st.markdown("---")
        
        # Auto-refresh settings
        st.markdown("### 🔄 Auto-Refresh")
        auto_refresh = st.checkbox("Enable Auto-Refresh", key="auto_refresh")
        
        if auto_refresh:
            refresh_interval = st.selectbox(
                "Refresh Interval",
                options=[5, 10, 30, 60],
                index=0,
                format_func=lambda x: f"{x} seconds"
            )
            session_state.refresh_interval = refresh_interval
        
        st.markdown("---")
        
        # Dashboard status
        st.markdown("### 📊 Dashboard Status")
        
        # Safe access to live_data
        live_data_success = False
        if hasattr(session_state, 'live_data'):
            live_data_success = getattr(session_state.live_data, 'success', False)
        
        st.success("🟢 API Connected" if live_data_success else "🔴 API Error")
        
        # Safe access to last_update
        last_update = getattr(session_state, 'last_update', 'Never')
        st.info(f"Last Update: {last_update}")
        
        return auto_refresh


def render_refresh_controls():
    """Render refresh controls bar"""
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        refresh_clicked = st.button("🔄 Refresh All Data", type="primary")
    
    with col2:
        auto_refresh = st.checkbox("Auto-Refresh (30s)", key="main_auto_refresh")
    
    with col3:
        st.markdown('<div class="live-indicator">🟢 LIVE</div>', unsafe_allow_html=True)
    
    return refresh_clicked, auto_refresh


def render_footer():
    """Render professional footer"""
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        🚀 <strong>ADVANCED LIVE TRADING DASHBOARD</strong> | 
        💹 <strong>Enhanced Smart Money Strategy</strong> | 
        🔴 <strong>LIVE TRADING READY</strong> | 
        © 2025 Professional Trading System
    </div>
    """, unsafe_allow_html=True)


def create_responsive_layout():
    """Create responsive layout structure"""
    # Set page config for optimal layout
    st.set_page_config(
        page_title="🚀 Advanced Live Trading Dashboard - MAINNET $50.00",
        page_icon="💰",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Apply professional styling
    apply_professional_styling()


def render_error_state(error_message):
    """Render error state with retry options"""
    st.error(f"❌ Dashboard Error: {error_message}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Retry Connection", type="primary"):
            st.rerun()
    
    with col2:
        if st.button("📧 Report Issue"):
            st.info("Please check your API credentials and network connection.")


def render_loading_state(message="Loading dashboard data..."):
    """Render loading state"""
    with st.spinner(message):
        # Show loading placeholder
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info("📊 Loading market data...")
        
        with col2:
            st.info("💰 Loading portfolio...")
        
        with col3:
            st.info("📈 Loading charts...")
