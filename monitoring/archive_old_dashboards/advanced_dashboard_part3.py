"""
🚀 ADVANCED LIVE TRADING DASHBOARD - TEIL 3
Professional Charts und Trading Controls
"""

def render_professional_chart_section():
    """Render professional candlestick chart with indicators"""
    st.markdown('<div class="widget-container">', unsafe_allow_html=True)
    st.markdown('<h2 class="widget-header">📈 PROFESSIONAL TRADING CHART</h2>', unsafe_allow_html=True)
    
    chart_data = st.session_state.chart_data
    
    if chart_data.get('success'):
        df = chart_data['data']
        
        # Chart controls
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            timeframe = st.selectbox(
                "📊 Timeframe",
                ['1', '5', '15', '30', '60', '240'],
                index=1,
                format_func=lambda x: f"{x}min" if int(x) < 60 else f"{int(x)//60}h"
            )
        
        with col2:
            indicators = st.multiselect(
                "📊 Indicators",
                ['EMA', 'RSI', 'MACD', 'Volume', 'Bollinger Bands'],
                default=['EMA', 'Volume', 'RSI']
            )
        
        with col3:
            chart_style = st.selectbox(
                "🎨 Style",
                ['Candlestick', 'OHLC', 'Line'],
                index=0
            )
        
        with col4:
            if st.button("🔄 Update Chart"):
                # Refresh chart data with new timeframe
                new_chart_data = st.session_state.api_client.get_kline_data('BTCUSDT', timeframe, 200)
                if new_chart_data['success']:
                    st.session_state.chart_data = new_chart_data
                    df = new_chart_data['data']
                    st.rerun()
        
        # Calculate technical indicators
        df = calculate_technical_indicators(df)
        
        # Create chart
        fig = create_professional_chart(df, indicators, chart_style)
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Chart analysis
        render_chart_analysis(df)
        
    else:
        st.error(f"❌ Chart data unavailable: {chart_data.get('error', 'Unknown error')}")
        st.info("🔄 Try refreshing to load chart data")
    
    st.markdown('</div>', unsafe_allow_html=True)


def calculate_technical_indicators(df):
    """Calculate technical indicators for the chart"""
    if len(df) < 50:
        return df
    
    # Exponential Moving Averages
    df['ema_9'] = df['close'].ewm(span=9).mean()
    df['ema_21'] = df['close'].ewm(span=21).mean()
    df['ema_50'] = df['close'].ewm(span=50).mean()
    
    # RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    # MACD
    ema_12 = df['close'].ewm(span=12).mean()
    ema_26 = df['close'].ewm(span=26).mean()
    df['macd'] = ema_12 - ema_26
    df['macd_signal'] = df['macd'].ewm(span=9).mean()
    df['macd_histogram'] = df['macd'] - df['macd_signal']
    
    # Bollinger Bands
    df['bb_middle'] = df['close'].rolling(window=20).mean()
    bb_std = df['close'].rolling(window=20).std()
    df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
    df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
    
    # Support/Resistance
    df['support'] = df['low'].rolling(window=20).min()
    df['resistance'] = df['high'].rolling(window=20).max()
    
    return df


def create_professional_chart(df, indicators, chart_style):
    """Create professional trading chart"""
    rows = 1
    subplot_titles = ['BTC/USDT Price']
    
    # Count additional indicators
    if 'Volume' in indicators:
        rows += 1
        subplot_titles.append('Volume')
    if 'RSI' in indicators:
        rows += 1
        subplot_titles.append('RSI')
    if 'MACD' in indicators:
        rows += 1
        subplot_titles.append('MACD')
    
    # Create subplots
    fig = make_subplots(
        rows=rows,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.02,
        subplot_titles=subplot_titles,
        row_heights=[0.6] + [0.4/(rows-1)]*(rows-1) if rows > 1 else [1.0]
    )
    
    current_row = 1
    
    # Main price chart
    if chart_style == 'Candlestick':
        fig.add_trace(
            go.Candlestick(
                x=df['timestamp'],
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'],
                name='BTC/USDT',
                increasing_line_color='#26a69a',
                decreasing_line_color='#ef5350',
                increasing_fillcolor='#26a69a',
                decreasing_fillcolor='#ef5350'
            ),
            row=current_row, col=1
        )
    elif chart_style == 'OHLC':
        fig.add_trace(
            go.Ohlc(
                x=df['timestamp'],
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'],
                name='BTC/USDT'
            ),
            row=current_row, col=1
        )
    else:  # Line chart
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df['close'],
                mode='lines',
                name='BTC/USDT',
                line=dict(color='#3b82f6', width=2)
            ),
            row=current_row, col=1
        )
    
    # Add EMAs
    if 'EMA' in indicators:
        ema_colors = ['#ffa726', '#42a5f5', '#ab47bc']
        ema_periods = [('ema_9', 'EMA 9'), ('ema_21', 'EMA 21'), ('ema_50', 'EMA 50')]
        
        for i, (col, name) in enumerate(ema_periods):
            if col in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df['timestamp'],
                        y=df[col],
                        mode='lines',
                        name=name,
                        line=dict(color=ema_colors[i], width=1),
                        opacity=0.8
                    ),
                    row=current_row, col=1
                )
    
    # Add Bollinger Bands
    if 'Bollinger Bands' in indicators:
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df['bb_upper'],
                mode='lines',
                name='BB Upper',
                line=dict(color='gray', width=1, dash='dash'),
                opacity=0.6
            ),
            row=current_row, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df['bb_lower'],
                mode='lines',
                name='BB Lower',
                line=dict(color='gray', width=1, dash='dash'),
                fill='tonexty',
                fillcolor='rgba(128, 128, 128, 0.1)',
                opacity=0.6
            ),
            row=current_row, col=1
        )
    
    # Add support/resistance lines
    if len(df) > 0:
        current_support = df['support'].iloc[-1]
        current_resistance = df['resistance'].iloc[-1]
        
        if not pd.isna(current_support):
            fig.add_hline(
                y=current_support,
                line_dash="dash",
                line_color="#10b981",
                line_width=2,
                annotation_text=f"Support: ${current_support:,.0f}",
                annotation_position="right",
                row=current_row
            )
        
        if not pd.isna(current_resistance):
            fig.add_hline(
                y=current_resistance,
                line_dash="dash",
                line_color="#ef4444",
                line_width=2,
                annotation_text=f"Resistance: ${current_resistance:,.0f}",
                annotation_position="right",
                row=current_row
            )
    
    # Add Volume
    if 'Volume' in indicators:
        current_row += 1
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
            row=current_row, col=1
        )
        
        # Add volume SMA
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
            row=current_row, col=1
        )
    
    # Add RSI
    if 'RSI' in indicators:
        current_row += 1
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df['rsi'],
                mode='lines',
                name='RSI',
                line=dict(color='#ffa726', width=2)
            ),
            row=current_row, col=1
        )
        
        # Add RSI levels
        fig.add_hline(y=70, line_dash="dash", line_color="red", 
                     annotation_text="Overbought", row=current_row)
        fig.add_hline(y=30, line_dash="dash", line_color="green", 
                     annotation_text="Oversold", row=current_row)
        fig.add_hline(y=50, line_dash="dot", line_color="gray", 
                     annotation_text="Midline", row=current_row)
    
    # Add MACD
    if 'MACD' in indicators:
        current_row += 1
        
        # MACD line
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df['macd'],
                mode='lines',
                name='MACD',
                line=dict(color='#42a5f5', width=2)
            ),
            row=current_row, col=1
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
            row=current_row, col=1
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
            row=current_row, col=1
        )
        
        # Zero line
        fig.add_hline(y=0, line_dash="dot", line_color="gray", row=current_row)
    
    # Update layout
    fig.update_layout(
        title="BTC/USDT Professional Trading Chart",
        xaxis_rangeslider_visible=False,
        height=500 + (rows - 1) * 150,
        showlegend=True,
        template="plotly_dark",
        font=dict(size=11),
        hovermode='x unified'
    )
    
    # Style axes
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
    
    return fig


def render_chart_analysis(df):
    """Render technical analysis summary"""
    if len(df) < 50:
        return
    
    st.markdown("#### 📊 Technical Analysis Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Current values
    current_price = df['close'].iloc[-1]
    current_rsi = df['rsi'].iloc[-1] if 'rsi' in df.columns else 50
    current_macd = df['macd'].iloc[-1] if 'macd' in df.columns else 0
    
    with col1:
        # Trend analysis
        ema_9 = df['ema_9'].iloc[-1] if 'ema_9' in df.columns else current_price
        ema_21 = df['ema_21'].iloc[-1] if 'ema_21' in df.columns else current_price
        
        if current_price > ema_9 > ema_21:
            trend = "🟢 BULLISH"
            trend_color = "#10b981"
        elif current_price < ema_9 < ema_21:
            trend = "🔴 BEARISH"
            trend_color = "#ef4444"
        else:
            trend = "🟡 NEUTRAL"
            trend_color = "#f59e0b"
        
        st.markdown(f"**Trend:** <span style='color: {trend_color};'>{trend}</span>", unsafe_allow_html=True)
    
    with col2:
        # RSI analysis
        if current_rsi > 70:
            rsi_signal = "🔴 OVERBOUGHT"
            rsi_color = "#ef4444"
        elif current_rsi < 30:
            rsi_signal = "🟢 OVERSOLD"
            rsi_color = "#10b981"
        else:
            rsi_signal = "🟡 NEUTRAL"
            rsi_color = "#f59e0b"
        
        st.markdown(f"**RSI ({current_rsi:.1f}):** <span style='color: {rsi_color};'>{rsi_signal}</span>", unsafe_allow_html=True)
    
    with col3:
        # MACD analysis
        macd_signal = df['macd_signal'].iloc[-1] if 'macd_signal' in df.columns else 0
        
        if current_macd > macd_signal and current_macd > 0:
            macd_status = "🟢 BULLISH"
            macd_color = "#10b981"
        elif current_macd < macd_signal and current_macd < 0:
            macd_status = "🔴 BEARISH"
            macd_color = "#ef4444"
        else:
            macd_status = "🟡 NEUTRAL"
            macd_color = "#f59e0b"
        
        st.markdown(f"**MACD:** <span style='color: {macd_color};'>{macd_status}</span>", unsafe_allow_html=True)
    
    with col4:
        # Volume analysis
        current_volume = df['volume'].iloc[-1]
        avg_volume = df['volume'].rolling(window=20).mean().iloc[-1]
        
        if current_volume > avg_volume * 1.5:
            volume_status = "🟢 HIGH"
            volume_color = "#10b981"
        elif current_volume < avg_volume * 0.5:
            volume_status = "🔴 LOW"
            volume_color = "#ef4444"
        else:
            volume_status = "🟡 NORMAL"
            volume_color = "#f59e0b"
        
        st.markdown(f"**Volume:** <span style='color: {volume_color};'>{volume_status}</span>", unsafe_allow_html=True)


def render_market_regime_section():
    """Render market regime detection section"""
    st.markdown('<div class="widget-container">', unsafe_allow_html=True)
    st.markdown('<h2 class="widget-header">🧠 MARKET REGIME DETECTION</h2>', unsafe_allow_html=True)
    
    current_regime = st.session_state.get('current_regime', 'BULL')
    regime_confidence = st.session_state.get('regime_confidence', 0.87)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        # Current regime display
        regime_colors = {'BULL': '#10b981', 'BEAR': '#ef4444', 'SIDEWAYS': '#f59e0b'}
        regime_color = regime_colors.get(current_regime, '#6b7280')
        
        st.markdown(f"""
        <div style="background: {regime_color}; color: white; padding: 25px; 
                    border-radius: 15px; text-align: center; margin-bottom: 15px;">
            <h2 style="margin: 0; font-size: 2em;">{current_regime} MARKET</h2>
            <h3 style="margin: 10px 0;">Confidence: {regime_confidence:.1%}</h3>
            <p style="margin: 0; opacity: 0.9;">
                Duration: 2h 34m
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Regime parameters
        st.markdown("**🎯 Active Parameters:**")
        
        if current_regime == 'BULL':
            st.success("• Volume Threshold: 80k (-20%)")
            st.success("• Risk-Reward: 1.8:1 (+20%)")  
            st.success("• Liquidity Focus: Enhanced")
        elif current_regime == 'BEAR':
            st.warning("• Volume Threshold: 120k (+20%)")
            st.warning("• Risk-Reward: 1.4:1 (-10%)")
            st.warning("• Defensive Mode: Active")
        else:
            st.info("• Volume Threshold: 150k (+50%)")
            st.info("• Risk-Reward: 1.5:1 (Standard)")
            st.info("• Selective Mode: Active")
    
    with col3:
        # Regime confidence gauge
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=regime_confidence * 100,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Confidence"},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': regime_color},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 80], 'color': "#f59e0b"},
                    {'range': [80, 100], 'color': "#10b981"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 80
                }
            }
        ))
        
        fig.update_layout(height=200, font=dict(size=12))
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)


def render_trading_signals_section():
    """Render live trading signals section"""
    st.markdown('<div class="widget-container">', unsafe_allow_html=True)
    st.markdown('<h2 class="widget-header">⚡ LIVE TRADING SIGNALS</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("#### 🎯 Current Signal Status")
        
        # Simulate current signal (in production, this comes from the trading bot)
        signal_strength = np.random.choice([0, 1, 2, 3, 4, 5], p=[0.3, 0.2, 0.2, 0.15, 0.10, 0.05])
        signal_type = np.random.choice(['BUY', 'SELL', 'HOLD'], p=[0.4, 0.3, 0.3])
        
        if signal_strength >= 4:
            st.success(f"🟢 STRONG {signal_type} SIGNAL")
            st.info(f"Signal Strength: {signal_strength}/5 ⭐")
            st.info("✅ High confidence setup detected")
        elif signal_strength >= 2:
            st.warning(f"🟡 WEAK {signal_type} SIGNAL")
            st.info(f"Signal Strength: {signal_strength}/5 ⭐")
            st.info("⚠️ Low confidence - wait for confirmation")
        else:
            st.info("⚪ NO ACTIVE SIGNAL")
            st.info("📊 Market analysis ongoing")
            st.info("⏳ Waiting for setup")
        
        # Next signal check countdown
        next_check = np.random.randint(30, 300)
        st.markdown(f"**Next Analysis:** {next_check} seconds")
    
    with col2:
        st.markdown("#### 🔍 Enhanced Strategy Filters")
        
        # Filter status (simulated)
        filters = [
            ("Volume Filter", np.random.choice([True, False], p=[0.7, 0.3]), "100k threshold"),
            ("Key Levels", np.random.choice([True, False], p=[0.6, 0.4]), "S/R confirmation"),  
            ("Pattern Recognition", np.random.choice([True, False], p=[0.5, 0.5]), "Bullish engulfing"),
            ("Order Flow", np.random.choice([True, False], p=[0.4, 0.6]), "Smart money activity"),
            ("Liquidity Sweep", np.random.choice([True, False], p=[0.3, 0.7]), "Level breakthrough")
        ]
        
        passed_filters = 0
        
        for filter_name, status, description in filters:
            if status:
                st.success(f"✅ {filter_name}")
                st.caption(f"   {description}")
                passed_filters += 1
            else:
                st.error(f"❌ {filter_name}")
                st.caption(f"   {description}")
        
        # Filter summary
        filter_quality = "HIGH" if passed_filters >= 4 else "MEDIUM" if passed_filters >= 2 else "LOW"
        filter_color = "#10b981" if filter_quality == "HIGH" else "#f59e0b" if filter_quality == "MEDIUM" else "#ef4444"
        
        st.markdown(f"""
        <div style="background: {filter_color}; color: white; padding: 15px; 
                    border-radius: 8px; text-align: center; margin-top: 15px;">
            <strong>SIGNAL QUALITY: {filter_quality}</strong><br>
            {passed_filters}/5 Filters Passed
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
