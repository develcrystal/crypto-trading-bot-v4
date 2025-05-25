import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go

# Simple Page Config
st.set_page_config(page_title="Crypto Bot", layout="wide")

# Simple Demo Data
def get_data():
    return {
        "portfolio": 10567.43,
        "pnl": 567.43,
        "trades": 15,
        "win_rate": 78.5,
        "current_price": 106450
    }

# Main Dashboard
st.title("🚀 Enhanced Smart Money Bot Dashboard")

data = get_data()

# Metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("💰 Portfolio", f"${data['portfolio']:,.2f}", f"+${data['pnl']:,.2f}")
with col2:
    st.metric("📊 Trades", data['trades'], "+3 today")
with col3:
    st.metric("🏆 Win Rate", f"{data['win_rate']:.1f}%", "↗️")
with col4:
    st.metric("💎 BTC Price", f"${data['current_price']:,}", "+1.2%")

# Charts
st.subheader("📈 Performance Chart")

# Generate sample data
dates = pd.date_range(start=datetime.now() - timedelta(days=30), periods=30)
values = 10000 + np.cumsum(np.random.normal(20, 50, 30))

fig = go.Figure()
fig.add_trace(go.Scatter(x=dates, y=values, mode='lines', name='Portfolio Value'))
fig.update_layout(title="Portfolio Performance", height=400)
st.plotly_chart(fig, use_container_width=True)

# Market Regime
st.subheader("🧠 Market Regime")
col1, col2 = st.columns(2)
with col1:
    st.success("Current Regime: BULL MARKET 🚀")
    st.info("Confidence: 85%")
with col2:
    st.metric("Volume Threshold", "80k BTC", "-20% (Bull Mode)")

# Recent Trades
st.subheader("📋 Recent Trades")
trades_df = pd.DataFrame({
    'Time': ['14:30:22', '13:15:11', '12:42:33'],
    'Signal': ['BUY', 'SELL', 'BUY'],
    'Price': ['$106,450', '$106,200', '$105,950'],
    'PnL': ['+$47.50', '+$62.00', '+$35.20'],
    'Status': ['CLOSED', 'CLOSED', 'CLOSED']
})
st.dataframe(trades_df, hide_index=True)

# Sidebar
st.sidebar.title("🎛️ Controls")
auto_refresh = st.sidebar.checkbox("Auto-Refresh", value=True)
if auto_refresh:
    st.sidebar.success("🔄 Refreshing...")
    
st.sidebar.markdown("### 📡 Status")
st.sidebar.success("✅ Demo Mode Active")
st.sidebar.info("📊 Simulated Data")

st.sidebar.markdown("### 🚨 Emergency")
if st.sidebar.button("🛑 Emergency Stop"):
    st.sidebar.error("🚨 STOPPED!")

# Footer
st.markdown("---")
st.markdown("🚀 Enhanced Smart Money Trading Bot V2 | © 2025 Romain Hill")
