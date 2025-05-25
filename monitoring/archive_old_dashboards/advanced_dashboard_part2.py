"""
🚀 ADVANCED LIVE TRADING DASHBOARD - TEIL 2
Dashboard-Funktionen und Datenverarbeitung
"""

def refresh_all_data():
    """Refresh all dashboard data with error handling"""
    api = st.session_state.api_client
    refresh_status = {'success': 0, 'errors': []}
    
    # Server time check
    server_time = api.get_server_time()
    if server_time['success']:
        st.session_state.environment_status = 'CONNECTED'
        if not server_time['synchronized']:
            refresh_status['errors'].append('⚠️ Server time not synchronized')
    else:
        st.session_state.environment_status = 'DISCONNECTED'
        refresh_status['errors'].append('❌ Cannot connect to Bybit API')
    
    # Get live ticker data
    ticker_data = api.get_live_ticker('BTCUSDT')
    if ticker_data['success']:
        st.session_state.live_data = ticker_data
        refresh_status['success'] += 1
    else:
        refresh_status['errors'].append(f"❌ Ticker: {ticker_data.get('error')}")
    
    # Get order book data
    book_data = api.get_order_book('BTCUSDT', 20)
    if book_data['success']:
        st.session_state.order_book = book_data
        refresh_status['success'] += 1
    else:
        refresh_status['errors'].append(f"❌ Order Book: {book_data.get('error')}")
    
    # Get account balance
    balance_data = api.get_account_balance()
    if balance_data['success']:
        st.session_state.account_balance = balance_data
        refresh_status['success'] += 1
        # Update portfolio value from real balance
        wallet_list = balance_data['data'].get('list', [])
        for wallet in wallet_list:
            for coin in wallet.get('coin', []):
                if coin.get('coin') == 'USDT':
                    st.session_state.portfolio_value = float(coin.get('walletBalance', 50.0))
                    break
    else:
        refresh_status['errors'].append(f"❌ Balance: {balance_data.get('error')}")
    
    # Get chart data
    chart_data = api.get_kline_data('BTCUSDT', '5', 200)
    if chart_data['success']:
        st.session_state.chart_data = chart_data
        refresh_status['success'] += 1
    else:
        refresh_status['errors'].append(f"❌ Chart Data: {chart_data.get('error')}")
    
    # Update last refresh time
    st.session_state.last_refresh = datetime.now()
    
    return refresh_status


def render_dashboard_header():
    """Render professional dashboard header"""
    environment_color = "#10b981" if st.session_state.api_client.environment == "MAINNET" else "#f59e0b"
    
    st.markdown(f"""
    <div class="dashboard-header">
        <h1 class="dashboard-title">🚀 ADVANCED LIVE TRADING DASHBOARD</h1>
        <p class="dashboard-subtitle">
            Enhanced Smart Money Strategy • Professional Grade • 
            <span style="color: {environment_color}; font-weight: bold;">
                {st.session_state.api_client.environment} ENVIRONMENT
            </span>
        </p>
        <div style="margin-top: 15px;">
            <span class="status-indicator status-{st.session_state.get('environment_status', 'unknown').lower()}">
                📡 {st.session_state.get('environment_status', 'UNKNOWN')}
            </span>
            {"<span class='status-indicator status-active'>🤖 TRADING ACTIVE</span>" if st.session_state.get('trading_active') else "<span class='status-indicator status-paused'>⏸️ TRADING PAUSED</span>"}
            {"<span class='status-indicator status-emergency'>🛑 EMERGENCY STOP</span>" if st.session_state.get('emergency_stop') else ""}
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_control_bar():
    """Render control bar with refresh and status"""
    col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
    
    with col1:
        refresh_clicked = st.button(
            "🔄 Refresh All Data", 
            type="primary",
            help="Refresh all live market data"
        )
        
        if refresh_clicked:
            with st.spinner("🔄 Refreshing live data..."):
                refresh_status = refresh_all_data()
                
                if refresh_status['success'] > 0:
                    st.success(f"✅ Refreshed {refresh_status['success']} data sources")
                
                if refresh_status['errors']:
                    for error in refresh_status['errors']:
                        st.error(error)
                
                st.rerun()
    
    with col2:
        auto_refresh = st.checkbox(
            "🔄 Auto-Refresh", 
            value=st.session_state.get('auto_refresh', True),
            help=f"Auto-refresh every {st.session_state.get('refresh_interval', 30)} seconds"
        )
        st.session_state.auto_refresh = auto_refresh
    
    with col3:
        refresh_interval = st.selectbox(
            "⏱️ Interval",
            [15, 30, 60, 120],
            index=1,
            help="Auto-refresh interval in seconds"
        )
        st.session_state.refresh_interval = refresh_interval
    
    with col4:
        last_refresh = st.session_state.get('last_refresh')
        if last_refresh:
            time_ago = (datetime.now() - last_refresh).total_seconds()
            st.metric("🕒 Last Update", f"{int(time_ago)}s ago")
        else:
            st.metric("🕒 Last Update", "Never")
    
    with col5:
        st.markdown(f'<div class="live-indicator">🔴 <span class="live-dot"></span> LIVE</div>', unsafe_allow_html=True)


def render_live_price_section():
    """Render live price and market data section"""
    st.markdown('<div class="widget-container">', unsafe_allow_html=True)
    st.markdown('<h2 class="widget-header">💰 LIVE MARKET DATA</h2>', unsafe_allow_html=True)
    
    live_data = st.session_state.live_data
    
    if live_data.get('success'):
        price = live_data['price']
        change_24h = live_data['change_24h']
        bid = live_data.get('bid', 0)
        ask = live_data.get('ask', 0)
        volume_24h = live_data.get('volume_24h', 0)
        high_24h = live_data.get('high_24h', 0)
        low_24h = live_data.get('low_24h', 0)
        
        # Main price display
        change_color = "#10b981" if change_24h >= 0 else "#ef4444"
        change_symbol = "▲" if change_24h >= 0 else "▼"
        
        st.markdown(f"""
        <div class="price-display">
            <div class="price-main">${price:,.2f}</div>
            <div class="price-change" style="color: {change_color};">
                {change_symbol} {change_24h:+.2f}% (24h)
            </div>
            <div class="price-meta">
                BTC/USDT • Last updated: {live_data['timestamp'].strftime('%H:%M:%S')}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Market metrics
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            st.metric("💚 Best Bid", f"${bid:,.2f}", help="Highest buy price")
        
        with col2:
            st.metric("❤️ Best Ask", f"${ask:,.2f}", help="Lowest sell price")
        
        with col3:
            spread = ask - bid if ask > 0 and bid > 0 else 0
            spread_pct = (spread / price * 100) if price > 0 else 0
            st.metric("📊 Spread", f"${spread:.2f}", f"{spread_pct:.3f}%")
        
        with col4:
            st.metric("📈 24h High", f"${high_24h:,.0f}")
        
        with col5:
            st.metric("📉 24h Low", f"${low_24h:,.0f}")
        
        with col6:
            st.metric("📊 24h Volume", f"{volume_24h:,.0f} BTC")
        
        # Market health indicators
        volatility = ((high_24h - low_24h) / low_24h * 100) if low_24h > 0 else 0
        price_position = ((price - low_24h) / (high_24h - low_24h) * 100) if high_24h > low_24h else 50
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("🎯 Price Position", f"{price_position:.1f}%", "In 24h range")
        
        with col2:
            volatility_color = "normal" if volatility < 5 else "inverse"
            st.metric("📊 24h Volatility", f"{volatility:.2f}%", delta_color=volatility_color)
        
        with col3:
            liquidity_score = min(100, (volume_24h / 1000))  # Simplified liquidity score
            st.metric("🌊 Liquidity Score", f"{liquidity_score:.0f}/100")
        
    else:
        st.error(f"❌ Unable to fetch live price data: {live_data.get('error', 'Unknown error')}")
        st.info("🔄 Try refreshing the data or check your internet connection")
    
    st.markdown('</div>', unsafe_allow_html=True)


def render_order_book_section():
    """Render order book visualization"""
    st.markdown('<div class="widget-container">', unsafe_allow_html=True)
    st.markdown('<h2 class="widget-header">📊 LIVE ORDER BOOK</h2>', unsafe_allow_html=True)
    
    book_data = st.session_state.order_book
    
    if book_data.get('success'):
        asks = book_data.get('asks', [])
        bids = book_data.get('bids', [])
        
        if asks and bids:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🔴 ASKS (Sell Orders)")
                
                # Process asks data
                ask_df = pd.DataFrame(asks[:10], columns=['Price', 'Size'])
                ask_df['Total'] = (ask_df['Price'] * ask_df['Size']).round(0)
                ask_df = ask_df.sort_values('Price', ascending=False)
                
                # Order book table
                st.markdown('<div class="order-book">', unsafe_allow_html=True)
                st.markdown('''
                <div class="order-book-header">
                    <span>Price (USDT)</span>
                    <span>Size (BTC)</span>
                    <span>Total (USDT)</span>
                </div>
                ''', unsafe_allow_html=True)
                
                for _, row in ask_df.iterrows():
                    st.markdown(f'''
                    <div class="order-book-row">
                        <span class="sell-price">${row['Price']:,.2f}</span>
                        <span>{row['Size']:.4f}</span>
                        <span>${row['Total']:,.0f}</span>
                    </div>
                    ''', unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown("#### 🟢 BIDS (Buy Orders)")
                
                # Process bids data
                bid_df = pd.DataFrame(bids[:10], columns=['Price', 'Size'])
                bid_df['Total'] = (bid_df['Price'] * bid_df['Size']).round(0)
                bid_df = bid_df.sort_values('Price', ascending=False)
                
                # Order book table
                st.markdown('<div class="order-book">', unsafe_allow_html=True)
                st.markdown('''
                <div class="order-book-header">
                    <span>Price (USDT)</span>
                    <span>Size (BTC)</span>
                    <span>Total (USDT)</span>
                </div>
                ''', unsafe_allow_html=True)
                
                for _, row in bid_df.iterrows():
                    st.markdown(f'''
                    <div class="order-book-row">
                        <span class="buy-price">${row['Price']:,.2f}</span>
                        <span>{row['Size']:.4f}</span>
                        <span>${row['Total']:,.0f}</span>
                    </div>
                    ''', unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Market depth visualization
            render_market_depth_chart(bids, asks)
            
        else:
            st.warning("📭 Order book data is empty")
    
    else:
        st.error(f"❌ Unable to fetch order book: {book_data.get('error', 'Unknown error')}")
    
    st.markdown('</div>', unsafe_allow_html=True)


def render_market_depth_chart(bids, asks):
    """Render market depth chart"""
    if not bids or not asks:
        return
    
    st.markdown("#### 📈 Market Depth Visualization")
    
    # Prepare data
    bid_df = pd.DataFrame(bids[:15], columns=['price', 'size'])
    ask_df = pd.DataFrame(asks[:15], columns=['price', 'size'])
    
    bid_df['cumulative'] = bid_df['size'].cumsum()
    ask_df['cumulative'] = ask_df['size'].cumsum()
    
    # Create depth chart
    fig = go.Figure()
    
    # Bids (green area)
    fig.add_trace(go.Scatter(
        x=bid_df['price'],
        y=bid_df['cumulative'],
        mode='lines',
        fill='tonexty',
        name='Bids',
        line=dict(color='#10b981', width=2),
        fillcolor='rgba(16, 185, 129, 0.3)',
        hovertemplate='<b>Bid</b><br>Price: $%{x:,.2f}<br>Cumulative: %{y:.4f} BTC<extra></extra>'
    ))
    
    # Asks (red area)
    fig.add_trace(go.Scatter(
        x=ask_df['price'],
        y=ask_df['cumulative'],
        mode='lines',
        fill='tonexty',
        name='Asks',
        line=dict(color='#ef4444', width=2),
        fillcolor='rgba(239, 68, 68, 0.3)',
        hovertemplate='<b>Ask</b><br>Price: $%{x:,.2f}<br>Cumulative: %{y:.4f} BTC<extra></extra>'
    ))
    
    # Add current price line
    current_price = st.session_state.live_data.get('price', 0)
    if current_price > 0:
        fig.add_vline(
            x=current_price,
            line_dash="dash",
            line_color="yellow",
            line_width=2,
            annotation_text=f"Current: ${current_price:,.2f}",
            annotation_position="top"
        )
    
    fig.update_layout(
        title="Market Depth - BTC/USDT",
        xaxis_title="Price (USDT)",
        yaxis_title="Cumulative Size (BTC)",
        height=350,
        showlegend=True,
        template="plotly_white",
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_portfolio_section():
    """Render portfolio monitoring section"""
    st.markdown('<div class="widget-container">', unsafe_allow_html=True)
    st.markdown('<h2 class="widget-header">💼 PORTFOLIO MONITORING</h2>', unsafe_allow_html=True)
    
    balance_data = st.session_state.account_balance
    portfolio_value = st.session_state.portfolio_value
    
    if balance_data.get('success'):
        # Extract detailed balance information
        wallet_list = balance_data['data'].get('list', [])
        
        if wallet_list:
            wallet = wallet_list[0]  # Unified account
            coins = wallet.get('coin', [])
            
            # Display all coin balances
            col1, col2, col3, col4 = st.columns(4)
            
            usdt_balance = 0
            btc_balance = 0
            total_equity = 0
            
            for coin in coins:
                coin_name = coin.get('coin', '')
                wallet_balance = float(coin.get('walletBalance', 0))
                equity = float(coin.get('equity', 0))
                
                if coin_name == 'USDT':
                    usdt_balance = wallet_balance
                elif coin_name == 'BTC':
                    btc_balance = wallet_balance
                
                total_equity += equity
            
            with col1:
                st.metric(
                    "💰 USDT Balance",
                    f"${usdt_balance:.2f}",
                    "Available for trading"
                )
            
            with col2:
                st.metric(
                    "₿ BTC Balance",
                    f"{btc_balance:.6f} BTC",
                    f"~${btc_balance * st.session_state.live_data.get('price', 0):,.2f}" if btc_balance > 0 else "No BTC"
                )
            
            with col3:
                start_value = 50.0  # Initial investment
                total_pnl = total_equity - start_value
                pnl_pct = (total_pnl / start_value) * 100 if start_value > 0 else 0
                
                st.metric(
                    "📊 Total P&L",
                    f"${total_pnl:+.2f}",
                    f"{pnl_pct:+.2f}%",
                    delta_color="normal" if total_pnl >= 0 else "inverse"
                )
            
            with col4:
                st.metric(
                    "🎯 Portfolio Value",
                    f"${total_equity:.2f}",
                    "Total Equity"
                )
            
            # Portfolio allocation chart
            if total_equity > 0:
                render_portfolio_allocation_chart(coins, total_equity)
        
        else:
            st.warning("📭 No wallet data available")
    
    else:
        st.error(f"❌ Portfolio data unavailable: {balance_data.get('error', 'Unknown error')}")
        
        # Show simulated portfolio
        st.info("📊 Showing simulated portfolio data")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("💰 Simulated Balance", f"${portfolio_value:.2f}")
        
        with col2:
            daily_pnl = st.session_state.get('daily_pnl', np.random.uniform(-2, 3))
            st.metric("📈 Daily P&L", f"${daily_pnl:+.2f}")
        
        with col3:
            total_pnl = portfolio_value - 50.0
            st.metric("📊 Total P&L", f"${total_pnl:+.2f}")
        
        with col4:
            st.metric("🎯 Win Rate", "75.2%")
    
    st.markdown('</div>', unsafe_allow_html=True)


def render_portfolio_allocation_chart(coins, total_equity):
    """Render portfolio allocation pie chart"""
    st.markdown("#### 🥧 Portfolio Allocation")
    
    # Prepare data for pie chart
    allocation_data = []
    colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4']
    
    for i, coin in enumerate(coins):
        coin_name = coin.get('coin', '')
        equity = float(coin.get('equity', 0))
        
        if equity > 0.01:  # Only show coins with significant value
            percentage = (equity / total_equity) * 100
            allocation_data.append({
                'coin': coin_name,
                'value': equity,
                'percentage': percentage
            })
    
    if allocation_data:
        df = pd.DataFrame(allocation_data)
        
        fig = go.Figure(data=[go.Pie(
            labels=[f"{row['coin']}<br>${row['value']:.2f}" for _, row in df.iterrows()],
            values=df['percentage'],
            hole=0.4,
            marker_colors=colors[:len(df)],
            hovertemplate='<b>%{label}</b><br>%{percent}<br>$%{value:.2f}<extra></extra>'
        )])
        
        fig.update_layout(
            title="Portfolio Distribution",
            height=300,
            showlegend=True,
            template="plotly_white"
        )
        
        st.plotly_chart(fig, use_container_width=True)
