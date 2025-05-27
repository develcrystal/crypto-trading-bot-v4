#!/usr/bin/env python3
"""
💰 LIVE MAINNET DASHBOARD - MIT ECHTEN $83.38 USDT BALANCE!
KEINE SIMULATION - NUR ECHTE BYBIT MAINNET DATEN!
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
import numpy as np
import re
import os
from live_bybit_api import LiveBybitAPI

# ============================================================================
# STREAMLIT CONFIGURATION - MAINNET MODE
# ============================================================================

st.set_page_config(
    page_title="💰 LIVE MAINNET Trading Bot",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# LIVE MAINNET CSS STYLES
# ============================================================================

st.markdown("""
<style>
    .mainnet-header {
        background: linear-gradient(90deg, #e74c3c, #c0392b);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        border: 3px solid #fff;
        box-shadow: 0 4px 15px rgba(231, 76, 60, 0.3);
        animation: pulse-red 3s infinite;
    }
    
    @keyframes pulse-red {
        0% { box-shadow: 0 4px 15px rgba(231, 76, 60, 0.3); }
        50% { box-shadow: 0 4px 25px rgba(231, 76, 60, 0.6); }
        100% { box-shadow: 0 4px 15px rgba(231, 76, 60, 0.3); }
    }
    
    .live-balance {
        background: linear-gradient(135deg, #2ecc71, #27ae60);
        color: white;
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        font-size: 1.5rem;
        font-weight: bold;
        margin: 1rem 0;
        border: 2px solid #fff;
        box-shadow: 0 6px 20px rgba(46, 204, 113, 0.4);
    }
    
    .api-status {
        background: linear-gradient(90deg, #2ecc71, #27ae60);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 10px;
        display: inline-block;
        font-weight: bold;
        margin: 0.5rem;
        animation: pulse-green 2s infinite;
    }
    
    @keyframes pulse-green {
        0% { opacity: 1; }
        50% { opacity: 0.8; }
        100% { opacity: 1; }
    }
    
    .real-price {
        background: linear-gradient(90deg, #3498db, #2980b9);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-size: 1.2rem;
        margin: 0.5rem 0;
    }
    
    .no-simulation {
        background: linear-gradient(90deg, #f39c12, #e67e22);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        margin: 1rem 0;
    }
    
    .trading-activity {
        background: linear-gradient(135deg, #2c3e50, #1a252f);
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .trading-signal {
        display: flex;
        align-items: center;
        padding: 0.75rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        background: rgba(32, 33, 36, 0.7);
    }
    
    .buy-signal {
        border-left: 4px solid #2ecc71;
    }
    
    .sell-signal {
        border-left: 4px solid #e74c3c;
    }
    
    .signal-time {
        font-size: 0.85rem;
        color: rgba(255, 255, 255, 0.7);
    }
    
    .signal-price {
        font-size: 1.1rem;
        font-weight: bold;
    }
    
    .buy-text {
        color: #2ecc71;
        font-weight: bold;
    }
    
    .sell-text {
        color: #e74c3c;
        font-weight: bold;
    }
    
    /* Style für Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: rgba(32, 33, 36, 0.7);
        border-radius: 4px 4px 0 0;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: rgba(52, 152, 219, 0.3);
        border-bottom: 2px solid #3498db;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# LIVE DATA HANDLER - MAINNET ONLY
# ============================================================================

@st.cache_data(ttl=60)  # Refresh every 60 seconds
def get_live_mainnet_balance():
    """Holt ECHTE Mainnet Balance - KEINE SIMULATION!"""
    api = LiveBybitAPI()
    result = api.get_dashboard_data()
    
    if result['success']:
        # Explizit kline_data abrufen, wenn nicht im Dashboard-Daten enthalten
        if 'kline_data' not in result or result.get('kline_data') is None or result.get('kline_data', pd.DataFrame()).empty:
            kline_result = api.get_kline_data(symbol='BTCUSDT', interval='5', limit=100)
            if kline_result['success'] and 'data' in kline_result:
                result['kline_data'] = kline_result['data']
        
        # Trades aus Log-Dateien lesen für Chart-Anzeige
        trades = []
        signals = []
        
        # Bot Status prüfen (für Market Regime und Signale)
        bot_status = result.get('bot_status', {})
        
        # Signal aus Bot Status extrahieren
        last_signal = bot_status.get('last_signal')
        if last_signal:
            # Füge Signal dem signals-Array hinzu (für Chart-Anzeige)
            signal_price = result.get('btc_price', 0)
            signals.append({
                'timestamp': datetime.now(),
                'price': signal_price,
                'type': last_signal  # 'BUY' oder 'SELL'
            })
        
        # Trades aus Logfiles extrahieren
        try:
            # Suche nach Logdateien im Hauptverzeichnis
            log_paths = [
                'live_trading_bot.log', 
                'live_trading.log',
                'enhanced_live_bot.log',
                'live_trading_mainnet_50eur.log'
            ]
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
            for log_path in log_paths:
                full_path = os.path.join(base_dir, log_path)
                if os.path.exists(full_path):
                    try:
                        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                            # Die letzten 500 Zeilen lesen
                            lines = f.readlines()[-500:]
                            
                            # Temporäre Variablen für Trades
                            temp_trades = {}
                            
                            # Nach Trades in den Logs suchen
                            for i, line in enumerate(lines):
                                # Signale im Log erkennen (verschiedene Formate abdecken)
                                if any(pattern in line for pattern in ["SIGNAL: BUY", "SIGNAL: SELL", "BUY SIGNAL", "SELL SIGNAL"]):
                                    # Zeitstempel und Preis extrahieren
                                    try:
                                        # Zeitstempel extrahieren (verschiedene Formate)
                                        timestamp_str = ""
                                        if "[" in line and "]" in line:
                                            timestamp_str = line.split("[")[1].split("]")[0].strip()
                                        elif ":" in line and line.split(":")[0].strip().replace("-", "").replace(" ", "").isdigit():
                                            timestamp_parts = line.split(":", 1)[0].strip().split()
                                            if len(timestamp_parts) >= 2:
                                                timestamp_str = " ".join(timestamp_parts)
                                        
                                        # Zeitstempel parsen
                                        timestamp = None
                                        if timestamp_str:
                                            # Verschiedene Zeitstempelformate versuchen
                                            for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M"]:
                                                try:
                                                    timestamp = datetime.strptime(timestamp_str, fmt)
                                                    break
                                                except ValueError:
                                                    continue
                                        
                                        if not timestamp:
                                            timestamp = datetime.now()
                                        
                                        # Preis extrahieren (verschiedene Formate)
                                        price = 0
                                        # Format: "at $1234.56" oder "price $1234.56"
                                        price_patterns = [
                                            r'at\s+\$?(\d+(?:,\d+)*(?:\.\d+)?)',
                                            r'price\s+\$?(\d+(?:,\d+)*(?:\.\d+)?)',
                                            r'Price:\s+\$?(\d+(?:,\d+)*(?:\.\d+)?)',
                                            r'\$(\d+(?:,\d+)*(?:\.\d+)?)'
                                        ]
                                        
                                        for pattern in price_patterns:
                                            price_match = re.search(pattern, line)
                                            if price_match:
                                                # Kommas entfernen und als Float konvertieren
                                                price_str = price_match.group(1).replace(',', '')
                                                price = float(price_str)
                                                break
                                        
                                        # Signal-Typ bestimmen
                                        signal_type = ""
                                        if any(buy_pattern in line for buy_pattern in ["SIGNAL: BUY", "BUY SIGNAL"]):
                                            signal_type = "BUY"
                                        elif any(sell_pattern in line for sell_pattern in ["SIGNAL: SELL", "SELL SIGNAL"]):
                                            signal_type = "SELL"
                                        
                                        # Nur wenn gültiger Preis und Signal-Typ
                                        if price > 0 and signal_type:
                                            # Eindeutige ID für diesen Trade
                                            trade_id = f"{timestamp.strftime('%Y%m%d%H%M%S')}-{signal_type}"
                                            
                                            # Neuen Trade starten
                                            temp_trades[trade_id] = {
                                                'entry_time': timestamp,
                                                'entry_price': price,
                                                'side': signal_type,
                                                'status': 'OPEN'
                                            }
                                            
                                            # Signal ebenfalls speichern
                                            signals.append({
                                                'timestamp': timestamp,
                                                'price': price,
                                                'type': signal_type,
                                                'status': 'OPEN'
                                            })
                                    except Exception as e:
                                        print(f"Error parsing signal: {e}")
                                
                                # Trade-Exits erkennen (verschiedene Formate abdecken)
                                elif any(pattern in line for pattern in ["TRADE CLOSED", "EXIT:", "Position closed", "CLOSED AT"]):
                                    try:
                                        # Zeitstempel extrahieren (verschiedene Formate)
                                        timestamp_str = ""
                                        if "[" in line and "]" in line:
                                            timestamp_str = line.split("[")[1].split("]")[0].strip()
                                        elif ":" in line and line.split(":")[0].strip().replace("-", "").replace(" ", "").isdigit():
                                            timestamp_parts = line.split(":", 1)[0].strip().split()
                                            if len(timestamp_parts) >= 2:
                                                timestamp_str = " ".join(timestamp_parts)
                                        
                                        # Zeitstempel parsen
                                        timestamp = None
                                        if timestamp_str:
                                            # Verschiedene Zeitstempelformate versuchen
                                            for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M"]:
                                                try:
                                                    timestamp = datetime.strptime(timestamp_str, fmt)
                                                    break
                                                except ValueError:
                                                    continue
                                        
                                        if not timestamp:
                                            timestamp = datetime.now()
                                        
                                        # Preis extrahieren (verschiedene Formate)
                                        price = 0
                                        price_patterns = [
                                            r'at\s+\$?(\d+(?:,\d+)*(?:\.\d+)?)',
                                            r'price\s+\$?(\d+(?:,\d+)*(?:\.\d+)?)',
                                            r'Price:\s+\$?(\d+(?:,\d+)*(?:\.\d+)?)',
                                            r'\$(\d+(?:,\d+)*(?:\.\d+)?)'
                                        ]
                                        
                                        for pattern in price_patterns:
                                            price_match = re.search(pattern, line)
                                            if price_match:
                                                # Kommas entfernen und als Float konvertieren
                                                price_str = price_match.group(1).replace(',', '')
                                                price = float(price_str)
                                                break
                                        
                                        # PnL extrahieren (verschiedene Formate)
                                        pnl = None
                                        pnl_patterns = [
                                            r'PNL:\s+\$?([+-]?\d+(?:,\d+)*(?:\.\d+)?)',
                                            r'P&L:\s+\$?([+-]?\d+(?:,\d+)*(?:\.\d+)?)',
                                            r'Profit/Loss:\s+\$?([+-]?\d+(?:,\d+)*(?:\.\d+)?)',
                                            r'profit\s+\$?([+-]?\d+(?:,\d+)*(?:\.\d+)?)',
                                            r'loss\s+\$?([+-]?\d+(?:,\d+)*(?:\.\d+)?)'
                                        ]
                                        
                                        for pattern in pnl_patterns:
                                            pnl_match = re.search(pattern, line, re.IGNORECASE)
                                            if pnl_match:
                                                # Kommas entfernen und als Float konvertieren
                                                pnl_str = pnl_match.group(1).replace(',', '')
                                                pnl = float(pnl_str)
                                                break
                                        
                                        # Wenn offene Trades vorhanden, letzten schließen
                                        if temp_trades and price > 0:
                                            # Letzten offenen Trade nehmen
                                            last_trade_id = list(temp_trades.keys())[-1]
                                            if temp_trades[last_trade_id]['status'] == 'OPEN':
                                                temp_trades[last_trade_id]['exit_time'] = timestamp
                                                temp_trades[last_trade_id]['exit_price'] = price
                                                temp_trades[last_trade_id]['pnl'] = pnl
                                                temp_trades[last_trade_id]['status'] = 'CLOSED'
                                                
                                                # Korrespondierendes Signal auch als geschlossen markieren
                                                for signal in signals:
                                                    if (signal['timestamp'] == temp_trades[last_trade_id]['entry_time'] and 
                                                        signal['type'] == temp_trades[last_trade_id]['side']):
                                                        signal['status'] = 'CLOSED'
                                    except Exception as e:
                                        print(f"Error parsing exit: {e}")
                            
                            # Fertige Trades in die Haupt-Liste übernehmen
                            for trade_id, trade_data in temp_trades.items():
                                trades.append(trade_data)
                    except Exception as e:
                        print(f"Error reading log file {log_path}: {str(e)}")
        except Exception as e:
            print(f"Error processing trade logs: {str(e)}")
        
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
            'is_real': True,
            'kline_data': result.get('kline_data', pd.DataFrame()),
            'signals': signals,  # Trading-Signale für Chart
            'trades': trades,    # Ausgeführte Trades für Chart
            'bot_status': result.get('bot_status', {})
        }
    else:
        return {
            'api_connected': False,
            'error': 'API Connection failed',
            'is_real': False
        }

# ============================================================================
# DASHBOARD COMPONENTS - LIVE MAINNET
# ============================================================================

def render_mainnet_header():
    """MAINNET Warning Header"""
    
    st.markdown("""
    <div class="mainnet-header">
        <h1>💰 LIVE BYBIT MAINNET TRADING DASHBOARD 💰</h1>
        <h2>🔴 REAL MONEY - NO SIMULATION! 🔴</h2>
        <p style="font-size: 1.1rem; margin-top: 1rem;">
            Connected to your actual Bybit account with real USDT balance
        </p>
    </div>
    """, unsafe_allow_html=True)

def render_live_balance_section(data):
    """Echte Balance Anzeige"""
    
    if not data.get('api_connected', False):
        st.error("❌ API Connection Failed!")
        st.error(f"Error: {data.get('error', 'Unknown error')}")
        return
    
    # Real Portfolio Value
    portfolio_value = data['portfolio_value']
    account_type = data['account_type']
    
    st.markdown(f"""
    <div class="live-balance">
        💰 LIVE {account_type} PORTFOLIO: ${portfolio_value:.2f} USDT
        <br><small>🔄 Last Update: {data['last_update'].strftime('%H:%M:%S')}</small>
    </div>
    """, unsafe_allow_html=True)
    
    # Detailed Balance Breakdown
    st.markdown("### 💼 **LIVE BALANCE BREAKDOWN**")
    
    col1, col2, col3 = st.columns(3)
    
    balances = data['balances']
    
    with col1:
        usdt_balance = balances.get('USDT', 0)
        st.metric(
            label="💵 USDT Balance",
            value=f"{usdt_balance:.2f}",
            delta="Real Balance"
        )
    
    with col2:
        btc_balance = balances.get('BTC', 0)
        if btc_balance > 0:
            st.metric(
                label="₿ BTC Balance", 
                value=f"{btc_balance:.6f}",
                delta="Real Balance"
            )
        else:
            st.metric(
                label="₿ BTC Balance",
                value="0.000000",
                delta="No BTC"
            )
    
    with col3:
        st.metric(
            label="🏦 Account Type",
            value=account_type,
            delta="LIVE API"
        )

def render_live_btc_price(data):
    """Live BTC Preis von Bybit"""
    
    if not data.get('api_connected', False):
        return
    
    btc_price = data['btc_price']
    btc_change = data['btc_change_24h']
    btc_high = data['btc_high_24h']
    btc_low = data['btc_low_24h']
    
    st.markdown("### 📈 **LIVE BTC/USDT PRICE (Bybit)**")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        delta_color = "normal" if btc_change >= 0 else "inverse"
        st.metric(
            label="💎 Current Price",
            value=f"${btc_price:,.2f}",
            delta=f"{btc_change:+.2f}%",
            delta_color=delta_color
        )
    
    with col2:
        st.metric(
            label="📈 24h High",
            value=f"${btc_high:,.2f}",
            delta="Live Data"
        )
    
    with col3:
        st.metric(
            label="📉 24h Low", 
            value=f"${btc_low:,.2f}",
            delta="Live Data"
        )
    
    with col4:
        # Calculate range
        daily_range = ((btc_high - btc_low) / btc_low) * 100
        st.metric(
            label="📊 Daily Range",
            value=f"{daily_range:.2f}%",
            delta="Volatility"
        )

def render_no_simulation_notice():
    """Klarer Hinweis: KEINE SIMULATION"""
    
    st.markdown("""
    <div class="no-simulation">
        ⚠️ NO SIMULATION - ALL DATA IS REAL! ⚠️
        <br>This dashboard shows your actual Bybit Mainnet account data.
        <br>Portfolio values, balances, and prices are 100% real and live.
    </div>
    """, unsafe_allow_html=True)

def render_api_status(data):
    """Live API Status"""
    
    st.markdown("### 📡 **API CONNECTION STATUS**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if data.get('api_connected', False):
            st.markdown('<div class="api-status">✅ CONNECTED</div>', unsafe_allow_html=True)
        else:
            st.error("❌ DISCONNECTED")
    
    with col2:
        account_type = data.get('account_type', 'UNKNOWN')
        if account_type == 'MAINNET':
            st.markdown('<div class="api-status">💰 MAINNET</div>', unsafe_allow_html=True)
        else:
            st.warning(f"🧪 {account_type}")
    
    with col3:
        if data.get('is_real', False):
            st.markdown('<div class="api-status">🔴 LIVE DATA</div>', unsafe_allow_html=True)
        else:
            st.error("❌ NO LIVE DATA")

def render_trading_readiness():
    """Trading Readiness Check"""
    
    st.markdown("### 🚀 **TRADING READINESS STATUS**")
    
    # Get fresh data to check readiness
    data = get_live_mainnet_balance()
    
    readiness_checks = []
    
    if data.get('api_connected', False):
        readiness_checks.append(("✅", "API Connection", "Connected to Bybit Mainnet"))
    else:
        readiness_checks.append(("❌", "API Connection", "Failed to connect"))
    
    portfolio_value = data.get('portfolio_value', 0)
    if portfolio_value >= 50:
        readiness_checks.append(("✅", "Balance Check", f"${portfolio_value:.2f} USDT available"))
    elif portfolio_value > 0:
        readiness_checks.append(("⚠️", "Balance Check", f"Only ${portfolio_value:.2f} USDT (recommend 50+)"))
    else:
        readiness_checks.append(("❌", "Balance Check", "No USDT balance found"))
    
    if data.get('account_type') == 'MAINNET':
        readiness_checks.append(("✅", "Account Type", "Mainnet account confirmed"))
    else:
        readiness_checks.append(("⚠️", "Account Type", f"{data.get('account_type', 'Unknown')} account"))
    
    btc_price = data.get('btc_price', 0)
    if btc_price > 50000:
        readiness_checks.append(("✅", "Market Data", f"BTC price: ${btc_price:,.0f}"))
    else:
        readiness_checks.append(("❌", "Market Data", "Invalid BTC price data"))
    
    # Display readiness table
    readiness_df = pd.DataFrame(readiness_checks, columns=['Status', 'Check', 'Details'])
    st.dataframe(readiness_df, hide_index=True, use_container_width=True)
    
    # Overall readiness
    passed_checks = sum(1 for check in readiness_checks if check[0] == "✅")
    total_checks = len(readiness_checks)
    
    if passed_checks == total_checks:
        st.success(f"🚀 **READY FOR LIVE TRADING!** ({passed_checks}/{total_checks} checks passed)")
        # Balloons entfernt
    elif passed_checks >= total_checks - 1:
        st.warning(f"⚠️ **MOSTLY READY** ({passed_checks}/{total_checks} checks passed)")
    else:
        st.error(f"❌ **NOT READY** ({passed_checks}/{total_checks} checks passed)")

def render_sidebar_live_controls(data):
    """Sidebar mit Live Controls"""
    
    st.sidebar.markdown("### 💰 **LIVE MAINNET CONTROLS**")
    
    # Auto-refresh
    auto_refresh = st.sidebar.checkbox("🔄 Auto-Refresh (15s)", value=True)
    
    if auto_refresh:
        st.sidebar.success("🔄 Live Updates: ON")
        time.sleep(0.1)
        st.rerun()
    else:
        if st.sidebar.button("🔄 Refresh Now"):
            st.cache_data.clear()
            st.rerun()
    
    # Connection Status
    st.sidebar.markdown("### 📡 **STATUS**")
    if data.get('api_connected', False):
        st.sidebar.success("✅ Bybit API: CONNECTED")
        st.sidebar.success(f"💰 Account: {data.get('account_type', 'UNKNOWN')}")
        st.sidebar.success("🔴 Data: LIVE & REAL")
    else:
        st.sidebar.error("❌ API: DISCONNECTED")
        st.sidebar.warning("⚠️ No live data available")
    
    # Bot Status
    bot_status = data.get('bot_status', {})
    st.sidebar.markdown("### 🤖 **BOT STATUS**")
    
    if bot_status.get('running', False):
        st.sidebar.success(f"✅ Bot Running (PID: {bot_status.get('process_id')})")
        st.sidebar.info(f"⏱️ Uptime: {bot_status.get('uptime', 'unknown')}")
        
        # Market Regime
        market_regime = bot_status.get('market_regime')
        if market_regime:
            if market_regime == "BULL":
                st.sidebar.success(f"🚀 Market Regime: {market_regime}")
            elif market_regime == "BEAR":
                st.sidebar.error(f"📉 Market Regime: {market_regime}")
            else:
                st.sidebar.warning(f"↔️ Market Regime: {market_regime}")
        
        # Last Signal
        last_signal = bot_status.get('last_signal')
        if last_signal:
            if last_signal == "BUY":
                st.sidebar.success(f"💰 Last Signal: {last_signal}")
            else:
                st.sidebar.error(f"📉 Last Signal: {last_signal}")
    else:
        st.sidebar.warning("⚠️ Bot nicht aktiv")
        st.sidebar.info("Dashboard im View-Only Modus")
    
    # Balance Info
    if data.get('api_connected', False):
        st.sidebar.markdown("### 💼 **QUICK BALANCE**")
        portfolio_value = data.get('portfolio_value', 0)
        st.sidebar.metric("Total USDT", f"${portfolio_value:.2f}")
        
        balances = data.get('balances', {})
        for coin, amount in balances.items():
            if coin == 'USDT':
                st.sidebar.metric(f"{coin} Balance", f"{amount:.2f}")
            else:
                st.sidebar.metric(f"{coin} Balance", f"{amount:.6f}")
    
    # Emergency Controls
    st.sidebar.markdown("### 🚨 **EMERGENCY**")
    
    emergency_col1, emergency_col2 = st.sidebar.columns(2)
    
    with emergency_col1:
        if st.button("🛑 EMERGENCY STOP", type="primary"):
            # API-Objekt erstellen und Emergency-Stop ausführen
            api = LiveBybitAPI()
            result = api.emergency_stop_bot()
            
            if result['success']:
                st.sidebar.success(f"✅ {result['message']}")
                # Kurz warten und Seite neu laden
                time.sleep(1)
                st.rerun()
            else:
                st.sidebar.error(f"❌ {result['message']}")
    
    with emergency_col2:
        if st.button("📊 CLOSE POSITIONS"):
            # Hier könnte man alle offenen Positionen schließen
            st.sidebar.warning("⚠️ Position Closing würde hier alle offenen Positionen schließen")
    
    # Open Positions
    if data.get('open_positions', False):
        st.sidebar.markdown("### 📊 **OPEN POSITIONS**")
        positions = data.get('positions', [])
        for pos in positions:
            symbol = pos.get('symbol', 'Unknown')
            size = float(pos.get('size', 0))
            side = pos.get('side', 'Unknown')
            pnl = float(pos.get('unrealisedPnl', 0))
            
            if side == "Buy":
                st.sidebar.success(f"LONG {symbol}: {size} (P&L: ${pnl:.2f})")
            else:
                st.sidebar.error(f"SHORT {symbol}: {size} (P&L: ${pnl:.2f})")
    
    # System Info
    st.sidebar.markdown("### ⚙️ **SYSTEM INFO**")
    st.sidebar.text("Mode: LIVE MAINNET")
    st.sidebar.text("Simulation: DISABLED")
    st.sidebar.text("Real Money: YES")
    
    if data.get('last_update'):
        st.sidebar.text(f"Last Update: {data['last_update'].strftime('%H:%M:%S')}")

# ============================================================================
# MAIN DASHBOARD FUNCTION
# ============================================================================

def render_btc_chart(data):
    """Renders a professional BTC/USDT candlestick chart with volume"""
    st.markdown("### 📈 **LIVE BTC/USDT CHART**")
    
    # Chart Controls
    chart_col1, chart_col2, chart_col3 = st.columns([2, 2, 1])
    
    with chart_col1:
        chart_interval = st.selectbox(
            "Zeitintervall",
            ["1", "3", "5", "15", "30", "60", "240", "D"],
            index=2,
            key="chart_interval"
        )
    
    with chart_col2:
        chart_limit = st.selectbox(
            "Anzahl Kerzen",
            [50, 100, 200, 500],
            index=1,
            key="chart_limit"
        )
    
    with chart_col3:
        if st.button("🔄 Chart laden"):
            st.cache_data.clear()
            # Direkt Kline-Daten holen
            with st.spinner("Lade Chart-Daten..."):
                api = LiveBybitAPI()
                kline_result = api.get_kline_data(
                    symbol='BTCUSDT',
                    interval=chart_interval,
                    limit=chart_limit
                )
                if kline_result['success'] and 'data' in kline_result:
                    data['kline_data'] = kline_result['data']
                    st.success("✅ Chart-Daten erfolgreich geladen!")
                else:
                    st.error(f"❌ Fehler beim Laden der Chart-Daten: {kline_result.get('error', 'Unbekannter Fehler')}")
    
    # Aktiv Kline-Daten abrufen, wenn sie nicht im Cache sind
    if 'kline_data' not in data or data['kline_data'].empty:
        with st.spinner("Lade Chart-Daten..."):
            api = LiveBybitAPI()
            kline_result = api.get_kline_data(
                symbol='BTCUSDT',
                interval=chart_interval,
                limit=chart_limit
            )
            
            if kline_result['success'] and 'data' in kline_result and not kline_result['data'].empty:
                df = kline_result['data']
            else:
                st.warning("⚠️ Keine Chart-Daten verfügbar. Bitte drücken Sie auf 'Chart laden'.")
                return
    else:
        df = data['kline_data']
    
    if df.empty:
        st.warning("⚠️ Keine Chart-Daten verfügbar. Bitte drücken Sie auf 'Chart laden'.")
        return
    
    # Erstelle einen Subplots mit 2 Zeilen (1 für Candlesticks, 1 für Volume)
    fig = go.Figure()
    
    # Erstelle Candlestick Chart
    fig = go.Figure(data=[go.Candlestick(
        x=df['timestamp'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        increasing_line_color='#26a69a',  # Grün für bullish candles
        decreasing_line_color='#ef5350',  # Rot für bearish candles
        name='BTC/USDT'
    )])
    
    # Füge Volume als Balken hinzu
    colors = ['#26a69a' if row['close'] >= row['open'] else '#ef5350' for _, row in df.iterrows()]
    
    fig.add_trace(go.Bar(
        x=df['timestamp'],
        y=df['volume'],
        marker_color=colors,
        name='Volume',
        opacity=0.5,
        yaxis='y2'  # Verwende die zweite y-Achse
    ))
    
    # Add Moving Averages for better context
    fig.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df['close'].rolling(20).mean(),
        line=dict(color='rgba(46, 204, 113, 0.7)', width=1.5),
        name='MA20'
    ))
    
    fig.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df['close'].rolling(50).mean(),
        line=dict(color='rgba(52, 152, 219, 0.7)', width=1.5),
        name='MA50'
    ))
    
    # Chart Layout konfigurieren
    fig.update_layout(
        title='BTC/USDT - Live Bybit Mainnet',
        xaxis_title='Time',
        yaxis_title='Price (USDT)',
        xaxis_rangeslider_visible=False,  # Rangeslider ausblenden für ein professionelleres Aussehen
        template='plotly_dark',  # Dunkles Theme
        plot_bgcolor='rgba(32, 33, 36, 0.9)',  # Chart Hintergrundfarbe
        paper_bgcolor='rgba(32, 33, 36, 0.9)',  # Papier Hintergrundfarbe
        font=dict(color='rgba(255, 255, 255, 0.85)'),  # Textfarbe
        height=600,  # Höhe des Charts
        # Setup für eine zweite y-Achse für das Volume
        yaxis2=dict(
            title='Volume',
            titlefont=dict(color='rgba(255, 255, 255, 0.85)'),
            tickfont=dict(color='rgba(255, 255, 255, 0.85)'),
            anchor="x",
            overlaying="y",
            side="right",
            showgrid=False
        ),
        # Legende konfigurieren
        legend=dict(
            x=0,
            y=1.0,
            bgcolor='rgba(50, 50, 50, 0.2)',
            bordercolor='rgba(255, 255, 255, 0.2)'
        ),
        margin=dict(l=10, r=10, b=10, t=40),
    )
    
    # Add Volume Layout
    fig.update_yaxes(
        showgrid=True, 
        gridwidth=1, 
        gridcolor='rgba(255, 255, 255, 0.1)',
        zeroline=False
    )
    
    # X-Achse anpassen
    fig.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='rgba(255, 255, 255, 0.1)',
        zeroline=False
    )
    
    # Chart anzeigen
    st.plotly_chart(fig, use_container_width=True)
    
    # Trade-Signale hinzufügen (wenn vorhanden)
    if 'signals' in data and data['signals']:
        # Zeige die Anzahl der gefundenen Signale
        num_signals = len(data['signals'])
        st.info(f"📊 {num_signals} Trading-Signale im Chart angezeigt")
        
        # Chart mit Signalen erstellen
        fig_signals = go.Figure(fig)  # Kopie des Haupt-Charts
        
        for signal in data['signals']:
            signal_time = signal['timestamp']
            signal_price = signal['price']
            signal_type = signal['type']  # 'BUY' oder 'SELL'
            
            # Signal-Pfeil hinzufügen
            if signal_type == 'BUY':
                fig_signals.add_trace(go.Scatter(
                    x=[signal_time],
                    y=[signal_price * 0.995],  # Leicht unter dem Preis
                    mode='markers',
                    marker=dict(
                        symbol='triangle-up',
                        size=15,
                        color='green',
                        line=dict(width=2, color='darkgreen')
                    ),
                    name='BUY Signal',
                    hoverinfo='text',
                    hovertext=f'BUY Signal: ${signal_price:,.2f}'
                ))
            else:
                fig_signals.add_trace(go.Scatter(
                    x=[signal_time],
                    y=[signal_price * 1.005],  # Leicht über dem Preis
                    mode='markers',
                    marker=dict(
                        symbol='triangle-down',
                        size=15,
                        color='red',
                        line=dict(width=2, color='darkred')
                    ),
                    name='SELL Signal',
                    hoverinfo='text',
                    hovertext=f'SELL Signal: ${signal_price:,.2f}'
                ))
        
        # Ausgeführte Trades hinzufügen (wenn vorhanden)
        if 'trades' in data and data['trades']:
            trades = data['trades']
            
            for trade in trades:
                entry_time = trade['entry_time']
                entry_price = trade['entry_price']
                exit_time = trade.get('exit_time')
                exit_price = trade.get('exit_price')
                side = trade['side']  # 'BUY' oder 'SELL'
                pnl = trade.get('pnl')
                
                # Entry-Point markieren
                entry_color = 'green' if side == 'BUY' else 'red'
                fig_signals.add_trace(go.Scatter(
                    x=[entry_time],
                    y=[entry_price],
                    mode='markers',
                    marker=dict(
                        symbol='circle',
                        size=12,
                        color=entry_color,
                        line=dict(width=2, color='white')
                    ),
                    name=f'{side} Entry',
                    hoverinfo='text',
                    hovertext=f'{side} Entry: ${entry_price:,.2f}'
                ))
                
                # Exit-Point markieren (wenn vorhanden)
                if exit_time and exit_price:
                    # PnL berechnen
                    pnl_text = ""
                    if pnl:
                        pnl_color = 'green' if pnl > 0 else 'red'
                        pnl_text = f" | P&L: ${pnl:+,.2f}"
                    
                    exit_color = 'green' if (side == 'BUY' and exit_price > entry_price) or (side == 'SELL' and exit_price < entry_price) else 'red'
                    fig_signals.add_trace(go.Scatter(
                        x=[exit_time],
                        y=[exit_price],
                        mode='markers',
                        marker=dict(
                            symbol='square',
                            size=12,
                            color=exit_color,
                            line=dict(width=2, color='white')
                        ),
                        name=f'Exit {side}',
                        hoverinfo='text',
                        hovertext=f'Exit {side}: ${exit_price:,.2f}{pnl_text}'
                    ))
                    
                    # Linie zwischen Entry und Exit
                    fig_signals.add_trace(go.Scatter(
                        x=[entry_time, exit_time],
                        y=[entry_price, exit_price],
                        mode='lines',
                        line=dict(
                            color=exit_color,
                            width=2,
                            dash='dot'
                        ),
                        showlegend=False
                    ))
            
            # Zeige Anzahl der Trades
            st.info(f"💰 {len(trades)} ausgeführte Trades im Chart angezeigt")
            
        # Chart mit Signalen anzeigen
        if 'signals' in data and data['signals'] or ('trades' in data and data['trades']):
            st.markdown("### 📈 **TRADING SIGNALE & AUSGEFÜHRTE TRADES**")
            st.plotly_chart(fig_signals, use_container_width=True)
    
    # Kleine Info unter dem Chart
    last_candle = df.iloc[-1]
    latest_price = last_candle['close']
    timestamp = last_candle['timestamp']
    
    # Vergleiche mit dem vorherigen Schlusskurs
    previous_close = df.iloc[-2]['close'] if len(df) > 1 else last_candle['open']
    price_change = latest_price - previous_close
    price_change_pct = (price_change / previous_close) * 100
    
    col1, col2, col3 = st.columns(3)
    with col1:
        delta_color = "normal" if price_change >= 0 else "inverse"
        st.metric(
            label="Current Close",
            value=f"${latest_price:,.2f}",
            delta=f"{price_change_pct:+.2f}%",
            delta_color=delta_color
        )
    
    with col2:
        st.metric(
            label="24h Range",
            value=f"${data.get('btc_low_24h', 0):,.0f} - ${data.get('btc_high_24h', 0):,.0f}",
            delta="Live Data"
        )
    
    with col3:
        st.metric(
            label="Last Update",
            value=timestamp.strftime('%H:%M:%S'),
            delta="Live Chart"
        )
    
    # Trennlinie
    st.markdown("---")

def render_trading_activity(data):
    """Trading Activity Panel mit Signal-Details und Trade-History"""
    
    st.markdown("### 📊 **TRADING ACTIVITY & SIGNAL HISTORY**")
    
    # Tab-System für verschiedene Ansichten
    activity_tab1, activity_tab2 = st.tabs(["📈 Trading Signals", "💰 Trade History"])
    
    with activity_tab1:
        # Trading Signals Tab
        if 'signals' in data and data['signals']:
            signals = data['signals']
            
            # DataFrame für Signale erstellen
            signal_data = []
            for signal in signals:
                signal_data.append({
                    'Timestamp': signal['timestamp'],
                    'Type': signal['type'],
                    'Price': f"${signal['price']:,.2f}",
                    'Status': 'Active' if signal.get('status', 'OPEN') == 'OPEN' else 'Closed'
                })
            
            # DataFrame erstellen und anzeigen
            if signal_data:
                signal_df = pd.DataFrame(signal_data)
                signal_df = signal_df.sort_values('Timestamp', ascending=False).reset_index(drop=True)
                
                # Styling für Buy/Sell
                def highlight_signal_type(val):
                    if val == 'BUY':
                        return 'background-color: rgba(46, 204, 113, 0.2); color: #2ecc71; font-weight: bold'
                    elif val == 'SELL':
                        return 'background-color: rgba(231, 76, 60, 0.2); color: #e74c3c; font-weight: bold'
                    return ''
                
                # Styling anwenden
                styled_signal_df = signal_df.style.applymap(highlight_signal_type, subset=['Type'])
                
                # Signal Tabelle anzeigen
                st.dataframe(styled_signal_df, use_container_width=True, hide_index=True)
                
                # Signal Statistik
                buy_signals = sum(1 for signal in signals if signal['type'] == 'BUY')
                sell_signals = sum(1 for signal in signals if signal['type'] == 'SELL')
                
                signal_stats_col1, signal_stats_col2, signal_stats_col3 = st.columns(3)
                with signal_stats_col1:
                    st.metric("Total Signals", f"{len(signals)}")
                with signal_stats_col2:
                    st.metric("Buy Signals", f"{buy_signals}")
                with signal_stats_col3:
                    st.metric("Sell Signals", f"{sell_signals}")
            else:
                st.info("Keine Trading-Signale gefunden.")
        else:
            st.info("Keine Trading-Signale in den Log-Dateien gefunden.")
    
    with activity_tab2:
        # Trade History Tab
        if 'trades' in data and data['trades']:
            trades = data['trades']
            
            # DataFrame für Trades erstellen
            trade_data = []
            for trade in trades:
                # Profit/Loss berechnen
                pnl = trade.get('pnl', None)
                pnl_str = f"${pnl:+,.2f}" if pnl is not None else "Open"
                
                # Status bestimmen
                status = 'CLOSED' if 'exit_time' in trade else 'OPEN'
                
                # Trade-Daten hinzufügen
                trade_data.append({
                    'Entry Time': trade.get('entry_time'),
                    'Exit Time': trade.get('exit_time', '-'),
                    'Side': trade.get('side', '-'),
                    'Entry Price': f"${trade.get('entry_price', 0):,.2f}",
                    'Exit Price': f"${trade.get('exit_price', 0):,.2f}" if 'exit_price' in trade else '-',
                    'P&L': pnl_str,
                    'Status': status
                })
            
            # DataFrame erstellen und anzeigen
            if trade_data:
                trade_df = pd.DataFrame(trade_data)
                trade_df = trade_df.sort_values('Entry Time', ascending=False).reset_index(drop=True)
                
                # Styling für P&L und Side
                def highlight_pnl(val):
                    if val == "Open":
                        return 'background-color: rgba(52, 152, 219, 0.2); color: #3498db'
                    elif val.startswith('$+'):
                        return 'background-color: rgba(46, 204, 113, 0.2); color: #2ecc71; font-weight: bold'
                    elif val.startswith('$-'):
                        return 'background-color: rgba(231, 76, 60, 0.2); color: #e74c3c; font-weight: bold'
                    return ''
                
                def highlight_side(val):
                    if val == 'BUY':
                        return 'background-color: rgba(46, 204, 113, 0.2); color: #2ecc71; font-weight: bold'
                    elif val == 'SELL':
                        return 'background-color: rgba(231, 76, 60, 0.2); color: #e74c3c; font-weight: bold'
                    return ''
                
                # Styling anwenden
                styled_trade_df = trade_df.style.applymap(highlight_pnl, subset=['P&L']).applymap(highlight_side, subset=['Side'])
                
                # Trade Tabelle anzeigen
                st.dataframe(styled_trade_df, use_container_width=True, hide_index=True)
                
                # Trade Statistik
                closed_trades = sum(1 for trade in trades if trade.get('status', '') == 'CLOSED')
                open_trades = sum(1 for trade in trades if trade.get('status', '') == 'OPEN')
                
                # Profit/Loss Berechnung
                total_pnl = sum(trade.get('pnl', 0) for trade in trades if trade.get('pnl') is not None)
                profitable_trades = sum(1 for trade in trades if trade.get('pnl', 0) > 0)
                loss_trades = sum(1 for trade in trades if trade.get('pnl', 0) < 0)
                
                # Win Rate berechnen
                win_rate = (profitable_trades / closed_trades * 100) if closed_trades > 0 else 0
                
                # Statistik anzeigen
                trade_stats_col1, trade_stats_col2, trade_stats_col3, trade_stats_col4 = st.columns(4)
                with trade_stats_col1:
                    st.metric("Total Trades", f"{len(trades)}")
                with trade_stats_col2:
                    st.metric("Closed Trades", f"{closed_trades}")
                with trade_stats_col3:
                    delta_color = "normal" if total_pnl >= 0 else "inverse"
                    st.metric("Total P&L", f"${total_pnl:,.2f}", delta=f"{win_rate:.1f}% Win Rate", delta_color=delta_color)
                with trade_stats_col4:
                    st.metric("Win/Loss", f"{profitable_trades}/{loss_trades}")
            else:
                st.info("Keine Trade-Historie gefunden.")
        else:
            st.info("Keine Trade-Historie in den Log-Dateien gefunden.")
    
    # Trennlinie
    st.markdown("---")

def render_manual_trading_controls(data):
    """Manual Trading Controls"""
    
    st.markdown("### 🎮 **MANUAL TRADING CONTROLS**")
    st.warning("⚠️ **ACHTUNG**: Diese Trades erfolgen mit echtem Geld auf dem Mainnet!")
    
    # Layout für Trading Controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        symbol = st.selectbox("Symbol", ["BTCUSDT", "ETHUSDT", "SOLUSDT"], index=0)
        if symbol == "BTCUSDT":
            current_price = data.get('btc_price', 0)
        else:
            # Für andere Symbole den aktuellen Preis abrufen
            api = LiveBybitAPI()
            ticker_data = api.get_live_ticker(symbol=symbol)
            current_price = ticker_data.get('price', 0) if ticker_data.get('success', False) else 0
            
        st.info(f"Aktueller Preis: ${current_price:,.2f}")
    
    with col2:
        side = st.radio("Richtung", ["Buy", "Sell"], horizontal=True)
        
        # Für USDT-Wert
        trade_amount_usdt = st.number_input("Trade Größe (USDT)", min_value=5.0, max_value=50.0, value=10.0, step=5.0)
        
        # Umrechnung in Asset-Einheiten
        if current_price > 0:
            quantity = round(trade_amount_usdt / current_price, 6)
            st.info(f"≈ {quantity:.6f} {symbol[:3]}")
        else:
            quantity = 0
            st.error("Preis nicht verfügbar")
    
    with col3:
        order_type = st.radio("Order Typ", ["Market", "Limit"], horizontal=True)
        
        # Nur für Limit Orders
        limit_price = None
        if order_type == "Limit":
            limit_price = st.number_input("Limit Preis", value=float(current_price), step=10.0)
        
        # Risk Management
        use_sl_tp = st.checkbox("Stop-Loss / Take-Profit", value=True)
        
        # Nur anzeigen wenn SL/TP aktiviert ist
        sl_price, tp_price = None, None
        if use_sl_tp:
            if side == "Buy":
                sl_percent = st.slider("Stop-Loss (%)", min_value=1.0, max_value=5.0, value=2.0, step=0.5)
                tp_percent = st.slider("Take-Profit (%)", min_value=1.0, max_value=10.0, value=3.0, step=0.5)
                
                if current_price > 0:
                    sl_price = round(current_price * (1 - sl_percent/100), 2)
                    tp_price = round(current_price * (1 + tp_percent/100), 2)
                    
                    st.info(f"SL: ${sl_price:,.2f} | TP: ${tp_price:,.2f}")
            else:
                # Für Sell Orders
                sl_percent = st.slider("Stop-Loss (%)", min_value=1.0, max_value=5.0, value=2.0, step=0.5)
                tp_percent = st.slider("Take-Profit (%)", min_value=1.0, max_value=10.0, value=3.0, step=0.5)
                
                if current_price > 0:
                    sl_price = round(current_price * (1 + sl_percent/100), 2)
                    tp_price = round(current_price * (1 - tp_percent/100), 2)
                    
                    st.info(f"SL: ${sl_price:,.2f} | TP: ${tp_price:,.2f}")
    
    # Execute Trade Button
    trade_col1, trade_col2 = st.columns([3, 1])
    
    with trade_col1:
        trade_summary = f"""
        **Trade Details**: {side} {quantity:.6f} {symbol[:3]} @ {'MARKET' if order_type == 'Market' else f'${limit_price:,.2f}'} 
        **Wert**: ${trade_amount_usdt:.2f} USDT
        """
        if use_sl_tp:
            trade_summary += f" | **SL**: ${sl_price:,.2f} | **TP**: ${tp_price:,.2f}"
        
        st.markdown(trade_summary)
    
    with trade_col2:
        if st.button(f"🚀 {side.upper()} {symbol[:3]}", type="primary" if side == "Buy" else "secondary"):
            # Ausführung bestätigen
            st.warning(f"⚠️ Bestätige den {side} von {quantity:.6f} {symbol[:3]}")
            
            confirm_col1, confirm_col2 = st.columns(2)
            with confirm_col1:
                if st.button("✅ BESTÄTIGEN", type="primary"):
                    # API-Objekt erstellen und Trade ausführen
                    api = LiveBybitAPI()
                    result = api.place_manual_trade(
                        side=side,
                        symbol=symbol,
                        quantity=quantity,
                        price=limit_price if order_type == "Limit" else None,
                        stop_loss=sl_price if use_sl_tp else None,
                        take_profit=tp_price if use_sl_tp else None
                    )
                    
                    if result.get('success', False):
                        st.success(f"✅ {result['message']}")
                        # Order ID anzeigen
                        st.info(f"Order ID: {result.get('order_id', 'Unknown')}")
                        # Kurz warten und Seite neu laden
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error(f"❌ {result.get('error', 'Unknown error')}")
                        
            with confirm_col2:
                if st.button("❌ ABBRECHEN"):
                    st.info("Trade abgebrochen")
                    # Neu laden um die Buttons zurückzusetzen
                    time.sleep(0.5)
                    st.rerun()
    
    # Hinweis
    st.caption("Alle Trades werden sofort auf dem Bybit Mainnet ausgeführt. Benutze dieses Feature mit Vorsicht.")
    
    # Trennlinie
    st.markdown("---")

def main():
    """Main dashboard function"""
    
    # Get live data from Bybit
    data = get_live_mainnet_balance()
    
    # Render dashboard components
    render_mainnet_header()
    
    if data.get('api_connected', False):
        # Top row with key metrics
        render_live_balance_section(data)
        render_live_btc_price(data)
        
        # Trading readiness
        render_trading_readiness()
        
        # Chart Initialisierung
        st.session_state.chart_initialized = st.session_state.get('chart_initialized', False)
        
        # BTC/USDT Chart anzeigen
        if not st.session_state.chart_initialized:
            with st.spinner("Initialisiere Chart-Daten..."):
                # Explizit Kline-Daten holen, wenn nicht vorhanden
                if 'kline_data' not in data or isinstance(data.get('kline_data'), pd.DataFrame) and data['kline_data'].empty:
                    api = LiveBybitAPI()
                    kline_result = api.get_kline_data(symbol='BTCUSDT', interval='5', limit=100)
                    if kline_result['success'] and 'data' in kline_result:
                        data['kline_data'] = kline_result['data']
                        st.session_state.chart_initialized = True
        
        # Chart anzeigen
        render_btc_chart(data)
        
        # Trading Activity Panel hinzufügen
        render_trading_activity(data)
        
        # Trading controls
        render_manual_trading_controls(data)
        
        # No simulation notice
        render_no_simulation_notice()
        
        # API status
        render_api_status(data)
    else:
        st.error("❌ API Connection Failed!")
        st.error(f"Error: {data.get('error', 'Unable to connect to Bybit API')}")
        st.info("Please check your API credentials and internet connection.")
    
    # Sidebar with live controls
    render_sidebar_live_controls(data)

if __name__ == "__main__":
    main()
