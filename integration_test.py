#!/usr/bin/env python3
"""
ENHANCED SMART MONEY DASHBOARD - INTEGRATION SCRIPT
"""

import streamlit as st
import pandas as pd
import numpy as np
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our modules
from core.api_client import BybitAPI
from strategies.enhanced_smart_money import EnhancedSmartMoneyStrategy

# Load environment variables
load_dotenv()

# Initialize API client
@st.cache_resource
def get_api_client():
    return BybitAPI(
        api_key=os.getenv('BYBIT_API_KEY'),
        api_secret=os.getenv('BYBIT_API_SECRET')
    )

# Initialize trading strategy
@st.cache_resource
def get_strategy():
    config = {
        'SYMBOL': 'BTCUSDT',
        'TIMEFRAME': '5',
        'RISK_PERCENTAGE': 2.0,
        'MAX_DRAWDOWN': 15.0,
        'POSITION_SIZE': 0.01,
        'LIQUIDITY_FACTOR': 1.0,
        'MIN_LIQUIDITY_THRESHOLD': 1000,
        'VOLUME_THRESHOLD': 100000,
        'USE_VOLUME_FILTER': True,
        'USE_KEY_LEVELS': True,
        'USE_PATTERN_RECOGNITION': True,
        'USE_ORDER_FLOW': False,
        'USE_LIQUIDITY_SWEEP': False,
        'TREND_LOOKBACK': 50,
        'VOLATILITY_LOOKBACK': 20,
        'SIDEWAYS_THRESHOLD': 0.02,
        'MARKET_MULTIPLIERS': {
            'bull': {
                'volume_threshold_multiplier': 0.8,
                'risk_reward_multiplier': 1.2,
                'liquidity_factor_multiplier': 1.1
            },
            'bear': {
                'volume_threshold_multiplier': 1.2,
                'risk_reward_multiplier': 0.9,
                'liquidity_factor_multiplier': 1.3
            },
            'sideways': {
                'volume_threshold_multiplier': 1.5,
                'risk_reward_multiplier': 1.0,
                'liquidity_factor_multiplier': 1.0
            }
        }
    }
    return EnhancedSmartMoneyStrategy(config)

# Analyze market with Enhanced Smart Money Strategy
def analyze_market_with_strategy(api_client, strategy, symbol='BTCUSDT', interval='5'):
    # Get market data
    kline_result = api_client.get_kline_data(symbol, interval, 100)
    
    if not kline_result['success']:
        return {
            'success': False,
            'error': kline_result.get('error', 'No market data available')
        }
    
    # Convert to DataFrame
    df = kline_result['data']
    
    if df.empty:
        return {
            'success': False,
            'error': 'Empty data received'
        }
    
    # Run technical analysis
    df_with_indicators = strategy.calculate_indicators(df)
    
    # Generate trading signal
    signal, entry_price, stop_loss, metadata = strategy.generate_signal(df_with_indicators)
    
    # Get market regime information
    latest_candle = df_with_indicators.iloc[-1]
    market_regime = latest_candle.get('market_regime', 'unknown')
    regime_confidence = latest_candle.get('regime_confidence', 0.0)
    
    # Extract filter status
    if signal == 'BUY':
        filter_results = metadata.get('buy_filters_passed', {})
    elif signal == 'SELL':
        filter_results = metadata.get('sell_filters_passed', {})
    else:
        filter_results = {}
    
    return {
        'success': True,
        'signal': signal,
        'entry_price': entry_price,
        'stop_loss': stop_loss,
        'market_regime': market_regime,
        'regime_confidence': regime_confidence,
        'filter_results': filter_results,
        'metadata': metadata,
        'df': df_with_indicators,
        'current_price': latest_candle['close'],
        'regime_adjusted_params': {
            'volume_threshold': latest_candle.get('adjusted_volume_threshold', None),
            'risk_reward': latest_candle.get('adjusted_risk_reward_ratio', None)
        }
    }

# Main function to test the integration
def main():
    st.title("Enhanced Smart Money Strategy Integration Test")
    
    # Initialize API client and strategy
    api_client = get_api_client()
    strategy = get_strategy()
    
    st.write("Testing API connection...")
    dashboard_data = api_client.get_dashboard_data()
    
    if dashboard_data['success']:
        st.success("API connection successful!")
        st.write(f"BTC Price: ${dashboard_data.get('btc_price', 0):,.2f}")
        st.write(f"Account Type: {dashboard_data.get('account_type', 'Unknown')}")
        
        # Display balances
        balances = dashboard_data.get('balances', {})
        st.write("**Available Balances:**")
        for coin, amount in balances.items():
            if coin == 'USDT':
                st.write(f"{coin}: {amount:.2f}")
            else:
                st.write(f"{coin}: {amount:.8f}")
    else:
        st.error("API connection failed!")
        st.write(f"Error: {dashboard_data.get('error', 'Unknown error')}")
        return
    
    st.write("---")
    st.write("Testing Enhanced Smart Money Strategy...")
    
    market_analysis = analyze_market_with_strategy(api_client, strategy)
    
    if market_analysis['success']:
        st.success("Strategy analysis successful!")
        
        # Display market regime
        regime = market_analysis.get('market_regime', 'unknown')
        confidence = market_analysis.get('regime_confidence', 0.0)
        
        st.write(f"**Market Regime:** {regime.upper()}")
        st.write(f"**Confidence:** {confidence:.2f}")
        
        # Display signal
        signal = market_analysis.get('signal', 'HOLD')
        entry_price = market_analysis.get('entry_price', 0.0)
        stop_loss = market_analysis.get('stop_loss', 0.0)
        
        st.write(f"**Signal:** {signal}")
        
        if signal in ['BUY', 'SELL']:
            st.write(f"**Entry Price:** ${entry_price:.2f}")
            st.write(f"**Stop Loss:** ${stop_loss:.2f}")
            
            # Display filter results
            filter_results = market_analysis.get('filter_results', {})
            st.write("**Filter Results:**")
            for filter_name, passed in filter_results.items():
                status = "✅ PASSED" if passed else "❌ FAILED"
                st.write(f"{filter_name}: {status}")
    else:
        st.error("Strategy analysis failed!")
        st.write(f"Error: {market_analysis.get('error', 'Unknown error')}")
    
    st.write("---")
    st.write("Integration test complete!")

if __name__ == "__main__":
    main()
