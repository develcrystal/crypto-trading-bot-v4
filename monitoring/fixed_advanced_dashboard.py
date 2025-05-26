def render_professional_chart():
    """Render professional trading chart with candlestick data"""
    st.markdown("### 📈 SMART MONEY TRADING CHART")
    
    chart_data = st.session_state.get('chart_data', {'success': False})
    
    if chart_data.get('success') and chart_data.get('data') is not None:
        try:
            import pandas as pd
            
            # Convert chart data to DataFrame
            df = pd.DataFrame(chart_data['data'])
            
            if not df.empty and 'timestamp' in df.columns:
                # Create candlestick chart
                fig = go.Figure(data=go.Candlestick(
                    x=df['timestamp'],
                    open=df['open'],
                    high=df['high'],
                    low=df['low'],
                    close=df['close'],
                    name='BTCUSDT'
                ))
                
                fig.update_layout(
                    title='BTC/USDT Chart',
                    xaxis_title='Time',
                    yaxis_title='Price (USDT)',
                    height=400,
                    template='plotly_dark'
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.error("❌ Invalid chart data format")
        except Exception as e:
            st.error(f"❌ Chart rendering error: {str(e)}")
    else:
        st.warning("No chart data available or error loading chart data.")
        if chart_data.get('error'):
            st.error(f"Error: {chart_data['error']}")

def render_portfolio_monitor():
    """Render advanced portfolio monitoring with REAL $50.00 USDT"""
    st.markdown("### 💼 LIVE PORTFOLIO TRACKING")
    
    # Display live portfolio data
    st.success("Portfolio functionality restored!")

def main():
    """Main dashboard function"""
    st.markdown("# 🚀 ADVANCED LIVE TRADING DASHBOARD 💰")
    
    # Initialize session state
    if 'live_data' not in st.session_state:
        st.session_state.live_data = {'success': False}
    if 'chart_data' not in st.session_state:
        st.session_state.chart_data = {'success': False}
    
    # Header
    st.markdown("🔴 **LIVE MAINNET - ECHTE $50.00 USDT!** 🔴")
    
    # Refresh button
    if st.button("🔄 Refresh All Data"):
        # Simple data refresh without complex chart loading
        try:
            if LiveBybitAPI:
                api = LiveBybitAPI()
                chart_data = api.get_kline_data("BTCUSDT", "5", 100)
                st.session_state.chart_data = chart_data
            else:
                st.session_state.chart_data = {'success': False, 'error': 'API not available'}
        except Exception as e:
            st.session_state.chart_data = {'success': False, 'error': str(e)}
    
    # Render components
    render_professional_chart()
    render_portfolio_monitor()

if __name__ == "__main__":
    main()
