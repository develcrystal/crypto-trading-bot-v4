"""
Live Widgets Module for Advanced Dashboard
Professional trading widgets with real-time data
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import pandas as pd
import numpy as np

class LivePriceWidget:
    """Professional live price widget with bid/ask spread"""
    
    def __init__(self, api_client):
        self.api = api_client
    
    def render(self, symbol='BTCUSDT'):
        """Render live price widget"""
        ticker_data = self.api.get_live_ticker(symbol)
        
        if ticker_data.get('success'):
            price = ticker_data['price']
            change = ticker_data['change_24h']
            bid = ticker_data.get('bid', 0)
            ask = ticker_data.get('ask', 0)
            volume = ticker_data.get('volume_24h', 0)
            
            # Price display with color coding
            color = "#10b981" if change >= 0 else "#ef4444"
            
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        color: white; padding: 25px; border-radius: 15px; text-align: center;
                        box-shadow: 0 10px 30px rgba(0,0,0,0.3);">
                <h1 style="margin: 0; font-size: 3.5em; font-weight: bold;">${price:,.2f}</h1>
                <h2 style="margin: 10px 0; color: {color}; font-size: 1.5em;">
                    {change:+.2f}% (24h)
                </h2>
                <p style="margin: 5px 0; opacity: 0.9;">
                    Last updated: {ticker_data['timestamp'].strftime('%H:%M:%S')}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Bid/Ask/Spread metrics
            spread = ask - bid if ask > 0 and bid > 0 else 0
            spread_pct = (spread / price * 100) if price > 0 else 0
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("💚 Best Bid", f"${bid:,.2f}", "Buy Price")
            
            with col2:
                st.metric("❤️ Best Ask", f"${ask:,.2f}", "Sell Price")
            
            with col3:
                st.metric("📊 Spread", f"${spread:.2f}", f"{spread_pct:.3f}%")
            
            with col4:
                st.metric("📈 Volume 24h", f"{volume:,.0f} BTC", "Trading Activity")
                
            return ticker_data
        
        else:
            st.error(f"❌ Failed to load price data: {ticker_data.get('error')}")
            return None

class OrderBookWidget:
    """Advanced order book visualization"""
    
    def __init__(self, api_client):
        self.api = api_client
    
    def render(self, symbol='BTCUSDT', depth=10):
        """Render live order book"""
        book_data = self.api.get_order_book(symbol, depth)
        
        if book_data.get('success'):
            asks = book_data.get('asks', [])
            bids = book_data.get('bids', [])
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🔴 ASKS (Sell Orders)")
                self._render_order_side(asks, "sell", reverse=True)
            
            with col2:
                st.markdown("#### 🟢 BIDS (Buy Orders)")
                self._render_order_side(bids, "buy", reverse=False)
            
            # Market depth chart
            self._render_depth_chart(bids, asks)
            
            return book_data
        
        else:
            st.error(f"❌ Failed to load order book: {book_data.get('error')}")
            return None
    
    def _render_order_side(self, orders, side, reverse=False):
        """Render one side of the order book"""
        if not orders:
            st.warning("No orders available")
            return
        
        # Convert to DataFrame
        df = pd.DataFrame(orders[:10], columns=['Price', 'Size'])
        df['Total'] = (df['Price'] * df['Size']).round(0)
        
        if reverse:
            df = df.sort_values('Price', ascending=False)
        else:
            df = df.sort_values('Price', ascending=False)
        
        # Color coding
        price_color = "#ef4444" if side == "sell" else "#10b981"
        
        st.markdown(f"""
        <div style="font-family: 'Monaco', 'Menlo', monospace; font-size: 13px;
                    background: #f8fafc; padding: 15px; border-radius: 8px;">
        """, unsafe_allow_html=True)
        
        # Header
        st.markdown(f"""
        <div style="display: flex; justify-content: space-between; font-weight: bold; 
                    border-bottom: 1px solid #e2e8f0; padding-bottom: 5px; margin-bottom: 8px;">
            <span>Price (USDT)</span>
            <span>Size (BTC)</span>
            <span>Total (USDT)</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Orders
        for _, row in df.iterrows():
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; padding: 3px 0;
                        border-bottom: 1px solid #f1f5f9;">
                <span style="color: {price_color}; font-weight: bold;">${row['Price']:,.2f}</span>
                <span>{row['Size']:.4f}</span>
                <span>${row['Total']:,.0f}</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    def _render_depth_chart(self, bids, asks):
        """Render market depth visualization"""
        if not bids or not asks:
            return
        
        # Prepare data for depth chart
        bid_df = pd.DataFrame(bids, columns=['price', 'size'])
        ask_df = pd.DataFrame(asks, columns=['price', 'size'])
        
        bid_df['cumulative'] = bid_df['size'].cumsum()
        ask_df['cumulative'] = ask_df['size'].cumsum()
        
        # Create depth chart
        fig = go.Figure()
        
        # Bids (green)
        fig.add_trace(go.Scatter(
            x=bid_df['price'],
            y=bid_df['cumulative'],
            mode='lines',
            fill='tonexty',
            name='Bids',
            line=dict(color='#10b981', width=2),
            fillcolor='rgba(16, 185, 129, 0.3)'
        ))
        
        # Asks (red)
        fig.add_trace(go.Scatter(
            x=ask_df['price'],
            y=ask_df['cumulative'],
            mode='lines',
            fill='tonexty',
            name='Asks',
            line=dict(color='#ef4444', width=2),
            fillcolor='rgba(239, 68, 68, 0.3)'
        ))
        
        fig.update_layout(
            title="Market Depth",
            xaxis_title="Price (USDT)",
            yaxis_title="Cumulative Size (BTC)",
            height=300,
            showlegend=True,
            template="plotly_white"
        )
        
        st.plotly_chart(fig, use_container_width=True)

class MarketStatsWidget:
    """24h market statistics widget"""
    
    def __init__(self, api_client):
        self.api = api_client
    
    def render(self, symbol='BTCUSDT'):
        """Render 24h market statistics"""
        ticker_data = self.api.get_live_ticker(symbol)
        
        if ticker_data.get('success'):
            high_24h = ticker_data.get('high_24h', 0)
            low_24h = ticker_data.get('low_24h', 0)
            volume_24h = ticker_data.get('volume_24h', 0)
            price = ticker_data['price']
            
            # Calculate additional metrics
            volatility = ((high_24h - low_24h) / low_24h * 100) if low_24h > 0 else 0
            mid_point = (high_24h + low_24h) / 2 if high_24h > 0 and low_24h > 0 else 0
            price_position = ((price - low_24h) / (high_24h - low_24h) * 100) if high_24h > low_24h else 50
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("📈 24h High", f"${high_24h:,.0f}", f"Peak price")
            
            with col2:
                st.metric("📉 24h Low", f"${low_24h:,.0f}", f"Bottom price")
            
            with col3:
                st.metric("🎯 Price Position", f"{price_position:.1f}%", f"In 24h range")
            
            with col4:
                st.metric("📊 24h Volatility", f"{volatility:.2f}%", f"Price swing")
            
            # Price range visualization
            self._render_range_chart(price, low_24h, high_24h, mid_point)
            
            return ticker_data
        
        else:
            st.error(f"❌ Failed to load market stats: {ticker_data.get('error')}")
            return None
    
    def _render_range_chart(self, current_price, low_24h, high_24h, mid_point):
        """Render 24h price range chart"""
        fig = go.Figure()
        
        # Add range bar
        fig.add_trace(go.Bar(
            x=['24h Range'],
            y=[high_24h - low_24h],
            base=[low_24h],
            name='24h Range',
            marker_color='rgba(99, 102, 241, 0.3)',
            width=0.6
        ))
        
        # Add current price line
        fig.add_hline(
            y=current_price,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Current: ${current_price:,.0f}",
            annotation_position="right"
        )
        
        # Add mid point
        fig.add_hline(
            y=mid_point,
            line_dash="dot",
            line_color="gray",
            annotation_text=f"Mid: ${mid_point:,.0f}",
            annotation_position="left"
        )
        
        fig.update_layout(
            title="24h Price Range",
            yaxis_title="Price (USDT)",
            height=200,
            showlegend=False,
            template="plotly_white"
        )
        
        st.plotly_chart(fig, use_container_width=True)

class TradingSignalWidget:
    """Live trading signals display"""
    
    def __init__(self):
        pass
    
    def render(self, signal_data=None):
        """Render current trading signals"""
        # For now, simulate signals (in production, this would receive real signal data)
        if signal_data is None:
            signal_data = self._generate_mock_signal()
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            self._render_signal_status(signal_data)
        
        with col2:
            self._render_filter_breakdown(signal_data)
    
    def _render_signal_status(self, signal_data):
        """Render current signal status"""
        st.markdown("#### 🎯 Current Signal")
        
        signal_type = signal_data.get('signal', 'NONE')
        confidence = signal_data.get('confidence', 0)
        timestamp = signal_data.get('timestamp', datetime.now())
        
        # Signal display
        if signal_type == 'BUY' and confidence >= 0.8:
            st.success("🟢 STRONG BUY SIGNAL")
            st.info(f"Confidence: {confidence:.1%} • Time: {timestamp.strftime('%H:%M:%S')}")
        elif signal_type == 'SELL' and confidence >= 0.8:
            st.error("🔴 STRONG SELL SIGNAL")
            st.info(f"Confidence: {confidence:.1%} • Time: {timestamp.strftime('%H:%M:%S')}")
        elif signal_type in ['BUY', 'SELL'] and confidence >= 0.5:
            st.warning(f"🟡 WEAK {signal_type} SIGNAL")
            st.info(f"Confidence: {confidence:.1%} • Time: {timestamp.strftime('%H:%M:%S')}")
        else:
            st.info("⚪ NO SIGNAL")
            st.info("Waiting for setup • Market analysis ongoing")
        
        # Signal strength meter
        self._render_confidence_meter(confidence)
    
    def _render_filter_breakdown(self, signal_data):
        """Render individual filter status"""
        st.markdown("#### 🔍 Filter Breakdown")
        
        filters = signal_data.get('filters', {})
        
        filter_names = [
            ('volume', 'Volume Filter'),
            ('levels', 'Key Levels'),
            ('pattern', 'Pattern Recognition'),
            ('orderflow', 'Order Flow'),
            ('liquidity', 'Liquidity Sweep')
        ]
        
        passed_filters = 0
        total_filters = len(filter_names)
        
        for key, name in filter_names:
            status = filters.get(key, False)
            if status:
                st.success(f"✅ {name}")
                passed_filters += 1
            else:
                st.error(f"❌ {name}")
        
        # Summary
        st.info(f"📊 Filters Passed: {passed_filters}/{total_filters}")
    
    def _render_confidence_meter(self, confidence):
        """Render confidence level meter"""
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=confidence * 100,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Signal Confidence"},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 80], 'color': "yellow"},
                    {'range': [80, 100], 'color': "green"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 80
                }
            }
        ))
        
        fig.update_layout(height=200)
        st.plotly_chart(fig, use_container_width=True)
    
    def _generate_mock_signal(self):
        """Generate mock signal data for testing"""
        signals = ['BUY', 'SELL', 'NONE']
        signal = np.random.choice(signals, p=[0.3, 0.2, 0.5])
        confidence = np.random.uniform(0.3, 0.95) if signal != 'NONE' else 0.0
        
        return {
            'signal': signal,
            'confidence': confidence,
            'timestamp': datetime.now(),
            'filters': {
                'volume': np.random.choice([True, False], p=[0.7, 0.3]),
                'levels': np.random.choice([True, False], p=[0.6, 0.4]),
                'pattern': np.random.choice([True, False], p=[0.5, 0.5]),
                'orderflow': np.random.choice([True, False], p=[0.4, 0.6]),
                'liquidity': np.random.choice([True, False], p=[0.3, 0.7])
            }
        }
