#!/usr/bin/env python3
"""
💰 EINFACHES BOT DASHBOARD - OHNE SIDEBAR
Direkte Bot-Steuerung und Überwachung ohne Komplexität
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import os
import sys
import subprocess
from live_bybit_api import LiveBybitAPI

# Füge Root-Verzeichnis zum Pfad hinzu für Modul-Importe
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ============================================================================
# STREAMLIT CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="💰 LIVE MAINNET Trading Bot",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"  # Sidebar minimiert
)

# ============================================================================
# STYLING
# ============================================================================

st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #3498db, #2980b9);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 1rem;
        border: 2px solid #fff;
    }
    
    .control-panel {
        background: linear-gradient(135deg, #2c3e50, #34495e);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .bot-status-running {
        background: linear-gradient(90deg, #2ecc71, #27ae60);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        margin: 1rem 0;
    }
    
    .bot-status-stopped {
        background: linear-gradient(90deg, #e74c3c, #c0392b);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        margin: 1rem 0;
    }
    
    .footer {
        text-align: center;
        margin-top: 2rem;
        padding: 1rem;
        font-size: 0.8rem;
        color: #7f8c8d;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.bot_running = False
    st.session_state.bot_pid = None
    st.session_state.bot_script = None
    st.session_state.auto_refresh = True
    st.session_state.refresh_interval = 15  # seconds

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_live_data():
    """Get live data from Bybit API"""
    api = LiveBybitAPI()
    result = api.get_dashboard_data()
    
    # Check bot status
    bot_status = api.check_bot_status()
    st.session_state.bot_running = bot_status.get('running', False)
    st.session_state.bot_pid = bot_status.get('process_id')
    
    if result['success']:
        return {
            'portfolio_value': result['portfolio_value'],
            'balances': result['balances'],
            'btc_price': result['btc_price'],
            'btc_change_24h': result['btc_change_24h'],
            'btc_high_24h': result['btc_high_24h'],
            'btc_low_24h': result['btc_low_24h'],
            'account_type': result['account_type'],
            'api_connected': True,
            'last_update': datetime.now(),
            'bot_status': bot_status
        }
    else:
        return {
            'api_connected': False,
            'error': result.get('error', 'API Connection failed')
        }

def start_trading_bot():
    """Start trading bot"""
    try:
        # Suche nach Bot-Skripten
        bot_scripts = [
            'enhanced_live_bot.py',
            'live_trading_bot.py'
        ]
        
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        bot_script_path = None
        
        for script in bot_scripts:
            script_path = os.path.join(base_dir, script)
            if os.path.exists(script_path):
                bot_script_path = script_path
                break
        
        if bot_script_path:
            # Python-Interpreter-Pfad ermitteln
            python_exe = sys.executable
            
            # Bot starten
            process = subprocess.Popen(
                [python_exe, bot_script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=base_dir
            )
            
            st.session_state.bot_running = True
            st.session_state.bot_pid = process.pid
            st.session_state.bot_script = os.path.basename(bot_script_path)
            
            return {
                'success': True,
                'message': f"Bot gestartet! (PID: {process.pid})",
                'pid': process.pid,
                'script': os.path.basename(bot_script_path)
            }
        else:
            return {
                'success': False,
                'message': "Bot-Script nicht gefunden."
            }
    except Exception as e:
        return {
            'success': False,
            'message': f"Fehler beim Starten des Bots: {str(e)}"
        }

def stop_trading_bot():
    """Stop trading bot"""
    api = LiveBybitAPI()
    result = api.emergency_stop_bot()
    
    if result.get('success', False):
        st.session_state.bot_running = False
        st.session_state.bot_pid = None
    
    return result

# ============================================================================
# MAIN DASHBOARD
# ============================================================================

def main():
    """Main dashboard function"""
    # Get live data
    data = get_live_data()
    
    # Dashboard header
    st.markdown("""
    <div class="main-header">
        <h1>💰 CRYPTO TRADING BOT DASHBOARD</h1>
        <p style="font-size: 1.2rem;">Enhanced Smart Money Strategy • Live Trading • Bybit</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Main dashboard content
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        # Bot status display
        if st.session_state.bot_running:
            st.markdown(f"""
            <div class="bot-status-running">
                ✅ BOT LÄUFT AKTIV! (PID: {st.session_state.bot_pid})
                <br>Script: {st.session_state.bot_script}
                <br>Uptime: {st.session_state.get('bot_status', {}).get('uptime', 'unbekannt')}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="bot-status-stopped">
                ⏸️ BOT IST GESTOPPT - KLICKE AUF START
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        # Start bot button
        if not st.session_state.bot_running:
            if st.button("🚀 START BOT", key="start_bot", type="primary", use_container_width=True):
                with st.spinner("Bot wird gestartet..."):
                    result = start_trading_bot()
                    if result.get('success', False):
                        st.success(f"✅ {result.get('message', 'Bot gestartet!')}")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"❌ {result.get('message', 'Fehler beim Starten!')}")
    
    with col3:
        # Stop bot button
        if st.session_state.bot_running:
            if st.button("🛑 STOP BOT", key="stop_bot", type="primary", use_container_width=True):
                result = stop_trading_bot()
                if result.get('success', False):
                    st.success(f"✅ {result.get('message', 'Bot gestoppt!')}")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(f"❌ {result.get('message', 'Fehler beim Stoppen!')}")
    
    # Market overview
    st.markdown("## 📊 MARKET OVERVIEW")
    
    if data.get('api_connected', False):
        market_col1, market_col2, market_col3, market_col4 = st.columns(4)
        
        with market_col1:
            btc_price = data.get('btc_price', 0)
            btc_change = data.get('btc_change_24h', 0)
            delta_color = "normal" if btc_change >= 0 else "inverse"
            st.metric(
                label="💎 BTC Price",
                value=f"${btc_price:,.2f}",
                delta=f"{btc_change:+.2f}%",
                delta_color=delta_color
            )
        
        with market_col2:
            portfolio_value = data.get('portfolio_value', 0)
            st.metric(
                label="💰 Portfolio Value",
                value=f"${portfolio_value:.2f}",
                delta=f"LIVE {data.get('account_type', 'UNKNOWN')}"
            )
        
        with market_col3:
            usdt_balance = data.get('balances', {}).get('USDT', 0)
            st.metric(
                label="💵 USDT Balance",
                value=f"${usdt_balance:.2f}"
            )
        
        with market_col4:
            bot_market_regime = st.session_state.get('bot_status', {}).get('market_regime', 'UNKNOWN')
            st.metric(
                label="🧠 Market Regime",
                value=bot_market_regime if bot_market_regime else "N/A"
            )
    else:
        st.error("❌ API Connection Failed!")
        st.error(f"Error: {data.get('error', 'Unable to connect to Bybit API')}")
    
    # Bot Controls and Settings
    st.markdown("## ⚙️ BOT CONTROLS")
    
    control_col1, control_col2 = st.columns(2)
    
    with control_col1:
        # Refresh controls
        auto_refresh = st.checkbox("Auto-Refresh Dashboard", value=st.session_state.auto_refresh)
        st.session_state.auto_refresh = auto_refresh
        
        if auto_refresh:
            refresh_interval = st.slider("Refresh-Intervall (Sekunden)", 5, 60, st.session_state.refresh_interval)
            st.session_state.refresh_interval = refresh_interval
    
    with control_col2:
        # Manual refresh button
        if st.button("🔄 Manueller Refresh", type="secondary", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        
        # Bot Status
        if st.session_state.bot_running:
            status_text = "Bot Status: ✅ AKTIV"
        else:
            status_text = "Bot Status: ⏸️ GESTOPPT"
        
        st.info(status_text)
    
    # Last update timestamp
    st.caption(f"Letztes Update: {datetime.now().strftime('%H:%M:%S')}")
    
    # Auto refresh logic
    if st.session_state.auto_refresh:
        time.sleep(st.session_state.refresh_interval)
        st.rerun()
    
    # Footer
    st.markdown("""
    <div class="footer">
        Enhanced Smart Money Trading Bot • Bybit Mainnet • Version 2.0
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
