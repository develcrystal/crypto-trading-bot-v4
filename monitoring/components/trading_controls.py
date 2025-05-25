        # Delivery methods
        st.markdown("**Delivery Methods:**")
        
        delivery_methods = {
            'Browser Notifications': st.checkbox("Browser Notifications", value=True),
            'Email Alerts': st.checkbox("Email Alerts", value=False),
            'Sound Alerts': st.checkbox("Sound Alerts", value=True),
            'Desktop Notifications': st.checkbox("Desktop Notifications", value=False)
        }
        
        if st.button("💾 Save Alert Settings", key="save_alerts"):
            st.success("Alert settings saved successfully!")
    
    def _render_recent_notifications(self):
        """Render recent notifications and alerts"""
        st.markdown("#### 📬 Recent Notifications")
        
        # Mock notification data (in production, this would come from a notification queue)
        notifications = [
            {
                'timestamp': datetime.now() - timedelta(minutes=5),
                'type': 'TRADE_EXECUTED',
                'message': 'BUY order executed at $107,200',
                'severity': 'info'
            },
            {
                'timestamp': datetime.now() - timedelta(minutes=15),
                'type': 'PROFIT_ALERT',
                'message': 'Profit target reached: +$5.20',
                'severity': 'success'
            },
            {
                'timestamp': datetime.now() - timedelta(minutes=30),
                'type': 'REGIME_CHANGE',
                'message': 'Market regime changed to BULL (0.87 confidence)',
                'severity': 'info'
            },
            {
                'timestamp': datetime.now() - timedelta(hours=1),
                'type': 'RISK_WARNING',
                'message': 'Daily risk limit 80% used',
                'severity': 'warning'
            },
            {
                'timestamp': datetime.now() - timedelta(hours=2),
                'type': 'SYSTEM_STATUS',
                'message': 'Trading bot restarted successfully',
                'severity': 'info'
            }
        ]
        
        # Display notifications
        for notif in notifications:
            severity_colors = {
                'info': '#3b82f6',
                'success': '#10b981',
                'warning': '#f59e0b',
                'error': '#ef4444'
            }
            
            severity_icons = {
                'info': 'ℹ️',
                'success': '✅',
                'warning': '⚠️',
                'error': '❌'
            }
            
            color = severity_colors.get(notif['severity'], '#666')
            icon = severity_icons.get(notif['severity'], 'ℹ️')
            
            st.markdown(f"""
            <div style="border-left: 4px solid {color}; padding: 10px; margin: 5px 0; 
                        background: rgba(59, 130, 246, 0.05); border-radius: 5px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span><strong>{icon} {notif['message']}</strong></span>
                    <span style="font-size: 0.8em; color: #666;">
                        {notif['timestamp'].strftime('%H:%M')}
                    </span>
                </div>
                <div style="font-size: 0.8em; color: #666; margin-top: 2px;">
                    {notif['type'].replace('_', ' ').title()}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Clear notifications button
        if st.button("🗑️ Clear All Notifications", key="clear_notifications"):
            st.info("All notifications cleared")

class SystemMonitoringPanel:
    """System health and performance monitoring"""
    
    def __init__(self):
        pass
    
    def render(self):
        """Render system monitoring panel"""
        st.markdown("### 🖥️ SYSTEM MONITORING")
        
        col1, col2 = st.columns(2)
        
        with col1:
            self._render_system_health()
        
        with col2:
            self._render_performance_metrics()
        
        st.markdown("---")
        self._render_connection_status()
    
    def _render_system_health(self):
        """Render system health indicators"""
        st.markdown("#### 💓 System Health")
        
        # Mock system metrics
        system_metrics = {
            'CPU Usage': {'value': 15.2, 'unit': '%', 'threshold': 80, 'status': 'good'},
            'Memory Usage': {'value': 245, 'unit': 'MB', 'threshold': 1000, 'status': 'good'},
            'API Calls/Min': {'value': 12, 'unit': 'calls', 'threshold': 100, 'status': 'good'},
            'Uptime': {'value': '2d 14h', 'unit': '', 'threshold': None, 'status': 'good'}
        }
        
        for metric, data in system_metrics.items():
            status_color = "#10b981" if data['status'] == 'good' else "#f59e0b" if data['status'] == 'warning' else "#ef4444"
            status_icon = "✅" if data['status'] == 'good' else "⚠️" if data['status'] == 'warning' else "❌"
            
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; padding: 8px; 
                        border-bottom: 1px solid #e2e8f0;">
                <span><strong>{metric}:</strong></span>
                <span style="color: {status_color};">
                    {status_icon} {data['value']} {data['unit']}
                </span>
            </div>
            """, unsafe_allow_html=True)
        
        # System status indicator
        st.markdown("""
        <div style="text-align: center; padding: 15px; background: #10b981; 
                    color: white; border-radius: 8px; font-weight: bold; margin-top: 10px;">
            🟢 SYSTEM STATUS: HEALTHY
        </div>
        """, unsafe_allow_html=True)
    
    def _render_performance_metrics(self):
        """Render performance metrics"""
        st.markdown("#### ⚡ Performance Metrics")
        
        # Mock performance data
        performance_data = {
            'Signal Generation': {'avg_time': 1.2, 'unit': 'seconds', 'status': 'good'},
            'Data Processing': {'avg_time': 0.8, 'unit': 'seconds', 'status': 'good'},
            'Order Execution': {'avg_time': 2.1, 'unit': 'seconds', 'status': 'good'},
            'Dashboard Refresh': {'avg_time': 0.5, 'unit': 'seconds', 'status': 'good'}
        }
        
        for process, data in performance_data.items():
            status_color = "#10b981" if data['status'] == 'good' else "#f59e0b"
            
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; padding: 5px; 
                        border-bottom: 1px solid #f1f5f9;">
                <span>{process}:</span>
                <span style="color: {status_color}; font-weight: bold;">
                    {data['avg_time']} {data['unit']}
                </span>
            </div>
            """, unsafe_allow_html=True)
        
        # Performance chart
        self._render_performance_chart()
    
    def _render_performance_chart(self):
        """Render system performance chart"""
        # Generate mock performance data
        times = pd.date_range(start=datetime.now() - timedelta(hours=1), end=datetime.now(), freq='5T')
        cpu_usage = np.random.normal(15, 3, len(times))
        memory_usage = np.random.normal(245, 20, len(times))
        
        fig = go.Figure()
        
        # CPU usage
        fig.add_trace(go.Scatter(
            x=times,
            y=cpu_usage,
            mode='lines',
            name='CPU Usage (%)',
            line=dict(color='#3b82f6', width=2)
        ))
        
        # Memory usage (scaled for visualization)
        fig.add_trace(go.Scatter(
            x=times,
            y=memory_usage / 10,  # Scale down for chart
            mode='lines',
            name='Memory Usage (MB/10)',
            line=dict(color='#10b981', width=2)
        ))
        
        fig.update_layout(
            title="System Performance (Last Hour)",
            xaxis_title="Time",
            yaxis_title="Usage",
            height=200,
            showlegend=True,
            template="plotly_white"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_connection_status(self):
        """Render API and connection status"""
        st.markdown("#### 🌐 Connection Status")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**Bybit API**")
            st.success("🟢 Connected")
            st.markdown("Latency: 45ms")
            st.markdown("Last Update: 2s ago")
        
        with col2:
            st.markdown("**Market Data**")
            st.success("🟢 Streaming")
            st.markdown("Updates: 30s interval")
            st.markdown("Data Quality: 100%")
        
        with col3:
            st.markdown("**Trading Bot**")
            if st.session_state.get('trading_active', False):
                st.success("🟢 Active")
                st.markdown("Status: Running")
            else:
                st.warning("🟡 Paused")
                st.markdown("Status: Standby")
            
            st.markdown("Last Signal: 3m ago")

class AdvancedTradingControls:
    """Main advanced trading controls interface"""
    
    def __init__(self, api_client):
        self.api = api_client
        self.control_panel = TradingControlPanel(api_client)
        self.strategy_panel = StrategyControlPanel()
        self.notification_center = NotificationCenter()
        self.system_monitor = SystemMonitoringPanel()
    
    def render_full_interface(self):
        """Render complete advanced trading controls interface"""
        # Main trading controls
        self.control_panel.render()
        
        st.markdown("---")
        
        # Strategy controls
        self.strategy_panel.render()
        
        st.markdown("---")
        
        # Create tabs for additional features
        tab1, tab2, tab3 = st.tabs(["🔔 Notifications", "🖥️ System Monitor", "📊 Advanced Analytics"])
        
        with tab1:
            self.notification_center.render()
        
        with tab2:
            self.system_monitor.render()
        
        with tab3:
            self._render_advanced_analytics()
    
    def _render_advanced_analytics(self):
        """Render advanced analytics section"""
        st.markdown("### 📊 ADVANCED ANALYTICS")
        
        col1, col2 = st.columns(2)
        
        with col1:
            self._render_signal_quality_analysis()
        
        with col2:
            self._render_market_conditions_analysis()
        
        st.markdown("---")
        self._render_optimization_suggestions()
    
    def _render_signal_quality_analysis(self):
        """Render signal quality analysis"""
        st.markdown("#### 🎯 Signal Quality Analysis")
        
        # Mock signal quality data
        signal_data = {
            'High Quality (4-5 filters)': 15,
            'Medium Quality (2-3 filters)': 28,
            'Low Quality (1 filter)': 7
        }
        
        # Create pie chart
        fig = go.Figure(data=[go.Pie(
            labels=list(signal_data.keys()),
            values=list(signal_data.values()),
            hole=0.4,
            marker_colors=['#10b981', '#f59e0b', '#ef4444']
        )])
        
        fig.update_layout(
            title="Signal Quality Distribution (Last 30 Days)",
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Signal quality metrics
        total_signals = sum(signal_data.values())
        high_quality_pct = (signal_data['High Quality (4-5 filters)'] / total_signals) * 100
        
        st.metric("High Quality Signals", f"{high_quality_pct:.1f}%", "Target: >60%")
    
    def _render_market_conditions_analysis(self):
        """Render market conditions analysis"""
        st.markdown("#### 📈 Market Conditions Analysis")
        
        # Mock market condition data
        conditions = {
            'Trending Markets': 65,
            'Ranging Markets': 25,
            'High Volatility': 10
        }
        
        # Bar chart
        fig = go.Figure(data=[
            go.Bar(
                x=list(conditions.keys()),
                y=list(conditions.values()),
                marker_color=['#3b82f6', '#f59e0b', '#ef4444']
            )
        ])
        
        fig.update_layout(
            title="Market Conditions (Last 30 Days, %)",
            yaxis_title="Percentage of Time",
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Current market assessment
        st.markdown("**Current Market Assessment:**")
        st.success("🟢 Trending market with good momentum")
        st.info("📊 Optimal conditions for Enhanced Smart Money Strategy")
    
    def _render_optimization_suggestions(self):
        """Render optimization suggestions"""
        st.markdown("#### 💡 OPTIMIZATION SUGGESTIONS")
        
        suggestions = [
            {
                'category': 'Risk Management',
                'suggestion': 'Consider reducing position size during high volatility periods',
                'impact': 'Medium',
                'effort': 'Low'
            },
            {
                'category': 'Signal Quality',
                'suggestion': 'Enable Order Flow filter for better signal precision',
                'impact': 'High',
                'effort': 'Low'
            },
            {
                'category': 'Performance',
                'suggestion': 'Implement dynamic stop-loss based on ATR',
                'impact': 'High',
                'effort': 'Medium'
            },
            {
                'category': 'Market Timing',
                'suggestion': 'Focus trading during London/NY session overlap',
                'impact': 'Medium',
                'effort': 'Low'
            }
        ]
        
        for i, sugg in enumerate(suggestions):
            # Color coding for impact/effort
            impact_colors = {'Low': '#10b981', 'Medium': '#f59e0b', 'High': '#ef4444'}
            effort_colors = {'Low': '#10b981', 'Medium': '#f59e0b', 'High': '#ef4444'}
            
            st.markdown(f"""
            <div style="border: 1px solid #e2e8f0; border-radius: 8px; padding: 15px; margin: 10px 0;">
                <h5 style="margin: 0 0 5px 0; color: #1f2937;">{sugg['category']}</h5>
                <p style="margin: 5px 0;">{sugg['suggestion']}</p>
                <div style="display: flex; gap: 10px; margin-top: 10px;">
                    <span style="background: {impact_colors[sugg['impact']]}; color: white; 
                                 padding: 2px 8px; border-radius: 4px; font-size: 0.8em;">
                        Impact: {sugg['impact']}
                    </span>
                    <span style="background: {effort_colors[sugg['effort']]}; color: white; 
                                 padding: 2px 8px; border-radius: 4px; font-size: 0.8em;">
                        Effort: {sugg['effort']}
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Implementation button
            if st.button(f"🚀 Implement Suggestion {i+1}", key=f"implement_{i}"):
                st.success(f"✅ Optimization suggestion {i+1} queued for implementation")

# Quick access functions for integration
def render_trading_controls(api_client):
    """Quick access function to render trading controls"""
    controls = AdvancedTradingControls(api_client)
    controls.render_full_interface()

def render_basic_controls(api_client):
    """Quick access function to render basic controls only"""
    controls = TradingControlPanel(api_client)
    controls.render()

def render_strategy_controls():
    """Quick access function to render strategy controls only"""
    strategy_controls = StrategyControlPanel()
    strategy_controls.render()
