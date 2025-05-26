#!/usr/bin/env python3
"""
🚀 SESSION STATE INITIALIZER
Garantiert sichere Initialisierung aller Session State Variablen
"""

import streamlit as st


def init_dashboard_session_state():
    """Initialize all dashboard session state variables safely"""
    
    # Core state variables
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
    
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = True
    
    if 'auto_refresh' not in st.session_state:
        st.session_state.auto_refresh = True
    
    if 'refresh_interval' not in st.session_state:
        st.session_state.refresh_interval = 30
    
    if 'last_update' not in st.session_state:
        st.session_state.last_update = None
    
    # Trading state
    if 'trading_active' not in st.session_state:
        st.session_state.trading_active = False
    
    if 'emergency_stop' not in st.session_state:
        st.session_state.emergency_stop = False
    
    if 'trading_enabled' not in st.session_state:
        st.session_state.trading_enabled = False
    
    # Data state
    if 'live_data' not in st.session_state:
        st.session_state.live_data = {'success': False}
    
    if 'account_balance' not in st.session_state:
        st.session_state.account_balance = {'success': False}
    
    if 'order_book' not in st.session_state:
        st.session_state.order_book = {'success': False}
    
    if 'chart_data' not in st.session_state:
        st.session_state.chart_data = {'success': False}
    
    return True


# Auto-initialize when imported
init_dashboard_session_state()
