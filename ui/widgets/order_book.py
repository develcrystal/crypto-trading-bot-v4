#!/usr/bin/env python3
"""
🚀 Order Book Component
Live Order Book Visualization with Bids/Asks
"""

import streamlit as st
import pandas as pd


def render_order_book(book_data):
    """Render live order book visualization"""
    st.markdown("### 📊 LIVE ORDER BOOK")
    
    if book_data.get('success'):
        asks = book_data.get('asks', [])
        bids = book_data.get('bids', [])
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🔴 ASKS (Sell Orders)")
            if asks:
                ask_df = pd.DataFrame(asks[:10], columns=['Price', 'Size'])
                ask_df['Total'] = (ask_df['Price'] * ask_df['Size']).round(2)
                ask_df = ask_df.sort_values('Price', ascending=False)
                
                st.markdown('<div class="order-book">', unsafe_allow_html=True)
                for _, row in ask_df.iterrows():
                    st.markdown(f"""
                    <div style="display: flex; justify-content: space-between; padding: 2px 0;">
                        <span class="sell-price">${row['Price']:,.2f}</span>
                        <span>{row['Size']:.4f}</span>
                        <span>${row['Total']:,.2f}</span>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown("#### 🟢 BIDS (Buy Orders)")
            if bids:
                bid_df = pd.DataFrame(bids[:10], columns=['Price', 'Size'])
                bid_df['Total'] = (bid_df['Price'] * bid_df['Size']).round(2)
                bid_df = bid_df.sort_values('Price', ascending=False)
                
                st.markdown('<div class="order-book">', unsafe_allow_html=True)
                for _, row in bid_df.iterrows():
                    st.markdown(f"""
                    <div style="display: flex; justify-content: space-between; padding: 2px 0;">
                        <span class="buy-price">${row['Price']:,.2f}</span>
                        <span>{row['Size']:.4f}</span>
                        <span>${row['Total']:,.2f}</span>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.error("❌ Unable to fetch order book data")


def get_order_book_styles():
    """Return CSS styles for order book"""
    return """
    .order-book {
        font-family: 'Monaco', 'Menlo', monospace;
        font-size: 12px;
    }
    
    .buy-price { 
        color: #10b981; 
        font-weight: bold; 
    }
    
    .sell-price { 
        color: #ef4444; 
        font-weight: bold; 
    }
    """
