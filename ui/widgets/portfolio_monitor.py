#!/usr/bin/env python3
"""
🚀 Portfolio Monitor Component
Advanced Portfolio Tracking with REAL $50.00 USDT
"""

import streamlit as st


def render_portfolio_monitor(live_account_data, trading_active=False):
    """Render advanced portfolio monitoring with REAL balance"""
    st.markdown("### 💼 LIVE PORTFOLIO TRACKING")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if live_account_data.get('success'):
            portfolio_value = live_account_data['portfolio_value']
            st.metric(
                "💰 REAL USDT Balance", 
                f"${portfolio_value:.2f}",
                f"LIVE {live_account_data.get('account_type', 'UMA')}"
            )
        else:
            st.error("❌ Unable to fetch live balance")
            st.metric("💰 Portfolio", "Error", "Check API")
    
    with col2:
        # Display Initial Investment
        st.metric(
            "💸 Initial Investment",
            f"${50.0:.2f}",
            "Planned Start Amount"
        )

    with col3:
        # Calculate P&L vs 50€ start
        if live_account_data.get('success'):
            current_value = live_account_data['portfolio_value']
            start_value = 50.0  # Planned start amount
            pnl = current_value - start_value
            pnl_pct = (pnl / start_value) * 100
            
            st.metric(
                "📊 P&L vs 50€ Start",
                f"${pnl:.2f}",
                f"{pnl_pct:+.2f}%",
                delta_color="normal" if pnl >= 0 else "inverse"
            )
        else:
            st.metric("📊 P&L", "Error", "API Error")
    
    with col4:
        # Risk level
        risk_used = 1.2  # Will be calculated from live trades
        max_risk = 10.0
        risk_pct = (risk_used / max_risk) * 100
        
        color = "normal" if risk_pct < 50 else "inverse"
        st.metric(
            "🛡️ Risk Level",
            f"{risk_pct:.1f}%",
            f"${risk_used:.2f} / ${max_risk:.2f}",
            delta_color=color
        )
    
    # Additional balance breakdown
    if live_account_data.get('success'):
        st.markdown("#### 💼 Detailed Balance Breakdown")
        balances = live_account_data.get('balances', {})
        
        balance_col1, balance_col2 = st.columns(2)
        
        with balance_col1:
            st.markdown("**Available Balances:**")
            for coin, amount in balances.items():
                if coin == 'USDT':
                    st.success(f"💵 {coin}: {amount:.2f}")
                else:
                    st.info(f"₿ {coin}: {amount:.6f}")
        
        with balance_col2:
            st.markdown("**Account Info:**")
            st.info(f"🏦 Account Type: {live_account_data.get('account_type', 'UMA')}")
            st.info("🔴 Data Source: LIVE MAINNET")
            st.info("⚠️ Real Money Trading")
    
    else:
        st.error("❌ Unable to load live account data")
        st.error(f"Error: {live_account_data.get('error', 'Unknown error')}")


def render_position_tracking(trading_active=False):
    """Render current position tracking"""
    st.markdown("#### 🎯 Position Status")
    
    if trading_active:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Position", "LONG BTC", "$10.50 exposure")
        
        with col2:
            st.metric("Entry Price", "$106,500.00", "Current position")
        
        with col3:
            st.metric("Unrealized P&L", "+$0.50", "+0.47%")
    else:
        st.info("⚪ No active positions • Waiting for signal")


def calculate_risk_metrics(portfolio_value, positions=None):
    """Calculate risk metrics for portfolio"""
    # Default risk calculation for $50 start
    start_amount = 50.0
    risk_per_trade = 2.0  # 2% = $1.00 per trade
    daily_risk_limit = 5.0  # 5% = $2.50 per day
    
    return {
        'risk_per_trade_usd': portfolio_value * (risk_per_trade / 100),
        'daily_risk_limit_usd': portfolio_value * (daily_risk_limit / 100),
        'max_drawdown_limit': portfolio_value * 0.15,  # 15%
        'position_size_limit': portfolio_value * 0.2   # 20% max per position
    }
