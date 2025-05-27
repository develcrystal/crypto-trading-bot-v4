#!/usr/bin/env python3
"""
🚀 Trading Controls Component
Manual Trading Controls and Risk Management
"""

import streamlit as st
import numpy as np
from datetime import datetime


def render_trading_controls(session_state):
    """Render trading controls panel with real trade execution"""
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
                    # Log the status change
                    st.info("Trading paused by user")
                    st.rerun()
            else:
                st.info("⏸️ Trading Bot PAUSED")
                if st.button("▶️ Start Trading", type="primary"):
                    session_state.trading_active = True
                    # Log the status change
                    st.info("Trading activated by user")
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
            # Log the emergency stop
            st.error("🚨 EMERGENCY STOP ACTIVATED!")
            st.rerun()
        
        col2a, col2b = st.columns(2)
        with col2a:
            buy_amount = st.number_input("BUY Amount ($)", min_value=5.0, max_value=25.0, value=10.0, step=1.0)
            if st.button("📈 Manual BUY", disabled=session_state.emergency_stop):
                try:
                    # Import API client here to avoid circular imports
                    from core.api_client import BybitAPI
                    api = BybitAPI()
                    
                    # Calculate quantity based on current price
                    price = session_state.live_data.get('price', 0)
                    if price > 0:
                        qty = buy_amount / price
                        
                        # Execute the buy order
                        order_result = api.place_order(
                            symbol="BTCUSDT", 
                            side="Buy", 
                            order_type="Market", 
                            qty=qty
                        )
                        
                        if order_result.get('success'):
                            st.success(f"✅ Buy order executed: {buy_amount:.2f} USD")
                            # Update position status
                            if 'positions' not in session_state:
                                session_state.positions = []
                            
                            session_state.positions.append({
                                'type': 'LONG',
                                'symbol': 'BTCUSDT',
                                'entry_price': price,
                                'amount': buy_amount,
                                'quantity': qty,
                                'timestamp': datetime.now(),
                                'order_id': order_result.get('order_id', 'manual')
                            })
                        else:
                            st.error(f"❌ Buy order failed: {order_result.get('error', 'Unknown error')}")
                    else:
                        st.error("Cannot determine price for order execution")
                except Exception as e:
                    st.error(f"Error executing buy order: {str(e)}")
        
        with col2b:
            sell_amount = st.number_input("SELL Amount ($)", min_value=5.0, max_value=25.0, value=10.0, step=1.0)
            if st.button("📉 Manual SELL", disabled=session_state.emergency_stop):
                try:
                    # Import API client here to avoid circular imports
                    from core.api_client import BybitAPI
                    api = BybitAPI()
                    
                    # Calculate quantity based on current price
                    price = session_state.live_data.get('price', 0)
                    if price > 0:
                        qty = sell_amount / price
                        
                        # Execute the sell order
                        order_result = api.place_order(
                            symbol="BTCUSDT", 
                            side="Sell", 
                            order_type="Market", 
                            qty=qty
                        )
                        
                        if order_result.get('success'):
                            st.success(f"✅ Sell order executed: {sell_amount:.2f} USD")
                            # Update position status
                            if 'positions' not in session_state:
                                session_state.positions = []
                            
                            session_state.positions.append({
                                'type': 'SHORT',
                                'symbol': 'BTCUSDT',
                                'entry_price': price,
                                'amount': sell_amount,
                                'quantity': qty,
                                'timestamp': datetime.now(),
                                'order_id': order_result.get('order_id', 'manual')
                            })
                        else:
                            st.error(f"❌ Sell order failed: {order_result.get('error', 'Unknown error')}")
                    else:
                        st.error("Cannot determine price for order execution")
                except Exception as e:
                    st.error(f"Error executing sell order: {str(e)}")
    
    # Risk Settings
    with col3:
        st.markdown("""
        <div class="trading-control">
            <h4>⚙️ Risk Settings</h4>
        </div>
        """, unsafe_allow_html=True)
        
        risk_per_trade = st.slider("Risk per Trade (%)", 0.5, 5.0, session_state.get('risk_per_trade', 2.0), 0.1)
        max_drawdown = st.slider("Max Drawdown (%)", 5, 25, session_state.get('max_drawdown', 15), 1)
        
        if st.button("💾 Save Settings"):
            session_state.risk_per_trade = risk_per_trade
            session_state.max_drawdown = max_drawdown
            st.success("✅ Settings saved!")
    
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
        
        # Get actual signal from session state if available
        signal_data = st.session_state.get('current_signal', {})
        signal_strength = signal_data.get('strength', 0)
        signal_filters_passed = signal_data.get('filters_passed', 0)
        signal_confidence = signal_data.get('confidence', 'Low')
        
        if 'current_signal' not in st.session_state:
            # Fallback to random signal only if no real signal available
            signal_strength = min(3, max(0, int(st.session_state.get('trading_active', False) * 3)))
            signal_filters_passed = signal_strength
        
        if signal_strength >= 4:
            st.success("🟢 STRONG BUY SIGNAL")
            st.info(f"{signal_filters_passed}/4 filters passed • High confidence")
        elif signal_strength >= 2:
            st.warning("🟡 WEAK SIGNAL")
            st.info(f"{signal_filters_passed}/4 filters passed • {signal_confidence} confidence")
        else:
            st.info("⚪ NO SIGNAL")
            st.info("Waiting for setup • Market analysis ongoing")
    
    with col2:
        st.markdown("#### 🔍 Filter Status")
        
        # Get actual filter status from session state if available
        filter_status = st.session_state.get('filter_status', {})
        
        # Define the filters to display - use real data if available
        filters = []
        if filter_status:
            for filter_name, status in filter_status.items():
                filters.append((filter_name, status))
        else:
            # Fallback to predefined filters
            filters = [
                ("Volume Filter", True),  # Default to True for Volume Filter
                ("Key Levels", False),    # Example filter status
                ("Pattern Recognition", True),  # Example filter status
                ("Order Flow", True)      # Example filter status
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
