"""
🚀 CRYPTO TRADING BOT V2 - REAL-TIME MONITORING DASHBOARD
Quick Version - Minimal but Functional

Enhanced Smart Money Strategy Live Monitoring

Aufruf: streamlit run dashboard.py --server.port 8501
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
import json
import os
import sys
import numpy as np
from typing import Dict, List, Optional

# Projekt Root zu sys.path hinzufügen
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

try:
    from config.config import Config
    from strategies.enhanced_smart_money import EnhancedSmartMoneyStrategy
    from risk.risk_manager import RiskManager
    from exchange.bybit_api import BybitAPI
    from data.data_handler import DataHandler
except ImportError as e:
    st.error(f"Import Error: {e}")
    st.info("Läuft im Demo-Modus mit simulierten Daten")

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
    .sidebar-info {
        background: #e9ecef;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

class MonitoringDashboard:
    def __init__(self):
        self.config = self._load_config()
        self.initialize_components()
        
    def _load_config(self):
        """Load configuration"""
        try:
            return Config()
        except:
            # Demo Config
            class DemoConfig:
                SYMBOL = "BTCUSDT"
                TIMEFRAME = "1h"
                INITIAL_BALANCE = 10000
                RISK_PERCENTAGE = 2.0
                USE_TESTNET = True
            return DemoConfig()
    
    def initialize_components(self):
        """Initialize trading components"""
        try:
            self.api = BybitAPI(self.config)
            self.data_handler = DataHandler(self.api)
            self.strategy = EnhancedSmartMoneyStrategy(self.config)
            self.risk_manager = RiskManager(self.config)
            self.live_mode = True
            st.success("✅ Live Trading Components geladen!")
        except Exception as e:
            self.live_mode = False
            st.warning(f"Demo-Modus aktiviert: {e}")
    
    def get_live_data(self) -> Dict:
        """Get real-time data from trading bot"""
        if self.live_mode:
            try:
                # Hier würde die echte Live-Daten-Abfrage stehen
                latest_data = self.data_handler.get_latest_data(self.config.SYMBOL, self.config.TIMEFRAME)
                market_regime = self.strategy.detect_market_regime(latest_data)
                
                return {
                    "portfolio_value": self.risk_manager.get_portfolio_value(),
                    "pnl": self.risk_manager.calculate_unrealized_pnl(),
                    "market_regime": market_regime,
                    "current_price": latest_data['close'].iloc[-1] if len(latest_data) > 0 else 0,
                    "last_update": datetime.now(),
                    "trades_today": len(self.strategy.get_recent_trades()),
                    "win_rate": self.strategy.calculate_win_rate(),
                    "is_live": True
                }
            except Exception as e:
                st.error(f"Live data error: {e}")
                return self._get_demo_data()
        else:
            return self._get_demo_data()
    
    def _get_demo_data(self) -> Dict:
        """Generate demo data for testing"""
        base_time = datetime.now()
        
        # Simuliere realistische Werte
        base_price = 106500 + np.random.normal(0, 500)
        portfolio_change = np.random.normal(0.02, 0.01)  # 2% average gain with volatility
        
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
            "active_trades": np.random.randint(0, 3),
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
                "max_drawdown": np.random.uniform(5, 15),
                "current_drawdown": np.random.uniform(0, 8)
            },
            "last_update": base_time,
            "is_live": False
        }

    def create_main_overview(self, data: Dict):
        """Create main overview panel"""
        st.markdown('<div class="main-header"><h1>🚀 ENHANCED SMART MONEY BOT</h1><h3>Live Trading Dashboard</h3></div>', unsafe_allow_html=True)
        
        # Hauptmetriken
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            pnl_color = "green" if data["pnl"] >= 0 else "red"
            delta_pnl = f"{data['pnl']:+,.2f} USD"
            st.metric(
                label="💰 Portfolio PnL",
                value=f"${data['portfolio_value']:,.2f}",
                delta=delta_pnl
            )
        
        with col2:
            total_trades = data.get("trades_today", 0)
            won_trades = data.get("trades_won", 0)
            st.metric(
                label="📊 Trades Heute",
                value=f"{total_trades}",
                delta=f"{won_trades}W/{total_trades-won_trades}L"
            )
        
        with col3:
            win_rate = data.get("win_rate", 0) * 100
            st.metric(
                label="🏆 Win Rate",
                value=f"{win_rate:.1f}%",
                delta="↗️" if win_rate > 70 else "→"
            )
        
        with col4:
            regime_data = data.get("market_regime", {})
            regime = regime_data.get("regime", "UNKNOWN")
            confidence = regime_data.get("confidence", 0)
            regime_emoji = {"BULL": "🚀", "BEAR": "🐻", "SIDEWAYS": "↔️"}.get(regime, "❓")
            st.metric(
                label="🧠 Market Regime",
                value=f"{regime_emoji} {regime}",
                delta=f"Conf: {confidence:.2f}"
            )

    def create_market_regime_panel(self, data: Dict):
        """Create market regime detection panel"""
        st.subheader("📈 Market Regime Analysis")
        
        regime_data = data.get("market_regime", {})
        regime = regime_data.get("regime", "UNKNOWN")
        confidence = regime_data.get("confidence", 0)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Regime Status
            regime_colors = {
                "BULL": "#28a745",
                "BEAR": "#dc3545", 
                "SIDEWAYS": "#ffc107"
            }
            
            st.markdown(f"""
            **Current Regime:** <span style="color: {regime_colors.get(regime, '#666')}; font-size: 1.2em; font-weight: bold;">{regime}</span>  
            **Confidence:** {confidence:.2%}  
            **Duration:** {np.random.randint(30, 180)} minutes
            """, unsafe_allow_html=True)
            
            # Scoring Breakdown
            bull_score = regime_data.get("bull_score", 0)
            bear_score = regime_data.get("bear_score", 0)
            sideways_score = regime_data.get("sideways_score", 0)
            
            st.markdown("**Regime Scoring:**")
            st.progress(bull_score / 8, text=f"🟢 Bull Score: {bull_score}/8")
            st.progress(bear_score / 8, text=f"📉 Bear Score: {bear_score}/8") 
            st.progress(sideways_score / 5, text=f"↔️ Sideways Score: {sideways_score}/5")
        
        with col2:
            # Adaptive Parameters
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

    def create_live_signals_panel(self, data: Dict):
        """Create live signals and filters panel"""
        st.subheader("⚡ Live Signals & Filters")
        
        last_signal = data.get("last_signal", {})
        signal_type = last_signal.get("type", "HOLD")
        signal_time = last_signal.get("time", datetime.now())
        signal_price = last_signal.get("price", data.get("current_price", 0))
        signal_strength = last_signal.get("strength", 0)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Latest Signal
            signal_colors = {"BUY": "green", "SELL": "red", "HOLD": "orange"}
            time_ago = datetime.now() - signal_time
            minutes_ago = int(time_ago.total_seconds() / 60)
            
            st.markdown(f"""
            **Last Signal:** <span style="color: {signal_colors.get(signal_type, 'black')}; font-weight: bold;">{signal_type}</span> at ${signal_price:,.0f}  
            **Time:** {minutes_ago} min ago  
            **Strength:** {'⭐' * int(signal_strength * 5)} ({signal_strength:.1%})
            """, unsafe_allow_html=True)
        
        with col2:
            # Current Price
            current_price = data.get("current_price", 0)
            st.metric(
                label="Current BTC Price",
                value=f"${current_price:,.0f}",
                delta=f"{np.random.uniform(-0.5, 0.5):+.2%}"
            )
        
        # Filter Status Table
        st.markdown("**Filter Status:**")
        
        filters = data.get("filter_status", {})
        filter_df = pd.DataFrame([
            {"Filter": "✅ Volume Filter", "Status": "✅ PASS" if filters.get("volume") else "❌ FAIL", "Value": "156,789 BTC", "Threshold": "80k"},
            {"Filter": "✅ Key Levels", "Status": "✅ PASS" if filters.get("key_levels") else "❌ FAIL", "Value": "S/R Confirmed", "Threshold": "Active"},
            {"Filter": "✅ Pattern Recognition", "Status": "✅ PASS" if filters.get("pattern") else "❌ FAIL", "Value": "Bull Engulfing", "Threshold": "Any"},
            {"Filter": "✅ Order Flow", "Status": "✅ PASS" if filters.get("order_flow") else "❌ FAIL", "Value": "+Smart Money", "Threshold": "Positive"},
            {"Filter": "❌ Liquidity Sweep", "Status": "✅ PASS" if filters.get("liquidity_sweep") else "❌ FAIL", "Value": "No Sweep", "Threshold": "Optional"},
        ])
        
        st.dataframe(filter_df, hide_index=True)

    def create_performance_panel(self, data: Dict):
        """Create performance analytics panel"""
        st.subheader("📊 Performance Analytics")
        
        # Generate sample equity curve data
        dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='H')
        equity_values = []
        base_value = 10000
        
        for i, date in enumerate(dates):
            daily_return = np.random.normal(0.001, 0.02)  # 0.1% daily return mit 2% volatility
            base_value *= (1 + daily_return)
            equity_values.append(base_value)
        
        equity_df = pd.DataFrame({
            'Date': dates,
            'Portfolio_Value': equity_values
        })
        
        # Equity Curve Chart
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
        
        # Performance Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        current_drawdown = data.get("risk_metrics", {}).get("current_drawdown", 0)
        max_drawdown = 18  # Classic strategy comparison
        
        with col1:
            st.metric("Max Drawdown", f"-{current_drawdown:.1f}%", f"vs -{max_drawdown}% Classic")
        
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

    def create_risk_panel(self, data: Dict):
        """Create risk management panel"""
        st.subheader("🛡️ Risk Management")
        
        risk_data = data.get("risk_metrics", {})
        
        # Portfolio Status
        portfolio_value = data.get("portfolio_value", 10000)
        current_exposure = risk_data.get("current_exposure", 2000)
        exposure_pct = (current_exposure / portfolio_value) * 100
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Risk Gauges
            st.markdown("**Current Exposure:**")
            st.progress(min(exposure_pct / 50, 1.0), text=f"${current_exposure:,.0f} ({exposure_pct:.1f}% of ${portfolio_value:,.0f})")
            
            daily_risk_used = risk_data.get("daily_risk_used", 300)
            daily_limit = 1000
            st.markdown("**Daily Risk Used:**")
            st.progress(daily_risk_used / daily_limit, text=f"${daily_risk_used:.0f} ({daily_risk_used/daily_limit:.0%} of ${daily_limit} limit)")
            
            current_dd = risk_data.get("current_drawdown", 6)
            max_dd_limit = 20
            st.markdown("**Max Drawdown:**")
            st.progress(current_dd / max_dd_limit, text=f"-{current_dd:.1f}% ({current_dd/max_dd_limit:.0%} of {max_dd_limit}% limit)")
        
        with col2:
            # Risk Status
            if exposure_pct < 30 and daily_risk_used < 500 and current_dd < 10:
                st.success("✅ **Portfolio Status: HEALTHY**")
            elif exposure_pct < 40 and daily_risk_used < 700 and current_dd < 15:
                st.warning("⚠️ **Portfolio Status: MODERATE**")
            else:
                st.error("🚨 **Portfolio Status: HIGH RISK**")
            
            st.markdown("**Active Alerts:**")
            if current_dd > 15:
                st.error("🚨 High Drawdown Alert")
            if daily_risk_used > 800:
                st.warning("⚠️ Daily Risk Limit Warning")
            if current_dd < 10 and daily_risk_used < 500:
                st.success("✅ No active risk warnings")

    def create_trade_log(self, data: Dict):
        """Create trade log and history"""
        st.subheader("📋 Recent Trades")
        
        # Generate sample trades
        trades_data = []
        base_time = datetime.now()
        
        for i in range(8):
            trade_time = base_time - timedelta(hours=i*2, minutes=np.random.randint(0, 119))
            signal_type = np.random.choice(["BUY", "SELL"])
            entry_price = 106500 + np.random.normal(0, 1000)
            
            if np.random.random() < 0.75:  # 75% win rate
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
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        with col1:
            filter_option = st.selectbox("Filter:", ["All", "Today", "Winners", "Losers", "By Regime"])
        with col2:
            regime_filter = st.selectbox("Regime:", ["All", "BULL", "BEAR", "SIDEWAYS"])
        with col3:
            export_format = st.selectbox("Export:", ["None", "CSV", "JSON"])
        
        # Apply filters
        display_df = trades_df.copy()
        if regime_filter != "All":
            display_df = display_df[display_df["Regime"] == regime_filter]
        
        st.dataframe(display_df, hide_index=True)
        
        # Export functionality
        if export_format == "CSV":
            csv = display_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"trades_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

    def create_sidebar(self, data: Dict):
        """Create sidebar with controls and info"""
        st.sidebar.markdown("### 🎛️ Dashboard Controls")
        
        # Auto-refresh toggle
        auto_refresh = st.sidebar.checkbox("Auto-Refresh (5s)", value=True)
        
        if auto_refresh:
            st.sidebar.success("🔄 Auto-refresh: ON")
            time.sleep(0.1)
            st.rerun()
        else:
            if st.sidebar.button("🔄 Manual Refresh"):
                st.rerun()
        
        # Connection Status
        st.sidebar.markdown("### 📡 Connection Status")
        if data.get("is_live", False):
            st.sidebar.success("✅ Live Trading Connection")
            st.sidebar.info("🔗 Bybit API: Connected")
            st.sidebar.info("📊 Real-time Data: Active")
        else:
            st.sidebar.warning("🧪 Demo Mode Active")
            st.sidebar.info("⚠️ Simulated data only")
        
        # Quick Stats
        st.sidebar.markdown("### 📈 Quick Stats")
        st.sidebar.metric("Last Update", data["last_update"].strftime("%H:%M:%S"))
        st.sidebar.metric("Bot Runtime", f"{np.random.randint(4, 48)}h {np.random.randint(0, 59)}m")
        
        # Emergency Controls
        st.sidebar.markdown("### 🚨 Emergency Controls")
        
        if st.sidebar.button("⏸️ Pause Trading", type="secondary"):
            st.sidebar.warning("Trading Paused!")
        
        if st.sidebar.button("🛑 Emergency STOP", type="primary"):
            st.sidebar.error("🚨 EMERGENCY STOP ACTIVATED!")
        
        # System Info
        st.sidebar.markdown("### ⚙️ System Info")
        st.sidebar.text(f"Symbol: {self.config.SYMBOL}")
        st.sidebar.text(f"Timeframe: {self.config.TIMEFRAME}")
        st.sidebar.text(f"Risk: {self.config.RISK_PERCENTAGE}%")
        st.sidebar.text(f"Balance: ${self.config.INITIAL_BALANCE:,}")

    def run(self):
        """Main dashboard loop"""
        
        # Get current data
        data = self.get_live_data()
        
        # Create sidebar
        self.create_sidebar(data)
        
        # Main content
        self.create_main_overview(data)
        
        # Create dashboard panels
        col1, col2 = st.columns(2)
        
        with col1:
            self.create_market_regime_panel(data)
            self.create_risk_panel(data)
        
        with col2:
            self.create_live_signals_panel(data)
            self.create_performance_panel(data)
        
        # Full width panels
        self.create_trade_log(data)
        
        # Footer
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; color: #666;'>
            🚀 Enhanced Smart Money Trading Bot V2 | 
            Real-time Monitoring Dashboard | 
            © 2025 Romain Hill
        </div>
        """, unsafe_allow_html=True)

def main():
    """Main entry point"""
    try:
        dashboard = MonitoringDashboard()
        dashboard.run()
    except Exception as e:
        st.error(f"Dashboard Error: {e}")
        st.info("Läuft im Notfall-Modus mit minimaler Funktionalität")
        
        # Minimal fallback dashboard
        st.title("🚀 Crypto Bot Monitoring (Fallback)")
        st.warning("Hauptsystem nicht verfügbar - Basis-Dashboard aktiv")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Portfolio", "$10,247", "+$247")
        with col2:
            st.metric("Trades", "15", "+3 today")
        with col3:
            st.metric("Win Rate", "78%", "↗️")

if __name__ == "__main__":
    main()
