#!/usr/bin/env python3
"""
🚀 MODULAR ADVANCED LIVE TRADING DASHBOARD
Professional Real-time Dashboard für Enhanced Smart Money Bot - MAINNET $50.00
Version: 3.0 - MODULAR & OPTIMIZED

Diese modulare Version teilt die große Dashboard-Datei in wartbare Komponenten auf:
- Widgets für Preis, Order Book, Portfolio
- Layout Manager für Styling und Theme
- Data Manager für Session State
- Chart-Komponente für Smart Money Analysis
"""

import os
import sys

# Set up Python path before any imports
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

# Now import other modules
import streamlit as st
import time
from datetime import datetime

# Import local modules after path setup
from ui.session_init import init_dashboard_session_state

# Initialize session state
init_dashboard_session_state()

# Import modular components
from ui.components.layout_manager import (
    create_responsive_layout, apply_theme, render_main_header,
    render_sidebar_controls, render_refresh_controls, render_footer,
    render_error_state, render_loading_state
)

from ui.components.data_manager import (
    get_data_manager, refresh_dashboard_data, get_50eur_metrics, get_dashboard_status
)

from ui.widgets.price_widget import render_live_price_widget
from ui.widgets.order_book import render_order_book
from ui.widgets.portfolio_monitor import render_portfolio_monitor, render_position_tracking
from ui.widgets.trading_controls import render_trading_controls, render_live_signals
from ui.widgets.trade_history import render_trade_history

from ui.advanced_chart import SmartMoneyChart
from core.api_client import BybitAPI


def render_professional_chart():
    """Render professional trading chart using SmartMoneyChart component"""
    st.markdown("### 📈 SMART MONEY TRADING CHART")
    
    chart_data = st.session_state.chart_data
    
    if chart_data.get('success') and chart_data.get('data') is not None:
        try:
            # Create SmartMoneyChart instance
            api_client = BybitAPI()
            chart = SmartMoneyChart(api_client=api_client, symbol="BTCUSDT", timeframe="5")
            
            # Load data directly from session state
            chart.data = chart_data['data']
            
            # Render the chart with all features
            fig = chart.render_chart(height=600)
            
            if fig:
                # Update layout for better visibility
                fig.update_layout(
                    title='BTC/USDT - Smart Money Concepts (FVG, BOS, ChoCH)',
                    xaxis_title="Time",
                    yaxis_title="Price (USDT)",
                    template="plotly_dark",
                    showlegend=True,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Chart info
                with st.expander("📊 Chart Information", expanded=False):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.info("**Fair Value Gaps (FVG)**\nGreen/Red boxes showing price inefficiencies")
                    
                    with col2:
                        st.info("**Break of Structure (BOS)**\nTriangles showing trend continuation")
                    
                    with col3:
                        st.info("**Change of Character (ChoCH)**\nCircles showing trend reversal points")
            else:
                st.error("Failed to render Smart Money Chart")
                
        except Exception as e:
            st.error(f"Chart rendering error: {str(e)}")
            st.info("Chart data available but rendering failed. Check chart component.")
    
    elif chart_data.get('success') == False:
        st.warning("⚠️ Chart data not available")
        if 'error' in chart_data:
            st.error(f"Error: {chart_data['error']}")
    
    else:
        st.info("📊 Loading chart data...")


def main_dashboard():
    """Main dashboard application with modular components"""
    
    # Set page config FIRST as the very first Streamlit command
    create_responsive_layout()
    
    # Initialize data manager FIRST to setup session state
    data_manager = get_data_manager()
    
    # Apply theme (now dark_mode should exist)
    apply_theme(st.session_state.get('dark_mode', True))
    
    # Render header
    render_main_header()
    
    # Sidebar controls
    auto_refresh = render_sidebar_controls(st.session_state)
    
    # Main refresh controls
    refresh_clicked, main_auto_refresh = render_refresh_controls()
    
    # Handle refresh
    if refresh_clicked:
        with st.spinner("🔄 Refreshing all dashboard data..."):
            success = refresh_dashboard_data()
            if success:
                st.success("✅ Dashboard data refreshed successfully!")
            else:
                st.error("❌ Failed to refresh data. Check API connection.")
            st.rerun()
    
    # Check dashboard status
    dashboard_status = get_dashboard_status()
    
    if not dashboard_status['data_valid']:
        # Show loading or error state
        if dashboard_status['errors']:
            render_error_state('; '.join(dashboard_status['errors']))
        else:
            render_loading_state("Loading dashboard data...")
        
        # Auto-attempt refresh
        if st.button("🔄 Retry Loading Data", type="primary"):
            with st.spinner("Attempting to load data..."):
                refresh_dashboard_data()
                st.rerun()
        
        return
    
    st.markdown("---")
    
    # ==== MAIN DASHBOARD CONTENT ====
    
    # Top Row - Live Price and Order Book
    col1, col2 = st.columns([1, 1])
    
    with col1:
        render_live_price_widget(st.session_state.live_data)
    
    with col2:
        render_order_book(st.session_state.order_book)
    
    st.markdown("---")
    
    # Chart Section
    render_professional_chart()
    
    st.markdown("---")
    
    # Portfolio and Trading Controls
    col1, col2 = st.columns([2, 1])
    
    with col1:
        from ui.components.real_balance import render_real_balances
        render_real_balances()
        
        # Show 50€ optimized metrics
        metrics_50 = get_50eur_metrics()
        
        metric_col1, metric_col2, metric_col3 = st.columns(3)
        
        with metric_col1:
            st.metric(
                "Risk per Trade",
                f"${metrics_50['risk_per_trade']:.2f}",
                "2% of portfolio"
            )
        
        with metric_col2:
            st.metric(
                "Daily Risk Limit",
                f"${metrics_50['daily_risk_limit']:.2f}",
                "5% of portfolio"
            )
        
        with metric_col3:
            st.metric(
                "Emergency Stop",
                f"${metrics_50['emergency_stop_level']:.2f}",
                "15% drawdown limit"
            )
    
    with col2:
        render_live_signals()
    
    st.markdown("---")
    
    # Trading Controls
    trading_settings = render_trading_controls(st.session_state)
    
    # Position tracking if trading is active
    if st.session_state.get('trading_active', False):
        render_position_tracking(st.session_state.trading_active)
    
    # Trade History Table
    st.markdown("---")
    render_trade_history(st.session_state)
    
    # Auto refresh logic
    if auto_refresh or main_auto_refresh:
        refresh_interval = st.session_state.get('refresh_interval', 30)
        
        # Show countdown
        placeholder = st.empty()
        for remaining in range(refresh_interval, 0, -1):
            placeholder.info(f"🔄 Auto-refresh in {remaining} seconds...")
            time.sleep(1)
        
        placeholder.empty()
        st.rerun()
    
    # Footer
    render_footer()
    
    # Status bar
    with st.container():
        st.markdown("---")
        status_col1, status_col2, status_col3, status_col4 = st.columns(4)
        
        with status_col1:
            if dashboard_status['api_connected']:
                st.success("🟢 API Connected")
            else:
                st.error("🔴 API Disconnected")
        
        with status_col2:
            st.info(f"⏰ Last Update: {dashboard_status['last_update']}")
        
        with status_col3:
            if st.session_state.get('trading_active', False):
                st.success("🤖 Bot ACTIVE")
            else:
                st.info("🤖 Bot PAUSED")
        
        with status_col4:
            if st.session_state.get('emergency_stop', False):
                st.error("🚨 EMERGENCY STOP")
            else:
                st.success("✅ Systems Normal")


if __name__ == "__main__":
    try:
        main_dashboard()
    except Exception as e:
        st.error(f"🚨 Dashboard Error: {str(e)}")
        st.markdown("### 🔧 Troubleshooting")
        st.info("""
        **Common Solutions:**
        1. Check API credentials in .env file
        2. Verify internet connection
        3. Restart the dashboard
        4. Check if all required modules are installed
        """)
        
        if st.button("🔄 Restart Dashboard"):
            st.rerun()
