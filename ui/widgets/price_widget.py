#!/usr/bin/env python3
"""
🚀 Price Widget Component
Live BTC/USDT Price Display with Bid/Ask Spread
"""

import streamlit as st
import pandas as pd


def render_live_price_widget(live_data):
    """Render live price widget with bid/ask"""
    st.markdown("### 💰 LIVE BTC/USDT PRICE")
    
    if live_data.get('success'):
        price = live_data['price']
        change = live_data['change_24h']
        bid = live_data.get('bid', 0)
        ask = live_data.get('ask', 0)
        spread = ask - bid if ask > 0 and bid > 0 else 0
        
        # Main price display
        color = "#10b981" if change >= 0 else "#ef4444"
        st.markdown(f"""
        <div class="price-widget">
            <h1 style="margin: 0; font-size: 3em;">${price:,.2f}</h1>
            <h3 style="margin: 5px 0; color: {color};">{change:+.2f}% (24h)</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Bid/Ask/Spread
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("💚 Bid", f"${bid:,.2f}", "Best Buy")
        
        with col2:
            st.metric("❤️ Ask", f"${ask:,.2f}", "Best Sell")
        
        with col3:
            st.metric("📊 Spread", f"${spread:.2f}", f"{(spread/price*100):.3f}%")
        
        with col4:
            volume = live_data.get('volume_24h', 0)
            st.metric("📈 Volume 24h", f"{volume:,.0f} BTC", "Trading Activity")
    
    else:
        st.error("❌ Unable to fetch live price data")
        st.error(f"Error: {live_data.get('error', 'Unknown error')}")


def get_price_widget_styles():
    """Return CSS styles for price widget"""
    return """
    .price-widget {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    """
