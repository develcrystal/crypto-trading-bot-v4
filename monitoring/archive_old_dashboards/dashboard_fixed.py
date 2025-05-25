"""
🚀 CRYPTO TRADING BOT V2 - MONITORING DASHBOARD
Fixed Version - Robuste Demo-Daten ohne Config-Probleme
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
import numpy as np
from typing import Dict, List, Optional

# Streamlit Page Configuration
st.set_page_config(
    page_title="🚀 Crypto Bot Monitoring",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #FF6B6B, #4ECDC4);
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        color: white;
        margin-bottom: 2rem;
    }
    .metric-container {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .status-good { color: #28a745; }
    .status-warning { color: #ffc107; }
    .status-danger { color: #dc3545; }
</style>
""", unsafe_allow_html=True)

def get_demo_data() -> Dict:
    """Generate realistic demo data"""
    base_time = datetime.now()
    base_price = 106500 + np.random.normal(0, 500)
    portfolio_change = np.random.normal(0.02, 0.01)
    
    return {
        "portfolio_value": 10000 * (1 + portfolio_change),
        "pnl": 10000 * portfolio_change,
        "daily_pnl": np.random.normal(50, 100),
        "current_price": base_price,
        "market_regime": {
            "regime": np.random.choice(["BULL", "BEAR", "SIDEWAYS"], p=[0.5, 0.2, 0.3]),
            "confidence": np.random.uniform(0.6, 0.95),
            "bull_score": np.random.randint(4, 8),
            "bear_score": np.random.randint(1, 5),
            "sideways_score": np.random.randint(1, 4)
        },
        "trades_today": np.random.randint(8, 25),
        "trades_won": np.random.randint(6, 20),
        "win_rate": np.random.uniform(0.65, 0.85),
        "last_signal": {
            "type": np.random.choice(["BUY", "SELL", "HOLD"]),
            "time": base_time - timedelta(minutes=np.random.randint(1, 120)),
            "price": base_price + np.random.normal(0, 100),
            "strength": np.random.uniform(0.6, 1.0)
        },
        "filter_status": {
            "volume": np.random.choice([True, False], p=[0.7, 0.3]),
            "key_levels": np.random.choice([True, False], p=[0.8, 0.2]),
            "pattern": np.random.choice([True, False], p=[0.6, 0.4]),
            "order_flow": np.random.choice([True, False], p=[0.5, 0.5]),
            "liquidity_sweep": np.random.choice([True, False], p=[0.3, 0.7])
        },
        "risk_metrics": {
            "current_exposure": np.random.uniform(1500, 3500),
            "daily_risk_used": np.random.uniform(100, 800),
            "current_drawdown": np.random.uniform(0, 8)
        },
        "last_update": base_time,
        "is_live": False
    }

def create_main_overview(data: Dict):
    """Create main overview panel"""
    st.markdown('<div class="main-header"><h1>🚀 ENHANCED SMART MONEY BOT</h1><h3>Live Trading Dashboard</h3></div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        delta_pnl = f"{data['pnl']:+,.2f} USD"
        st.metric(
            label="💰 Portfolio PnL",
            value=f"${data['portfolio_value']:,.2f}",
            delta=delta_pnl
        )
    
    with col2:
        total_trades = data["trades_today"]
        won_trades = data["trades_won"]
        st.metric(
            label="📊 Trades Heute",
            value=f"{total_trades}",
            delta=f"{won_trades}W/{total_trades-won_trades}L"
        )
    
    with col3:
        win_rate = data["win_rate"] * 100
        st.metric(
            label="🏆 Win Rate",
            value=f"{win_rate:.1f}%",
            delta="↗️" if win_rate > 70 else "→"
        )
    
    with col4:
        regime_data = data["market_regime"]
        regime = regime_data["regime"]
        confidence = regime_data["confidence"]
        regime_emoji = {"BULL": "🚀", "BEAR": "🐻", "SIDEWAYS": "↔️"}[regime]
        st.metric(
            label="🧠 Market Regime",
            value=f"{regime_emoji} {regime}",
            delta=f"Conf: {confidence:.2f}"
        )

def create_market_regime_panel(data: Dict):
    """Create market regime detection panel"""
    st.subheader("📈 Market Regime Analysis")
    
    regime_data = data["market_regime"]
    regime = regime_data["regime"]
    confidence = regime_data["confidence"]
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        regime_colors = {"BULL": "#28a745", "BEAR": "#dc3545", "SIDEWAYS": "#ffc107"}
        
        st.markdown(f"""
        **Current Regime:** <span style="color: {regime_colors[regime]}; font-size: 1.2em; font-weight: bold;">{regime}</span>  
        **Confidence:** {confidence:.2%}  
        **Duration:** {np.random.randint(30, 180)} minutes
        """, unsafe_allow_html=True)
        
        bull_score = regime_data["bull_score"]
        bear_score = regime_data["bear_score"]
        sideways_score = regime_data["sideways_score"]
        
        st.markdown("**Regime Scoring:**")
        st.progress(bull_score / 8, text=f"🟢 Bull Score: {bull_score}/8")
        st.progress(bear_score / 8, text=f"📉 Bear Score: {bear_score}/8") 
        st.progress(sideways_score / 5, text=f"↔️ Sideways Score: {sideways_score}/5")
    
    with col2:
        st.markdown("**Adaptive Parameters:**")
        
        if regime == "BULL":
            st.success("• Volume: 100k → 80k (-20%)")
            st.success("• R:R Ratio: 1.5:1 → 1.8:1 (+20%)")
            st.success("• Liquidity Focus: Enhanced")
        elif regime == "BEAR":
            st.error("• Volume: 100k → 120k (+20%)")
            st.error("• R:R Ratio: 1.5:1 → 1.4:1 (-10%)")
            st.error("• Conservative Mode: ON")
        else:
            st.warning("• Volume: 100k → 150k (+50%)")
            st.warning("• R:R Ratio: 1.5:1 (Standard)")
            st.warning("• Maximum Selectivity: ON")

def create_live_signals_panel(data: Dict):
    """Create live signals and filters panel"""
    st.subheader("⚡ Live Signals & Filters")
    
    last_signal = data["last_signal"]
    signal_type = last_signal["type"]
    signal_time = last_signal["time"]
    signal_price = last_signal["price"]
    signal_strength = last_signal["strength"]
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        signal_colors = {"BUY": "green", "SELL": "red", "HOLD": "orange"}
        time_ago = datetime.now() - signal_time
        minutes_ago = int(time_ago.total_seconds() / 60)
        
        st.markdown(f"""
        **Last Signal:** <span style="color: {signal_colors[signal_type]}; font-weight: bold;">{signal_type}</span> at ${signal_price:,.0f}  
        **Time:** {minutes_ago} min ago  
        **Strength:** {'⭐' * int(signal_strength * 5)} ({signal_strength:.1%})
        """, unsafe_allow_html=True)
    
    with col2:
        current_price = data["current_price"]
        st.metric(
            label="Current BTC Price",
            value=f"${current_price:,.0f}",
            delta=f"{np.random.uniform(-0.5, 0.5):+.2%}"
        )
    
    st.markdown("**Filter Status:**")
    
    filters = data["filter_status"]
    filter_df = pd.DataFrame([
        {"Filter": "Volume Filter", "Status": "✅ PASS" if filters["volume"] else "❌ FAIL", "Value": "156,789 BTC", "Threshold": "80k"},
        {"Filter": "Key Levels", "Status": "✅ PASS" if filters["key_levels"] else "❌ FAIL", "Value": "S/R Confirmed", "Threshold": "Active"},
        {"Filter": "Pattern Recognition", "Status": "✅ PASS" if filters["pattern"] else "❌ FAIL", "Value": "Bull Engulfing", "Threshold": "Any"},
        {"Filter": "Order Flow", "Status": "✅ PASS" if filters["order_flow"] else "❌ FAIL", "Value": "+Smart Money", "Threshold": "Positive"},
        {"Filter": "Liquidity Sweep", "Status": "✅ PASS" if filters["liquidity_sweep"] else "❌ FAIL", "Value": "No Sweep", "Threshold": "Optional"},
    ])
    
    st.dataframe(filter_df, hide_index=True)

def create_performance_panel(data: Dict):
    """Create performance analytics panel"""
    st.subheader("📊 Performance Analytics")
    
    # Generate equity curve
    dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='4H')
    equity_values = []
    base_value = 10000
    
    for i, date in enumerate(dates):
        daily_return = np.random.normal(0.002, 0.025)
        base_value *= (1 + daily_return)
        equity_values.append(base_value)
    
    equity_df = pd.DataFrame({'Date': dates, 'Portfolio_Value': equity_values})
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=equity_df['Date'], 
        y=equity_df['Portfolio_Value'],
        mode='lines',
        name='Portfolio Value',
        line=dict(color='#28a745', width=2)
    ))
    
    fig.update_layout(
        title="Equity Curve (Last 30 Days)",
        xaxis_title="Date",
        yaxis_title="Portfolio Value ($)",
        height=400,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    current_drawdown = data["risk_metrics"]["current_drawdown"]
    
    with col1:
        st.metric("Max Drawdown", f"-{current_drawdown:.1f}%", "vs -18% Classic")
    
    with col2:
        sharpe_ratio = np.random.uniform(1.8, 2.5)
        st.metric("Sharpe Ratio", f"{sharpe_ratio:.2f}", "Excellent" if sharpe_ratio > 2.0 else "Good")
    
    with col3:
        profit_factor = np.random.uniform(1.4, 1.8)
        st.metric("Profit Factor", f"{profit_factor:.2f}", "✅" if profit_factor > 1.5 else "⚠️")
    
    with col4:
        avg_win = np.random.uniform(70, 120)
        avg_loss = np.random.uniform(30, 60)
        st.metric("Avg Win/Loss", f"${avg_win:.0f}/${avg_loss:.0f}", f"Ratio: {avg_win/avg_loss:.1f}")

def create_risk_panel(data: Dict):
    """Create risk management panel"""
    st.subheader("🛡️ Risk Management")
    
    risk_data = data["risk_metrics"]
    portfolio_value = data["portfolio_value"]
    current_exposure = risk_data["current_exposure"]
    exposure_pct = (current_exposure / portfolio_value) * 100
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("**Current Exposure:**")
        st.progress(min(exposure_pct / 50, 1.0), text=f"${current_exposure:,.0f} ({exposure_pct:.1f}% of ${portfolio_value:,.0f})")
        
        daily_risk_used = risk_data["daily_risk_used"]
        daily_limit = 1000
        st.markdown("**Daily Risk Used:**")
        st.progress(daily_risk_used / daily_limit, text=f"${daily_risk_used:.0f} ({daily_risk_used/daily_limit:.0%} of ${daily_limit} limit)")
        
        current_dd = risk_data["current_drawdown"]
        max_dd_limit = 20
        st.markdown("**Max Drawdown:**")
        st.progress(current_dd / max_dd_limit, text=f"-{current_dd:.1f}% ({current_dd/max_dd_limit:.0%} of {max_dd_limit}% limit)")
    
    with col2:
        if exposure_pct < 30 and daily_risk_used < 500 and current_dd < 10:
            st.success("✅ **HEALTHY**")
        elif exposure_pct < 40 and daily_risk_used < 700 and current_dd < 15:
            st.warning("⚠️ **MODERATE**")
        else:
            st.error("🚨 **HIGH RISK**")
        
        st.markdown("**Active Alerts:**")
        if current_dd < 10 and daily_risk_used < 500:
            st.success("✅ No warnings")
        else:
            st.warning("⚠️ Monitor closely")

def create_trade_log(data: Dict):
    """Create trade log"""
    st.subheader("📋 Recent Trades")
    
    trades_data = []
    base_time = datetime.now()
    
    for i in range(8):
        trade_time = base_time - timedelta(hours=i*2, minutes=np.random.randint(0, 119))
        signal_type = np.random.choice(["BUY", "SELL"])
        entry_price = 106500 + np.random.normal(0, 1000)
        
        if np.random.random() < 0.75:
            if signal_type == "BUY":
                exit_price = entry_price + np.random.uniform(200, 800)
            else:
                exit_price = entry_price - np.random.uniform(200, 800)
            pnl = abs(exit_price - entry_price) * 0.01
            status = "CLOSED"
        else:
            if signal_type == "BUY":
                exit_price = entry_price - np.random.uniform(150, 400)
            else:
                exit_price = entry_price + np.random.uniform(150, 400)
            pnl = -abs(exit_price - entry_price) * 0.01
            status = "STOPPED" if i > 0 else "OPEN"
        
        regime = np.random.choice(["BULL", "BEAR", "SIDEWAYS"], p=[0.6, 0.2, 0.2])
        
        trades_data.append({
            "Time": trade_time.strftime("%H:%M:%S"),
            "Signal": signal_type,
            "Entry": f"${entry_price:,.0f}",
            "Exit": f"${exit_price:,.0f}" if status != "OPEN" else "OPEN",
            "PnL": f"${pnl:+.2f}",
            "Status": status,
            "Regime": regime
        })
    
    trades_df = pd.DataFrame(trades_data)
    st.dataframe(trades_df, hide_index=True)

def create_sidebar(data: Dict):
    """Create sidebar"""
    st.sidebar.markdown("### 🎛️ Dashboard Controls")
    
    auto_refresh = st.sidebar.checkbox("Auto-Refresh (5s)", value=True)
    
    if auto_refresh:
        st.sidebar.success("🔄 Auto-refresh: ON")
        time.sleep(5)
        st.rerun()
    else:
        if st.sidebar.button("🔄 Manual Refresh"):
            st.rerun()
    
    st.sidebar.markdown("### 📡 Connection Status")
    st.sidebar.warning("🧪 Demo Mode Active")
    st.sidebar.info("📊 Simulated Data")
    
    st.sidebar.markdown("### 📈 Quick Stats")
    st.sidebar.metric("Last Update", data["last_update"].strftime("%H:%M:%S"))
    st.sidebar.metric("Bot Runtime", f"{np.random.randint(4, 48)}h {np.random.randint(0, 59)}m")
    
    st.sidebar.markdown("### 🚨 Emergency Controls")
    if st.sidebar.button("⏸️ Pause Trading"):
        st.sidebar.warning("Trading Paused!")
    if st.sidebar.button("🛑 Emergency STOP"):
        st.sidebar.error("🚨 EMERGENCY STOP!")

def main():
    """Main dashboard function"""
    try:
        # Get current data
        data = get_demo_data()
        
        # Create sidebar
        create_sidebar(data)
        
        # Main content
        create_main_overview(data)
        
        # Create dashboard panels
        col1, col2 = st.columns(2)
        
        with col1:
            create_market_regime_panel(data)
            create_risk_panel(data)
        
        with col2:
            create_live_signals_panel(data)
            create_performance_panel(data)
        
        # Full width panels
        create_trade_log(data)
        
        # Footer
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; color: #666;'>
            🚀 Enhanced Smart Money Trading Bot V2 | 
            Real-time Monitoring Dashboard | 
            © 2025 Romain Hill
        </div>
        """, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"Dashboard Error: {e}")
        st.title("🚀 Crypto Bot Monitoring (Fallback)")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Portfolio", "$10,247", "+$247")
        with col2:
            st.metric("Trades", "15", "+3 today")
        with col3:
            st.metric("Win Rate", "78%", "↗️")

if __name__ == "__main__":
    main()
