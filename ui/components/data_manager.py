#!/usr/bin/env python3
"""
🚀 Data Manager Component
Centralized data management for dashboard session state and API calls
"""

import streamlit as st
from datetime import datetime
import sys
import os

# Add root directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.api_client import BybitAPIClient
from ui.advanced_chart import SmartMoneyChart


class DashboardDataManager:
    """Centralized data management for the trading dashboard"""
    
    def __init__(self):
        self.api_client = None
        self.initialize_session_state()
    
    def initialize_session_state(self):
        """Initialize all session state variables"""
        # Initialize all session state variables - always check if exists first
        if 'initialized' not in st.session_state:
            st.session_state.initialized = True
        
        if 'live_data' not in st.session_state:
            st.session_state.live_data = {'success': False}
        
        if 'account_balance' not in st.session_state:
            st.session_state.account_balance = {'success': False}
        
        if 'order_book' not in st.session_state:
            st.session_state.order_book = {'success': False}
        
        if 'chart_data' not in st.session_state:
            st.session_state.chart_data = {'success': False}
        
        if 'last_update' not in st.session_state:
            st.session_state.last_update = None
        
        if 'refresh_interval' not in st.session_state:
            st.session_state.refresh_interval = 30
        
        if 'auto_refresh' not in st.session_state:
            st.session_state.auto_refresh = True
        
        if 'trading_enabled' not in st.session_state:
            st.session_state.trading_enabled = False
        
        if 'emergency_stop' not in st.session_state:
            st.session_state.emergency_stop = False
        
        if 'dark_mode' not in st.session_state:
            st.session_state.dark_mode = True
        
        if 'trading_active' not in st.session_state:
            st.session_state.trading_active = False
    
    def get_api_client(self):
        """Get or create API client"""
        if self.api_client is None:
            # Import the working LiveBybitAPI
            try:
                sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'monitoring'))
                from live_bybit_api import LiveBybitAPI
                self.api_client = LiveBybitAPI()
            except ImportError:
                # Fallback to standard API client
                self.api_client = BybitAPIClient()
        
        return self.api_client
    
    def refresh_all_data(self):
        """Refresh all dashboard data"""
        try:
            api_client = self.get_api_client()
            
            # Check if using LiveBybitAPI
            if hasattr(api_client, 'get_dashboard_data'):
                dashboard_data = api_client.get_dashboard_data()
                
                if dashboard_data['success']:
                    self._update_live_data(dashboard_data)
                    self._update_account_balance(dashboard_data)
                    self._update_order_book(dashboard_data)
                    self._update_chart_data(api_client)
                    st.session_state.last_update = datetime.now().strftime("%H:%M:%S")
                    return True
                else:
                    self._set_error_states(dashboard_data.get('error', 'API Error'))
                    return False
            else:
                # Fallback for standard API client
                return self._refresh_with_standard_api(api_client)
                
        except Exception as e:
            error_msg = f"Data refresh error: {str(e)}"
            self._set_error_states(error_msg)
            return False
    
    def _update_live_data(self, dashboard_data):
        """Update live market data in session state"""
        st.session_state.live_data = {
            'success': True,
            'price': dashboard_data['btc_price'],
            'change_24h': dashboard_data['btc_change_24h'],
            'high_24h': dashboard_data.get('btc_high_24h', 0),
            'low_24h': dashboard_data.get('btc_low_24h', 0),
            'volume_24h': dashboard_data.get('btc_volume_24h', 0),
            'bid': dashboard_data.get('bid', 0),
            'ask': dashboard_data.get('ask', 0),
            'timestamp': datetime.now()
        }
    
    def _update_account_balance(self, dashboard_data):
        """Update account balance in session state"""
        st.session_state.account_balance = {
            'success': True,
            'portfolio_value': dashboard_data['portfolio_value'],
            'balances': dashboard_data['balances'],
            'account_type': dashboard_data.get('account_type', 'UMA')
        }
    
    def _update_order_book(self, dashboard_data):
        """Update order book in session state"""
        st.session_state.order_book = {
            'success': True,
            'bids': dashboard_data.get('order_book_bids', []),
            'asks': dashboard_data.get('order_book_asks', []),
            'timestamp': datetime.now()
        }
    
    def _update_chart_data(self, api_client):
        """Update chart data in session state"""
        try:
            chart_instance = SmartMoneyChart(api_client=api_client, symbol="BTCUSDT", timeframe="5")
            if chart_instance.load_data():
                st.session_state.chart_data = {
                    'success': True,
                    'data': chart_instance.data
                }
            else:
                st.session_state.chart_data = {
                    'success': False, 
                    'error': 'Failed to load chart data'
                }
        except Exception as e:
            st.session_state.chart_data = {
                'success': False, 
                'error': f'Chart data error: {str(e)}'
            }
    
    def _refresh_with_standard_api(self, api_client):
        """Fallback refresh with standard API client"""
        # Implement basic data refresh with standard API
        # This is a simplified version for fallback
        st.session_state.live_data = {'success': False, 'error': 'Using fallback API'}
        st.session_state.account_balance = {'success': False, 'error': 'Using fallback API'}
        st.session_state.order_book = {'success': False, 'error': 'Using fallback API'}
        st.session_state.chart_data = {'success': False, 'error': 'Using fallback API'}
        return False
    
    def _set_error_states(self, error_msg):
        """Set error states for all data"""
        st.session_state.live_data = {'success': False, 'error': error_msg}
        st.session_state.account_balance = {'success': False, 'error': error_msg}
        st.session_state.order_book = {'success': False, 'error': error_msg}
        st.session_state.chart_data = {'success': False, 'error': error_msg}
    
    def get_live_account_data(self):
        """Get live account data (cached)"""
        if st.session_state.account_balance.get('success'):
            return {
                'success': True,
                'portfolio_value': st.session_state.account_balance['portfolio_value'],
                'balances': st.session_state.account_balance['balances'],
                'account_type': st.session_state.account_balance.get('account_type', 'UMA'),
                'is_real': True
            }
        else:
            return {
                'success': False,
                'error': st.session_state.account_balance.get('error', 'No account data')
            }
    
    def calculate_50eur_metrics(self):
        """Calculate metrics optimized for 50€ start capital"""
        portfolio_value = 50.0  # Default to planned amount
        
        if st.session_state.account_balance.get('success'):
            portfolio_value = st.session_state.account_balance['portfolio_value']
        
        return {
            'start_amount': 50.0,
            'current_value': portfolio_value,
            'pnl': portfolio_value - 50.0,
            'pnl_percentage': ((portfolio_value - 50.0) / 50.0) * 100,
            'risk_per_trade': portfolio_value * 0.02,  # 2%
            'daily_risk_limit': portfolio_value * 0.05,  # 5%
            'emergency_stop_level': portfolio_value * 0.15,  # 15%
            'position_size_range': {
                'min': portfolio_value * 0.05,  # 5%
                'max': portfolio_value * 0.20   # 20%
            }
        }
    
    def get_trading_status(self):
        """Get current trading status"""
        return {
            'trading_active': st.session_state.get('trading_active', False),
            'emergency_stop': st.session_state.get('emergency_stop', False),
            'auto_refresh': st.session_state.get('auto_refresh', True),
            'last_update': st.session_state.get('last_update', 'Never')
        }
    
    def update_trading_status(self, **kwargs):
        """Update trading status"""
        for key, value in kwargs.items():
            if key in ['trading_active', 'emergency_stop', 'auto_refresh']:
                st.session_state[key] = value
    
    def is_data_valid(self):
        """Check if dashboard data is valid"""
        return (
            st.session_state.live_data.get('success', False) and
            st.session_state.account_balance.get('success', False)
        )
    
    def get_error_summary(self):
        """Get summary of any data errors"""
        errors = []
        
        if not st.session_state.live_data.get('success'):
            errors.append(f"Market Data: {st.session_state.live_data.get('error', 'Unknown error')}")
        
        if not st.session_state.account_balance.get('success'):
            errors.append(f"Account Data: {st.session_state.account_balance.get('error', 'Unknown error')}")
        
        if not st.session_state.order_book.get('success'):
            errors.append(f"Order Book: {st.session_state.order_book.get('error', 'Unknown error')}")
        
        if not st.session_state.chart_data.get('success'):
            errors.append(f"Chart Data: {st.session_state.chart_data.get('error', 'Unknown error')}")
        
        return errors


# Global instance for easy access
@st.cache_resource
def get_data_manager():
    """Get singleton data manager instance"""
    return DashboardDataManager()


# Convenience functions for direct use in dashboard
def refresh_dashboard_data():
    """Convenience function to refresh all dashboard data"""
    data_manager = get_data_manager()
    return data_manager.refresh_all_data()


def get_50eur_metrics():
    """Get 50€ optimized trading metrics"""
    data_manager = get_data_manager()
    return data_manager.calculate_50eur_metrics()


def get_dashboard_status():
    """Get complete dashboard status"""
    data_manager = get_data_manager()
    
    return {
        'data_valid': data_manager.is_data_valid(),
        'trading_status': data_manager.get_trading_status(),
        'errors': data_manager.get_error_summary(),
        'last_update': st.session_state.get('last_update', 'Never'),
        'api_connected': st.session_state.live_data.get('success', False)
    }
