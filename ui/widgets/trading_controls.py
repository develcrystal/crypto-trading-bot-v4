#!/usr/bin/env python3
"""
🚀 Trading Controls Component
Manual Trading Controls and Risk Management
"""

import streamlit as st
import numpy as np


def render_trading_controls(session_state):
    """Render trading controls panel"""
    st.markdown("### 🎮 TRADING CONTROLS")
    
    col1, col2, col3 = st.columns(3)
    
    # Bot Status Control
    with col1:
        st.markdown("""
        <div class="trading-control">
            <h4>🤖 Bot Status</h4>
        </div>
        """, unsafe_allow_html=True)
        
        if session_state.emergency_stop:
            st.error("🛑 EMERGENCY STOP ACTIVE")
            if st.button("🔄 Reset Emergency Stop", type="primary"):
                session_state.emergency_stop = False
                st.rerun()
        else:
            if session_state.trading_active:
                st.success("✅ Trading Bot ACTIVE")
                if st.button("⏸️ Pause Trading"):
                    session_state.trading_active = False
                    st.rerun()
            else:
                st.info("⏸️ Trading Bot PAUSED")
                if st.button("▶️ Start Trading", type="primary"):
                    session_state.trading_active = True
                    st.rerun()
    
    # Quick Actions
    with col2:
        st.markdown("""
        <div class="trading-control">
            <h4>⚡ Quick Actions</h4>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚨 EMERGENCY STOP", key="emergency", help="Stop all trading immediately"):
            session_state.emergency_stop = True
            session_state.trading_active = False
            st.error("🚨 EMERGENCY STOP ACTIVATED!")
            st.rerun()
        
        col2a, col2b = st.columns(2)
        with col2a:
            if st.button("📈 Manual BUY", disabled=session_state.emergency_stop):
                st.info("Manual buy order simulated")
        
        with col2b:
            if st.button("📉 Manual SELL", disabled=session_state.emergency_stop):
                st.info("Manual sell order simulated")
    
    # Risk Settings
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
    
    return {
        'risk_per_trade': risk_per_trade,
        'max_drawdown': max_drawdown
    }


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


def get_trading_controls_styles():
    """Return CSS styles for trading controls"""
    return """
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
    """
