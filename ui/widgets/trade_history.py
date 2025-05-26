#!/usr/bin/env python3
"""
📋 Trade History Component
Tabelle mit allen abgeschlossenen und laufenden Trades
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import numpy as np


def render_trade_history(session_state, trade_data=None):
    """
    Render a table with trade history
    
    Args:
        session_state: Streamlit session state
        trade_data: Optional DataFrame with trade data
    """
    st.markdown("### 📋 TRADE HISTORY")
    
    # Initialize dummy data if not provided
    if trade_data is None:
        # Check if we have trade data in the session state
        if 'trade_history' not in session_state:
            session_state.trade_history = create_sample_trade_history()
        
        trade_data = session_state.trade_history
    
    # Filters for trade history
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status_filter = st.selectbox(
            "Status Filter",
            ["All", "Open", "Closed", "Win", "Loss"],
            key="trade_status_filter"
        )
    
    with col2:
        date_filter = st.selectbox(
            "Date Filter",
            ["All Time", "Today", "This Week", "This Month"],
            key="trade_date_filter"
        )
    
    with col3:
        side_filter = st.selectbox(
            "Side Filter",
            ["All", "Buy", "Sell"],
            key="trade_side_filter"
        )
    
    with col4:
        min_profit = st.number_input(
            "Min. Profit ($)",
            min_value=-10.0,
            max_value=10.0,
            value=-10.0,
            step=0.5,
            key="trade_min_profit"
        )
    
    # Apply filters
    filtered_data = trade_data.copy()
    
    # Status filter
    if status_filter == "Open":
        filtered_data = filtered_data[filtered_data['Status'] == 'Open']
    elif status_filter == "Closed":
        filtered_data = filtered_data[filtered_data['Status'] == 'Closed']
    elif status_filter == "Win":
        filtered_data = filtered_data[(filtered_data['Status'] == 'Closed') & (filtered_data['PnL'] > 0)]
    elif status_filter == "Loss":
        filtered_data = filtered_data[(filtered_data['Status'] == 'Closed') & (filtered_data['PnL'] < 0)]
    
    # Date filter
    now = datetime.now()
    today_start = datetime(now.year, now.month, now.day, 0, 0, 0)
    
    if date_filter == "Today":
        filtered_data = filtered_data[filtered_data['Time'] >= today_start]
    elif date_filter == "This Week":
        week_start = today_start - timedelta(days=now.weekday())
        filtered_data = filtered_data[filtered_data['Time'] >= week_start]
    elif date_filter == "This Month":
        month_start = datetime(now.year, now.month, 1, 0, 0, 0)
        filtered_data = filtered_data[filtered_data['Time'] >= month_start]
    
    # Side filter
    if side_filter == "Buy":
        filtered_data = filtered_data[filtered_data['Side'] == 'Buy']
    elif side_filter == "Sell":
        filtered_data = filtered_data[filtered_data['Side'] == 'Sell']
    
    # Profit filter
    filtered_data = filtered_data[filtered_data['PnL'] >= min_profit]
    
    # Render the trade table
    if not filtered_data.empty:
        # Format the dataframe for display
        display_df = filtered_data.copy()
        
        # Format Time column
        display_df['Time'] = display_df['Time'].dt.strftime('%Y-%m-%d %H:%M')
        
        # Format numeric columns
        display_df['Entry'] = display_df['Entry'].map('${:,.2f}'.format)
        display_df['Exit'] = display_df['Exit'].map(lambda x: '${:,.2f}'.format(x) if pd.notna(x) else 'Open')
        display_df['PnL'] = display_df['PnL'].map(lambda x: '${:+,.2f}'.format(x) if pd.notna(x) else '-')
        
        # Color code based on PnL or Status
        def highlight_trades(row):
            if row['Status'] == 'Open':
                return ['background-color: #374151'] * len(row)
            elif row['PnL'] > 0:
                return ['background-color: rgba(5, 150, 105, 0.2)'] * len(row)
            elif row['PnL'] < 0:
                return ['background-color: rgba(220, 38, 38, 0.2)'] * len(row)
            return [''] * len(row)
        
        # Apply styling and display
        styled_df = display_df.style.apply(highlight_trades, axis=1)
        st.dataframe(styled_df, use_container_width=True)
        
        # Trade statistics
        st.markdown("#### 📊 Trading Statistics")
        
        stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
        
        with stat_col1:
            num_trades = len(filtered_data)
            win_trades = len(filtered_data[(filtered_data['Status'] == 'Closed') & (filtered_data['PnL'] > 0)])
            loss_trades = len(filtered_data[(filtered_data['Status'] == 'Closed') & (filtered_data['PnL'] < 0)])
            
            closed_trades = win_trades + loss_trades
            win_rate = (win_trades / closed_trades * 100) if closed_trades > 0 else 0
            
            st.metric("Win Rate", f"{win_rate:.1f}%", f"{win_trades}/{closed_trades} trades")
        
        with stat_col2:
            total_pnl = filtered_data['PnL'].sum()
            st.metric("Total P&L", f"${total_pnl:.2f}", "From filtered trades")
        
        with stat_col3:
            avg_win = filtered_data[filtered_data['PnL'] > 0]['PnL'].mean() if len(filtered_data[filtered_data['PnL'] > 0]) > 0 else 0
            avg_loss = filtered_data[filtered_data['PnL'] < 0]['PnL'].mean() if len(filtered_data[filtered_data['PnL'] < 0]) > 0 else 0
            
            st.metric("Avg Win", f"${avg_win:.2f}", "Per winning trade")
        
        with stat_col4:
            st.metric("Avg Loss", f"${avg_loss:.2f}", "Per losing trade")
        
        # Download trade history button
        if st.button("📥 Export Trade History"):
            csv = filtered_data.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"trade_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
            )
    else:
        st.info("No trades match the selected filters.")


def create_sample_trade_history():
    """Create sample trade history data for testing"""
    # Current time
    now = datetime.now()
    
    # Sample data
    data = {
        'ID': range(1, 11),
        'Time': [
            now - timedelta(hours=1),
            now - timedelta(hours=3),
            now - timedelta(hours=6),
            now - timedelta(hours=12),
            now - timedelta(days=1),
            now - timedelta(days=1, hours=6),
            now - timedelta(days=2),
            now - timedelta(days=3),
            now - timedelta(days=4),
            now - timedelta(days=5),
        ],
        'Side': ['Buy', 'Sell', 'Buy', 'Sell', 'Buy', 'Buy', 'Sell', 'Buy', 'Sell', 'Buy'],
        'Symbol': ['BTCUSDT'] * 10,
        'Size': [0.0001, 0.0002, 0.0001, 0.0001, 0.0002, 0.0001, 0.0001, 0.0002, 0.0001, 0.0001],
        'Entry': [
            106500.00,
            106800.00,
            106200.00,
            105900.00,
            107100.00,
            107400.00,
            107800.00,
            108200.00,
            108500.00,
            108900.00
        ],
        'Exit': [
            106700.00,
            106600.00,
            106400.00,
            105700.00,
            107300.00,
            107200.00,
            107600.00,
            None,
            None,
            None
        ],
        'PnL': [
            0.20,
            0.40,
            0.20,
            -0.20,
            0.40,
            -0.20,
            -0.20,
            None,
            None,
            None
        ],
        'Status': ['Closed', 'Closed', 'Closed', 'Closed', 'Closed', 'Closed', 'Closed', 'Open', 'Open', 'Open'],
        'Regime': ['Bull', 'Bull', 'Bull', 'Sideways', 'Bull', 'Bull', 'Bear', 'Bull', 'Bull', 'Bull']
    }
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    return df


def get_trade_history_styles():
    """Return CSS styles for trade history component"""
    return """
    .trade-history-table {
        font-family: monospace;
    }
    
    .positive-pnl {
        color: #10b981 !important;
        font-weight: bold;
    }
    
    .negative-pnl {
        color: #ef4444 !important;
        font-weight: bold;
    }
    
    .open-trade {
        color: #3b82f6 !important;
        font-style: italic;
    }
    """


if __name__ == "__main__":
    st.set_page_config(page_title="Trade History Test", layout="wide")
    render_trade_history(st.session_state)
