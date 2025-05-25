#!/usr/bin/env python3
"""
🚀 ADVANCED LIVE TRADING DASHBOARD - FINAL INTEGRATED VERSION
Professional Real-time Dashboard für Enhanced Smart Money Bot
Version: 2.1 - PRODUCTION READY for 50€ Mainnet Deployment

All parts integrated into single file
"""

# Import all parts
from advanced_dashboard_part1 import *
from advanced_dashboard_part2 import *
from advanced_dashboard_part3 import *
from advanced_dashboard_part4 import *

# Additional imports for components
try:
    from components.live_widgets import LivePriceWidget, OrderBookWidget, MarketStatsWidget, TradingSignalWidget
    from components.portfolio_monitor import AdvancedPortfolioMonitor, TradeHistoryWidget, RiskAnalyticsWidget
    from components.professional_charts import ProfessionalChart, MarketRegimeChart
    from components.trading_controls import AdvancedTradingControls
    COMPONENTS_AVAILABLE = True
except ImportError:
    COMPONENTS_AVAILABLE = False
    print("⚠️ Component modules not found, using built-in functions")

def render_startup_info():
    """Display startup information and environment status"""
    st.markdown("""
    <div style="background: linear-gradient(45deg, #667eea, #764ba2); 
                color: white; padding: 20px; border-radius: 15px; margin-bottom: 20px;">
        <h1 style="margin: 0; text-align: center;">🚀 DASHBOARD STARTUP</h1>
        <p style="text-align: center; margin: 10px 0;">
            Loading Enhanced Smart Money Trading Dashboard...
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Environment check
    api = st.session_state.api_client
    environment_color = "#10b981" if api.environment == "MAINNET" else "#f59e0b"
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("🌐 Environment", api.environment)
        st.markdown(f"<div style='color: {environment_color}; font-weight: bold;'>{'🟢 LIVE TRADING' if api.environment == 'MAINNET' else '🟡 TESTNET MODE'}</div>", unsafe_allow_html=True)
    
    with col2:
        portfolio_value = st.session_state.get('portfolio_value', 50.0)
        st.metric("💰 Portfolio", f"${portfolio_value:.2f}")
        st.markdown("<div style='color: #3b82f6; font-weight: bold;'>50€ Deployment Ready</div>", unsafe_allow_html=True)
    
    with col3:
        components_status = "✅ LOADED" if COMPONENTS_AVAILABLE else "⚠️ BUILT-IN"
        st.metric("🔧 Components", components_status)
        st.markdown("<div style='color: #10b981; font-weight: bold;'>Professional Grade</div>", unsafe_allow_html=True)


def enhanced_main():
    """Enhanced main function with error handling and initialization"""
    
    # Initial setup check
    if 'dashboard_initialized' not in st.session_state:
        render_startup_info()
        
        # Initialize data on first load
        with st.spinner("🔄 Initializing dashboard components..."):
            refresh_status = refresh_all_data()
            
            if refresh_status['success'] > 0:
                st.success(f"✅ Dashboard initialized with {refresh_status['success']} data sources")
                st.session_state.dashboard_initialized = True
                time.sleep(2)
                st.rerun()
            else:
                st.error("❌ Failed to initialize dashboard")
                for error in refresh_status['errors']:
                    st.error(error)
                
                if st.button("🔄 Retry Initialization"):
                    st.rerun()
                return
    
    # Main dashboard rendering
    try:
        main()
        
    except Exception as e:
        st.error(f"❌ Dashboard Error: {str(e)}")
        st.info("🔄 Refreshing dashboard...")
        
        if st.button("🔄 Reload Dashboard"):
            # Reset initialization flag
            if 'dashboard_initialized' in st.session_state:
                del st.session_state.dashboard_initialized
            st.rerun()


def render_welcome_message():
    """Render welcome message for first-time users"""
    if 'welcome_shown' not in st.session_state:
        st.balloons()
        
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    color: white; padding: 30px; border-radius: 20px; text-align: center; margin: 20px 0;">
            <h1 style="margin: 0; font-size: 2.5em;">🎉 WELCOME TO THE FUTURE OF TRADING!</h1>
            <h2 style="margin: 15px 0;">Advanced Live Trading Dashboard</h2>
            <p style="font-size: 1.2em; margin: 15px 0;">
                ✨ Professional Grade • 🧠 AI-Enhanced • 🚀 Production Ready
            </p>
            <div style="background: rgba(255,255,255,0.1); padding: 20px; border-radius: 10px; margin-top: 20px;">
                <h3>🎯 Ready for 50€ Mainnet Deployment</h3>
                <p>Your Enhanced Smart Money Strategy is loaded and ready to trade!</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.session_state.welcome_shown = True


# Application entry point
if __name__ == "__main__":
    
    # Show welcome message
    render_welcome_message()
    
    # Run enhanced main function
    enhanced_main()
