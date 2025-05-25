"""
Portfolio Monitor Module for Advanced Dashboard
Advanced portfolio tracking with real-time P&L
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class AdvancedPortfolioMonitor:
    """Advanced portfolio monitoring with real-time tracking"""
    
    def __init__(self, api_client):
        self.api = api_client
    
    def render(self, initial_balance=50.0):
        """Render advanced portfolio monitoring"""
        col1, col2 = st.columns([2, 1])
        
        with col1:
            self._render_portfolio_overview(initial_balance)
            self._render_performance_chart()
        
        with col2:
            self._render_risk_dashboard()
            self._render_position_tracker()
    
    def _render_portfolio_overview(self, initial_balance):
        """Render portfolio overview metrics"""
        st.markdown("### 💼 PORTFOLIO OVERVIEW")
        
        # Get account balance
        balance_data = self.api.get_account_balance()
        current_balance = initial_balance  # Default fallback
        
        if balance_data.get('success'):
            # Extract USDT balance from API response
            wallet_list = balance_data['data'].get('list', [])
            for wallet in wallet_list:
                for coin in wallet.get('coin', []):
                    if coin.get('coin') == 'USDT':
                        current_balance = float(coin.get('walletBalance', initial_balance))
                        break
        
        # Calculate P&L
        total_pnl = current_balance - initial_balance
        pnl_percentage = (total_pnl / initial_balance) * 100
        
        # Daily P&L (simulated - in production, this would be calculated from trade history)
        daily_pnl = np.random.uniform(-2, 3)  # Simulated daily P&L
        daily_pnl_pct = (daily_pnl / current_balance) * 100
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "💰 Current Balance",
                f"${current_balance:.2f}",
                f"USDT Available"
            )
        
        with col2:
            st.metric(
                "📊 Total P&L",
                f"${total_pnl:+.2f}",
                f"{pnl_percentage:+.1f}%",
                delta_color="normal" if total_pnl >= 0 else "inverse"
            )
        
        with col3:
            st.metric(
                "📈 Daily P&L",
                f"${daily_pnl:+.2f}",
                f"{daily_pnl_pct:+.1f}%",
                delta_color="normal" if daily_pnl >= 0 else "inverse"
            )
        
        with col4:
            # Calculate ROI since inception
            days_trading = 7  # Simulated
            annualized_return = (pnl_percentage / days_trading) * 365 if days_trading > 0 else 0
            st.metric(
                "🎯 Annualized ROI",
                f"{annualized_return:+.1f}%",
                f"Based on {days_trading} days"
            )
    
    def _render_performance_chart(self):
        """Render equity curve and performance chart"""
        st.markdown("### 📈 EQUITY CURVE")
        
        # Generate mock equity curve data (in production, this would come from trade history)
        dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
        
        # Simulate realistic equity curve
        initial_value = 50.0
        returns = np.random.normal(0.002, 0.02, len(dates))  # 0.2% daily return, 2% volatility
        cumulative_returns = np.cumprod(1 + returns)
        equity_values = initial_value * cumulative_returns
        
        df = pd.DataFrame({
            'date': dates,
            'equity': equity_values,
            'returns': returns
        })
        
        # Create equity curve chart
        fig = go.Figure()
        
        # Equity line
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['equity'],
            mode='lines',
            name='Portfolio Value',
            line=dict(color='#3b82f6', width=3),
            fill='tonexty',
            fillcolor='rgba(59, 130, 246, 0.1)'
        ))
        
        # Add benchmark line (initial investment)
        fig.add_hline(
            y=initial_value,
            line_dash="dash",
            line_color="gray",
            annotation_text=f"Initial: ${initial_value}",
            annotation_position="right"
        )
        
        # Highlight current value
        current_value = df['equity'].iloc[-1]
        fig.add_scatter(
            x=[df['date'].iloc[-1]],
            y=[current_value],
            mode='markers',
            marker=dict(color='red', size=10),
            name=f'Current: ${current_value:.2f}'
        )
        
        fig.update_layout(
            title="Portfolio Equity Curve (30 Days)",
            xaxis_title="Date",
            yaxis_title="Portfolio Value (USD)",
            height=300,
            showlegend=True,
            template="plotly_white"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Performance statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            max_value = df['equity'].max()
            st.metric("📈 All-Time High", f"${max_value:.2f}")
        
        with col2:
            min_value = df['equity'].min()
            drawdown = ((max_value - min_value) / max_value) * 100
            st.metric("📉 Max Drawdown", f"-{drawdown:.1f}%")
        
        with col3:
            sharpe_ratio = (df['returns'].mean() / df['returns'].std()) * np.sqrt(365) if df['returns'].std() > 0 else 0
            st.metric("⚡ Sharpe Ratio", f"{sharpe_ratio:.2f}")
        
        with col4:
            win_rate = (df['returns'] > 0).mean() * 100
            st.metric("🎯 Win Rate", f"{win_rate:.1f}%")
    
    def _render_risk_dashboard(self):
        """Render risk management dashboard"""
        st.markdown("### 🛡️ RISK DASHBOARD")
        
        # Risk metrics (simulated - in production, calculated from actual positions)
        current_exposure = 15.50  # Current position value
        max_exposure = 25.00     # Max allowed exposure (50% of 50€)
        daily_risk_used = 2.80   # Risk used today
        daily_risk_limit = 5.00  # Daily risk limit (10% of 50€)
        max_drawdown_limit = 7.50  # Max drawdown limit (15% of 50€)
        current_drawdown = 1.20    # Current drawdown
        
        # Exposure gauge
        exposure_pct = (current_exposure / max_exposure) * 100
        
        st.markdown("#### 📊 Position Exposure")
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=exposure_pct,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Exposure %"},
            delta={'reference': 50},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgreen"},
                    {'range': [50, 80], 'color': "yellow"},
                    {'range': [80, 100], 'color': "red"}
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
        
        # Risk metrics
        st.markdown("#### 📋 Risk Metrics")
        
        risk_metrics = {
            "Current Exposure": f"${current_exposure:.2f} / ${max_exposure:.2f}",
            "Daily Risk Used": f"${daily_risk_used:.2f} / ${daily_risk_limit:.2f}",
            "Current Drawdown": f"${current_drawdown:.2f} / ${max_drawdown_limit:.2f}",
            "Risk Level": "SAFE" if exposure_pct < 50 else "MODERATE" if exposure_pct < 80 else "HIGH"
        }
        
        for metric, value in risk_metrics.items():
            st.markdown(f"**{metric}:** {value}")
        
        # Risk alerts
        if exposure_pct > 80:
            st.error("⚠️ HIGH EXPOSURE WARNING")
        elif daily_risk_used > daily_risk_limit * 0.8:
            st.warning("⚠️ Daily risk limit approaching")
        else:
            st.success("✅ Risk levels are healthy")
    
    def _render_position_tracker(self):
        """Render current positions tracker"""
        st.markdown("### 🎯 CURRENT POSITIONS")
        
        # Mock position data (in production, this would come from API)
        positions = [
            {
                'symbol': 'BTCUSDT',
                'side': 'LONG',
                'size': 0.00015,
                'entry_price': 104500,
                'current_price': 107200,
                'pnl': 2.70,
                'pnl_pct': 2.58
            }
        ]
        
        if positions:
            for pos in positions:
                # Position card
                side_color = "#10b981" if pos['side'] == 'LONG' else "#ef4444"
                pnl_color = "#10b981" if pos['pnl'] >= 0 else "#ef4444"
                
                st.markdown(f"""
                <div style="background: #f8fafc; padding: 15px; border-radius: 8px; 
                            border-left: 4px solid {side_color}; margin: 10px 0;">
                    <h4 style="margin: 0; color: {side_color};">
                        {pos['side']} {pos['symbol']}
                    </h4>
                    <div style="display: flex; justify-content: space-between; margin-top: 10px;">
                        <div>
                            <p style="margin: 2px 0;"><strong>Size:</strong> {pos['size']:.6f} BTC</p>
                            <p style="margin: 2px 0;"><strong>Entry:</strong> ${pos['entry_price']:,.0f}</p>
                            <p style="margin: 2px 0;"><strong>Current:</strong> ${pos['current_price']:,.0f}</p>
                        </div>
                        <div style="text-align: right;">
                            <p style="margin: 2px 0; color: {pnl_color}; font-weight: bold;">
                                <strong>P&L:</strong> ${pos['pnl']:+.2f}
                            </p>
                            <p style="margin: 2px 0; color: {pnl_color}; font-weight: bold;">
                                <strong>%:</strong> {pos['pnl_pct']:+.2f}%
                            </p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Position management buttons
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button(f"📉 Close Position", key=f"close_{pos['symbol']}"):
                        st.info("Position close order simulated")
                
                with col2:
                    if st.button(f"🛡️ Adjust SL", key=f"sl_{pos['symbol']}"):
                        st.info("Stop-loss adjustment simulated")
                
                with col3:
                    if st.button(f"🎯 Adjust TP", key=f"tp_{pos['symbol']}"):
                        st.info("Take-profit adjustment simulated")
        
        else:
            st.info("📭 No open positions")
            st.markdown("*Waiting for trading signals...*")

class TradeHistoryWidget:
    """Trade history and analysis widget"""
    
    def __init__(self):
        pass
    
    def render(self):
        """Render trade history table"""
        st.markdown("### 📋 RECENT TRADES")
        
        # Mock trade history (in production, this would come from database)
        trades = [
            {
                'timestamp': datetime.now() - timedelta(hours=2),
                'symbol': 'BTCUSDT',
                'side': 'BUY',
                'entry_price': 104500,
                'exit_price': 107200,
                'size': 0.00015,
                'pnl': 2.70,
                'pnl_pct': 2.58,
                'regime': 'BULL',
                'signal_strength': 4
            },
            {
                'timestamp': datetime.now() - timedelta(hours=5),
                'symbol': 'BTCUSDT',
                'side': 'SELL',
                'entry_price': 106800,
                'exit_price': 105200,
                'size': 0.00012,
                'pnl': 1.92,
                'pnl_pct': 1.50,
                'regime': 'BEAR',
                'signal_strength': 3
            },
            {
                'timestamp': datetime.now() - timedelta(hours=8),
                'symbol': 'BTCUSDT',
                'side': 'BUY',
                'entry_price': 105000,
                'exit_price': 104200,
                'size': 0.00010,
                'pnl': -0.80,
                'pnl_pct': -0.76,
                'regime': 'SIDEWAYS',
                'signal_strength': 2
            }
        ]
        
        if trades:
            # Create DataFrame
            df = pd.DataFrame(trades)
            
            # Display trades table
            for i, trade in enumerate(trades):
                side_color = "#10b981" if trade['side'] == 'BUY' else "#ef4444"
                pnl_color = "#10b981" if trade['pnl'] >= 0 else "#ef4444"
                
                col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
                
                with col1:
                    st.markdown(f"""
                    <div style="font-weight: bold;">
                        <span style="color: {side_color};">{trade['side']}</span> {trade['symbol']}
                    </div>
                    <div style="font-size: 0.8em; color: #666;">
                        {trade['timestamp'].strftime('%H:%M:%S')}
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div>Entry: ${trade['entry_price']:,.0f}</div>
                    <div>Exit: ${trade['exit_price']:,.0f}</div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                    <div style="color: {pnl_color}; font-weight: bold;">
                        ${trade['pnl']:+.2f}
                    </div>
                    <div style="color: {pnl_color}; font-size: 0.9em;">
                        {trade['pnl_pct']:+.2f}%
                    </div>
                    """, unsafe_allow_html=True)
                
                with col4:
                    regime_colors = {'BULL': '#10b981', 'BEAR': '#ef4444', 'SIDEWAYS': '#f59e0b'}
                    st.markdown(f"""
                    <div style="color: {regime_colors.get(trade['regime'], '#666')};">
                        {trade['regime']}
                    </div>
                    """, unsafe_allow_html=True)
                
                with col5:
                    # Signal strength stars
                    stars = "⭐" * trade['signal_strength'] + "☆" * (5 - trade['signal_strength'])
                    st.markdown(f"<div>{stars}</div>", unsafe_allow_html=True)
                
                st.markdown("---")
            
            # Trade statistics
            st.markdown("#### 📊 Trading Statistics")
            
            total_trades = len(trades)
            winning_trades = len([t for t in trades if t['pnl'] > 0])
            win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
            total_pnl = sum(t['pnl'] for t in trades)
            avg_win = np.mean([t['pnl'] for t in trades if t['pnl'] > 0]) if winning_trades > 0 else 0
            avg_loss = np.mean([t['pnl'] for t in trades if t['pnl'] < 0]) if (total_trades - winning_trades) > 0 else 0
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("🎯 Win Rate", f"{win_rate:.1f}%", f"{winning_trades}/{total_trades}")
            
            with col2:
                st.metric("💰 Total P&L", f"${total_pnl:+.2f}")
            
            with col3:
                st.metric("📈 Avg Win", f"${avg_win:.2f}")
            
            with col4:
                st.metric("📉 Avg Loss", f"${avg_loss:.2f}")
        
        else:
            st.info("📭 No trade history available")

class RiskAnalyticsWidget:
    """Advanced risk analytics and monitoring"""
    
    def __init__(self):
        pass
    
    def render(self):
        """Render risk analytics dashboard"""
        st.markdown("### 🔍 RISK ANALYTICS")
        
        col1, col2 = st.columns(2)
        
        with col1:
            self._render_var_analysis()
        
        with col2:
            self._render_correlation_analysis()
    
    def _render_var_analysis(self):
        """Render Value at Risk analysis"""
        st.markdown("#### 📊 Value at Risk (VaR)")
        
        # Mock VaR calculations (in production, based on actual position data)
        var_1d_95 = 1.85  # 1-day VaR at 95% confidence
        var_1d_99 = 2.45  # 1-day VaR at 99% confidence
        expected_shortfall = 3.20  # Expected shortfall (CVaR)
        
        st.markdown(f"""
        <div style="background: #f8fafc; padding: 15px; border-radius: 8px;">
            <p><strong>1-Day VaR (95%):</strong> <span style="color: #ef4444;">-${var_1d_95:.2f}</span></p>
            <p><strong>1-Day VaR (99%):</strong> <span style="color: #dc2626;">-${var_1d_99:.2f}</span></p>
            <p><strong>Expected Shortfall:</strong> <span style="color: #991b1b;">-${expected_shortfall:.2f}</span></p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("*Maximum expected loss on 95% of trading days: $1.85*")
    
    def _render_correlation_analysis(self):
        """Render correlation analysis"""
        st.markdown("#### 🔗 Market Correlation")
        
        # Mock correlation data
        correlations = {
            'BTC vs Portfolio': 0.92,
            'BTC vs DXY': -0.65,
            'BTC vs SPX': 0.71,
            'BTC vs GOLD': 0.23
        }
        
        for asset, corr in correlations.items():
            color = "#10b981" if abs(corr) < 0.7 else "#f59e0b" if abs(corr) < 0.9 else "#ef4444"
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; padding: 5px 0;">
                <span>{asset}:</span>
                <span style="color: {color}; font-weight: bold;">{corr:+.2f}</span>
            </div>
            """, unsafe_allow_html=True)
