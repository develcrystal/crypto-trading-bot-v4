"""
Professional Charts Module for Advanced Dashboard
Advanced candlestick charts with technical indicators
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class ProfessionalChart:
    """Professional trading chart with technical indicators"""
    
    def __init__(self, api_client):
        self.api = api_client
    
    def render(self, symbol='BTCUSDT', timeframe='5', indicators=None):
        """Render professional candlestick chart"""
        if indicators is None:
            indicators = ['EMA', 'RSI', 'MACD', 'Volume']
        
        # Get chart data
        chart_data = self.api.get_kline_data(symbol, timeframe, 200)
        
        if not chart_data.get('success'):
            st.error(f"❌ Failed to load chart data: {chart_data.get('error')}")
            return None
        
        df = chart_data['data']
        
        # Add technical indicators
        df = self._calculate_indicators(df)
        
        # Create chart layout
        rows = 1
        if 'RSI' in indicators:
            rows += 1
        if 'MACD' in indicators:
            rows += 1
        if 'Volume' in indicators:
            rows += 1
        
        # Create subplots
        fig = make_subplots(
            rows=rows,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.02,
            subplot_titles=self._get_subplot_titles(indicators),
            row_heights=self._get_row_heights(indicators)
        )
        
        # Main candlestick chart
        self._add_candlesticks(fig, df, row=1)
        
        # Add moving averages
        if 'EMA' in indicators:
            self._add_moving_averages(fig, df, row=1)
        
        # Add support/resistance levels
        self._add_support_resistance(fig, df, row=1)
        
        # Add additional indicators
        current_row = 2
        
        if 'Volume' in indicators:
            self._add_volume(fig, df, row=current_row)
            current_row += 1
        
        if 'RSI' in indicators:
            self._add_rsi(fig, df, row=current_row)
            current_row += 1
        
        if 'MACD' in indicators:
            self._add_macd(fig, df, row=current_row)
            current_row += 1
        
        # Update layout
        fig.update_layout(
            title=f"{symbol} Professional Chart ({timeframe}min)",
            xaxis_rangeslider_visible=False,
            height=600 + (rows - 1) * 150,
            showlegend=True,
            template="plotly_dark",
            font=dict(size=12),
            hovermode='x unified'
        )
        
        # Style the chart
        fig.update_xaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(128, 128, 128, 0.2)'
        )
        fig.update_yaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(128, 128, 128, 0.2)'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        return df
    
    def _calculate_indicators(self, df):
        """Calculate technical indicators"""
        # Moving averages
        df['ema_9'] = df['close'].ewm(span=9).mean()
        df['ema_21'] = df['close'].ewm(span=21).mean()
        df['ema_50'] = df['close'].ewm(span=50).mean()
        df['sma_200'] = df['close'].rolling(window=200).mean()
        
        # RSI
        df['rsi'] = self._calculate_rsi(df['close'], 14)
        
        # MACD
        macd_data = self._calculate_macd(df['close'])
        df['macd'] = macd_data['macd']
        df['macd_signal'] = macd_data['signal']
        df['macd_histogram'] = macd_data['histogram']
        
        # Support/Resistance levels
        df = self._calculate_support_resistance(df)
        
        return df
    
    def _add_candlesticks(self, fig, df, row):
        """Add candlestick chart"""
        fig.add_trace(
            go.Candlestick(
                x=df['timestamp'],
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'],
                name=f'Price',
                increasing_line_color='#26a69a',
                decreasing_line_color='#ef5350',
                increasing_fillcolor='#26a69a',
                decreasing_fillcolor='#ef5350'
            ),
            row=row, col=1
        )
    
    def _add_moving_averages(self, fig, df, row):
        """Add moving average lines"""
        # EMA 9 (fast)
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df['ema_9'],
                mode='lines',
                name='EMA 9',
                line=dict(color='#ffa726', width=1),
                opacity=0.8
            ),
            row=row, col=1
        )
        
        # EMA 21 (medium)
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df['ema_21'],
                mode='lines',
                name='EMA 21',
                line=dict(color='#42a5f5', width=1),
                opacity=0.8
            ),
            row=row, col=1
        )
        
        # EMA 50 (slow)
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df['ema_50'],
                mode='lines',
                name='EMA 50',
                line=dict(color='#ab47bc', width=2),
                opacity=0.8
            ),
            row=row, col=1
        )
    
    def _add_support_resistance(self, fig, df, row):
        """Add support and resistance levels"""
        if 'support_level' in df.columns and 'resistance_level' in df.columns:
            # Support level
            support_level = df['support_level'].iloc[-1]
            if not pd.isna(support_level):
                fig.add_hline(
                    y=support_level,
                    line_dash="dash",
                    line_color="#10b981",
                    line_width=2,
                    annotation_text=f"Support: ${support_level:,.0f}",
                    annotation_position="right",
                    row=row
                )
            
            # Resistance level
            resistance_level = df['resistance_level'].iloc[-1]
            if not pd.isna(resistance_level):
                fig.add_hline(
                    y=resistance_level,
                    line_dash="dash",
                    line_color="#ef4444",
                    line_width=2,
                    annotation_text=f"Resistance: ${resistance_level:,.0f}",
                    annotation_position="right",
                    row=row
                )
    
    def _add_volume(self, fig, df, row):
        """Add volume bars"""
        colors = ['#26a69a' if close >= open else '#ef5350' 
                 for close, open in zip(df['close'], df['open'])]
        
        fig.add_trace(
            go.Bar(
                x=df['timestamp'],
                y=df['volume'],
                name='Volume',
                marker_color=colors,
                opacity=0.7
            ),
            row=row, col=1
        )
        
        # Add volume moving average
        df['volume_sma'] = df['volume'].rolling(window=20).mean()
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df['volume_sma'],
                mode='lines',
                name='Volume SMA',
                line=dict(color='yellow', width=1),
                opacity=0.8
            ),
            row=row, col=1
        )
    
    def _add_rsi(self, fig, df, row):
        """Add RSI indicator"""
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df['rsi'],
                mode='lines',
                name='RSI',
                line=dict(color='#ffa726', width=2)
            ),
            row=row, col=1
        )
        
        # Add overbought/oversold lines
        fig.add_hline(y=70, line_dash="dash", line_color="red", 
                     annotation_text="Overbought", row=row)
        fig.add_hline(y=30, line_dash="dash", line_color="green", 
                     annotation_text="Oversold", row=row)
        fig.add_hline(y=50, line_dash="dot", line_color="gray", 
                     annotation_text="Midline", row=row)
    
    def _add_macd(self, fig, df, row):
        """Add MACD indicator"""
        # MACD line
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df['macd'],
                mode='lines',
                name='MACD',
                line=dict(color='#42a5f5', width=2)
            ),
            row=row, col=1
        )
        
        # Signal line
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df['macd_signal'],
                mode='lines',
                name='Signal',
                line=dict(color='#ff7043', width=2)
            ),
            row=row, col=1
        )
        
        # Histogram
        colors = ['#26a69a' if val >= 0 else '#ef5350' for val in df['macd_histogram']]
        fig.add_trace(
            go.Bar(
                x=df['timestamp'],
                y=df['macd_histogram'],
                name='Histogram',
                marker_color=colors,
                opacity=0.7
            ),
            row=row, col=1
        )
        
        # Zero line
        fig.add_hline(y=0, line_dash="dot", line_color="gray", row=row)
    
    def _calculate_rsi(self, prices, period=14):
        """Calculate RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_macd(self, prices, fast=12, slow=26, signal=9):
        """Calculate MACD"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd = ema_fast - ema_slow
        macd_signal = macd.ewm(span=signal).mean()
        macd_histogram = macd - macd_signal
        
        return {
            'macd': macd,
            'signal': macd_signal,
            'histogram': macd_histogram
        }
    
    def _calculate_support_resistance(self, df, lookback=20):
        """Calculate support and resistance levels"""
        df['support_level'] = df['low'].rolling(window=lookback).min()
        df['resistance_level'] = df['high'].rolling(window=lookback).max()
        return df
    
    def _get_subplot_titles(self, indicators):
        """Get subplot titles based on indicators"""
        titles = ['Price Chart']
        
        if 'Volume' in indicators:
            titles.append('Volume')
        if 'RSI' in indicators:
            titles.append('RSI (14)')
        if 'MACD' in indicators:
            titles.append('MACD (12,26,9)')
        
        return titles
    
    def _get_row_heights(self, indicators):
        """Get row heights based on number of indicators"""
        heights = [0.6]  # Main chart takes 60%
        
        remaining = 0.4
        additional_indicators = sum([
            'Volume' in indicators,
            'RSI' in indicators,
            'MACD' in indicators
        ])
        
        if additional_indicators > 0:
            indicator_height = remaining / additional_indicators
            heights.extend([indicator_height] * additional_indicators)
        
        return heights

class MarketRegimeChart:
    """Market regime detection visualization"""
    
    def __init__(self):
        pass
    
    def render(self, regime_data=None):
        """Render market regime detection chart"""
        if regime_data is None:
            regime_data = self._generate_mock_regime_data()
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            self._render_regime_timeline(regime_data)
        
        with col2:
            self._render_regime_gauge(regime_data)
    
    def _render_regime_timeline(self, regime_data):
        """Render regime timeline chart"""
        st.markdown("#### 🧠 Market Regime Timeline")
        
        df = pd.DataFrame(regime_data['timeline'])
        
        fig = go.Figure()
        
        # Color mapping for regimes
        color_map = {
            'BULL': '#10b981',
            'BEAR': '#ef4444', 
            'SIDEWAYS': '#f59e0b'
        }
        
        # Add regime periods as horizontal bars
        for i, row in df.iterrows():
            fig.add_shape(
                type="rect",
                x0=row['start_time'],
                x1=row['end_time'],
                y0=0,
                y1=1,
                fillcolor=color_map.get(row['regime'], '#6b7280'),
                opacity=0.7,
                line_width=0
            )
            
            # Add regime labels
            mid_time = row['start_time'] + (row['end_time'] - row['start_time']) / 2
            fig.add_annotation(
                x=mid_time,
                y=0.5,
                text=f"{row['regime']}<br>{row['confidence']:.1%}",
                showarrow=False,
                font=dict(color="white", size=10),
                bgcolor=color_map.get(row['regime'], '#6b7280'),
                bordercolor="white",
                borderwidth=1
            )
        
        fig.update_layout(
            title="Market Regime Detection Over Time",
            xaxis_title="Time",
            yaxis=dict(showticklabels=False, range=[0, 1]),
            height=200,
            showlegend=False,
            template="plotly_white"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_regime_gauge(self, regime_data):
        """Render current regime confidence gauge"""
        st.markdown("#### 🎯 Current Regime")
        
        current = regime_data['current']
        regime = current['regime']
        confidence = current['confidence']
        
        # Regime display
        color_map = {
            'BULL': '#10b981',
            'BEAR': '#ef4444',
            'SIDEWAYS': '#f59e0b'
        }
        
        st.markdown(f"""
        <div style="background: {color_map.get(regime, '#6b7280')}; 
                    color: white; padding: 20px; border-radius: 10px; text-align: center;">
            <h2 style="margin: 0;">{regime} MARKET</h2>
            <h3 style="margin: 5px 0;">Confidence: {confidence:.1%}</h3>
            <p style="margin: 0; opacity: 0.9;">
                Duration: {current.get('duration', 'Unknown')}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Confidence gauge
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=confidence * 100,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Confidence Level"},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': color_map.get(regime, '#6b7280')},
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
        
        fig.update_layout(height=250)
        st.plotly_chart(fig, use_container_width=True)
        
        # Regime factors
        st.markdown("**Key Factors:**")
        factors = current.get('factors', {})
        for factor, value in factors.items():
            if isinstance(value, bool):
                icon = "✅" if value else "❌"
                st.markdown(f"{icon} {factor}")
            else:
                st.markdown(f"📊 {factor}: {value}")
    
    def _generate_mock_regime_data(self):
        """Generate mock regime data for testing"""
        now = datetime.now()
        
        return {
            'current': {
                'regime': np.random.choice(['BULL', 'BEAR', 'SIDEWAYS'], p=[0.4, 0.3, 0.3]),
                'confidence': np.random.uniform(0.6, 0.95),
                'duration': f"{np.random.randint(30, 180)} minutes",
                'factors': {
                    'Price Trend': np.random.choice([True, False]),
                    'Volume Trend': np.random.choice([True, False]),
                    'MA Alignment': np.random.choice([True, False]),
                    'Volatility Level': f"{np.random.uniform(0.02, 0.08):.1%}"
                }
            },
            'timeline': [
                {
                    'regime': 'BULL',
                    'confidence': 0.85,
                    'start_time': now - timedelta(hours=4),
                    'end_time': now - timedelta(hours=2)
                },
                {
                    'regime': 'SIDEWAYS',
                    'confidence': 0.65,
                    'start_time': now - timedelta(hours=2),
                    'end_time': now - timedelta(hours=1)
                },
                {
                    'regime': 'BULL',
                    'confidence': 0.78,
                    'start_time': now - timedelta(hours=1),
                    'end_time': now
                }
            ]
        }
