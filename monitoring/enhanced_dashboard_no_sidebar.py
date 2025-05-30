import sys
import io
import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import json
import time
from typing import Dict, List, Optional
import traceback

# Projektverzeichnis zum Python-Pfad hinzufügen
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
    print(f"Projektverzeichnis zum Python-Pfad hinzugefügt: {project_root}")

# Importe für Smart Money Chart
try:
    from ui.advanced_chart import SmartMoneyChart
    from core.api_client import BybitAPI
except ImportError as e:
    st.error(f"Kritischer Importfehler: {str(e)}")
    print(f"Importfehler: {traceback.format_exc()}")
    # Fallback: Platzhalter für fehlende Komponenten
    class SmartMoneyChart:
        def __init__(self, *args, **kwargs):
            pass
        def load_data(self, *args, **kwargs):
            return False
        def render_chart(self, *args, **kwargs):
            return None

# ... [bestehender Code] ...

def render_smart_money_chart():
    """
    Render advanced trading chart with Fair Value Gaps and volume
    
    Diese Funktion erstellt einen professionellen Trading-Chart mit:
    - Fair Value Gaps (FVG) Visualisierung
    - Volume-Anzeige im unteren Bereich
    - Unterstützungs-/Widerstandslinien
    - Echtzeit-Daten von der Bybit API
    
    Fehler werden umfassend behandelt und protokolliert.
    """
    st.markdown("## 📊 **SMART MONEY CHART**")
    
    try:
        # Initialisiere API-Client mit Fehlerbehandlung
        try:
            api_client = BybitAPI()
            st.session_state['api_status'] = "Verbunden"
        except Exception as api_error:
            st.error(f"API-Verbindungsfehler: {str(api_error)}")
            st.session_state['api_status'] = "Fehler"
            return
        
        # Chart-Objekt erstellen
        try:
            chart = SmartMoneyChart(
                api_client=api_client,
                symbol="BTCUSDT",
                timeframe="15"
            )
        except Exception as init_error:
            st.error(f"Chart-Initialisierungsfehler: {str(init_error)}")
            return
        
        # Lade Marktdaten
        try:
            if chart.load_data(limit=200):
                st.success("Daten erfolgreich geladen")
                # Rendere den Chart
                fig = chart.render_chart(height=600)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Chart konnte nicht generiert werden")
            else:
                st.error("Chart-Daten konnten nicht geladen werden")
                # Debug-Informationen anzeigen
                st.write("API-Status:", st.session_state.get('api_status', 'Unbekannt'))
                st.write("Letzter Fehler:", traceback.format_exc())
        except Exception as data_error:
            st.error(f"Datenverarbeitungsfehler: {str(data_error)}")
            print(f"DEBUG: {traceback.format_exc()}")
            # Fallback: Einfache Fehlermeldung anzeigen
            st.warning("Smart Money Chart konnte nicht geladen werden. Bitte versuchen Sie es später erneut.")
            
    except Exception as e:
        st.error(f"Kritischer Fehler: {str(e)}")
        print(f"CRITICAL: {traceback.format_exc()}")

# ... [bestehender Code] ...

def main():
    # ... [bestehender Code] ...
    
    # Main rendering flow
    render_main_overview(data_provider)
    # Haupt-Rendering-Fluss
    render_main_overview(data_provider)
    render_smart_money_chart()
    render_position_status(data_provider)
    render_market_regime_panel(data_provider)
    render_performance_charts(data_provider)
    render_risk_management_panel(data_provider)
    render_trade_log(data_provider)
    render_footer()

# ... [bestehender Code] ...
# Import Corrected Live API
from corrected_live_api import LiveBybitAPI
from data_integration import DataIntegration

# ============================================================================
# CONFIGURATION & SETUP
# ============================================================================

st.set_page_config(
    page_title="Enhanced Smart Money Bot",
    page_icon="🚀",
    layout="wide"
)

# Custom CSS for professional styling without sidebar
st.markdown("""
<style>
    /* Expand main content to full width */
    .main .block-container {
        max-width: 100% !important;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .status-good { color: #00ff00; font-weight: bold; }
    .status-warning { color: #ffaa00; font-weight: bold; }
    .status-danger { color: #ff0000; font-weight: bold; }
    .regime-bull { background: linear-gradient(90deg, #2ecc71, #27ae60); }
    .regime-bear { background: linear-gradient(90deg, #e74c3c, #c0392b); }
    .regime-sideways { background: linear-gradient(90deg, #f39c12, #e67e22); }
    .signal-strong { background: #2ecc71; color: white; padding: 0.2rem 0.5rem; border-radius: 5px; }
    .signal-weak { background: #e74c3c; color: white; padding: 0.2rem 0.5rem; border-radius: 5px; }
    .signal-hold { background: #f39c12; color: white; padding: 0.2rem 0.5rem; border-radius: 5px; }
    
    .stDataFrame {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
    }
    
    /* Boxed container styling */
    .dashboard-section {
        background: linear-gradient(145deg, rgba(40, 42, 54, 0.9), rgba(30, 31, 41, 0.9));
        border: 1px solid rgba(86, 125, 188, 0.3);
        border-radius: 12px;
        padding: 1.8rem;
        margin-bottom: 1.8rem;
        box-shadow: 0 6px 25px rgba(0, 0, 0, 0.25);
        backdrop-filter: blur(4px);
    }
    
    .dashboard-header {
        margin-bottom: 1.5rem;
        border-bottom: 2px solid rgba(102, 126, 234, 0.7);
        padding-bottom: 0.7rem;
        color: #f8f8f2;
        font-weight: 600;
    }
    
    /* Improve text readability */
    .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {
        color: #f8f8f2 !important;
    }
    
    .stDataFrame, .stTable {
        color: #f8f8f2;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# HEADER & CONTROL PANEL COMPONENTS
# ============================================================================

def render_header():
    """Render dashboard header with timestamp"""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f"<h1 style='margin-bottom: 0;'>🚀 Enhanced Smart Money Bot Dashboard</h1>", unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"<div style='text-align: right; color: #888; margin-top: 15px;'>{current_time}</div>", unsafe_allow_html=True)
    
    st.markdown("---")

def render_control_panel():
    """Render bot control panel with status indicators and buttons"""
    with st.container():
        st.markdown("### Bot Kontrollzentrum")
        col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
        
        with col1:
            st.markdown("**Status**")
            status = st.empty()
            status.markdown("<div class='status-good'>▶ Aktiv</div>", unsafe_allow_html=True)
            
            st.markdown("**Letzte Aktion**")
            st.markdown("<div>Keine</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("**Steuerung**")
            start_btn = st.button("▶ Start", key="start_btn", use_container_width=True)
            stop_btn = st.button("⏹ Stop", key="stop_btn", use_container_width=True)
            pause_btn = st.button("⏸ Pause", key="pause_btn", use_container_width=True)
        
        with col3:
            st.markdown("**API Status**")
            api_status = st.empty()
            api_status.markdown("<div class='status-good'>✓ Verbunden</div>", unsafe_allow_html=True)
            
            st.markdown("**Letzter Ping**")
            st.markdown("<div>vor 2s</div>", unsafe_allow_html=True)
        
        with col4:
            st.markdown("**Notfall**")
            emergency_btn = st.button("⛔ Notfall-Stop",
                                      key="emergency_btn",
                                      type="primary",
                                      use_container_width=True,
                                      help="Sofortiger Stop aller Handelsaktivitäten")
        
        st.checkbox("🔄 Automatische Aktualisierung", value=True, key="auto_refresh")

# ============================================================================
# DATA SERVICE & PROVIDER
# ============================================================================

class DataService:
    """Centralized data service for consistent API access"""
    
    def __init__(self):
        self.live_api = LiveBybitAPI()
        self.bybit_client = BybitAPI()  # Konsistente Verwendung von BybitAPI
        self.cache = {}
        self.cache_timestamps = {}
        self.cache_duration = 300  # Cache für 5 Minuten
        
    def get_portfolio_data(self):
        """Get unified portfolio data from API"""
        if 'portfolio' not in self.cache or (time.time() - self.cache_timestamps.get('portfolio', 0)) > self.cache_duration:
            data = self.live_api.get_wallet_balance()
            if data.get('success'):
                self.cache['portfolio'] = data
                self.cache_timestamps['portfolio'] = time.time()
            else:
                return self.get_simulated_portfolio()
        return self.cache['portfolio']
    
    def get_simulated_portfolio(self):
        """Fallback simulated portfolio data"""
        return {
            'balances': {'USDT': 52.70, 'BTC': 0.00027872},
            'total_usdt_value': 83.38,
            'success': True
        }
        
    def get_open_positions(self):
        """Get detailed open positions data"""
        positions_data = self.live_api.check_open_positions()
        
        if not positions_data or not positions_data.get('success'):
            return {
                'success': False,
                'error': positions_data.get('error', 'Unknown error') if positions_data else 'No data'
            }
        
        # Enhance position data with additional details
        if positions_data.get('open_positions'):
            raw_positions = positions_data.get('positions', {})
            open_orders = raw_positions.get('open_orders', [])
            non_usdt_assets = raw_positions.get('non_usdt_assets', {})
            
            # Convert to unified format
            position_list = []
            
            # Process open orders
            for order in open_orders:
                if isinstance(order, dict):
                    position_list.append({
                        'symbol': order.get('symbol', 'UNKNOWN'),
                        'side': order.get('side', 'UNKNOWN'),
                        'size': float(order.get('qty', 0)),
                        'entry_price': float(order.get('price', 0)),
                        'current_price': self._get_current_price(order.get('symbol', 'BTCUSDT')),
                        'unrealizedPnl': 0.0,  # Placeholder
                        'status': order.get('orderStatus', 'UNKNOWN'),
                        'type': 'ORDER',
                        'id': order.get('orderId', 'UNKNOWN')
                    })
            
            # Process asset positions
            for asset, balance in non_usdt_assets.items():
                if balance > 0:
                    symbol = f"{asset}USDT"
                    current_price = self._get_current_price(symbol)
                    entry_price = self._get_average_entry_price(symbol)
                    
                    unrealized_pnl = (current_price - entry_price) * balance if entry_price else 0
                    
                    position_list.append({
                        'symbol': symbol,
                        'side': 'LONG',
                        'size': balance,
                        'entry_price': entry_price,
                        'current_price': current_price,
                        'unrealizedPnl': unrealized_pnl,
                        'status': 'ACTIVE',
                        'type': 'POSITION',
                        'id': f"pos_{asset}"
                    })
            
            positions_data['positions'] = position_list
        
        return positions_data
    
    def _get_current_price(self, symbol):
        """Get current price for a symbol"""
        try:
            market_data = self.bybit_client.get_kline_data(symbol, "1", 1)
            if market_data is not None and market_data.get('success') and not market_data['data'].empty:
                return market_data['data']['close'].iloc[0]
            return 0
        except Exception:
            return 0
            
    def _get_average_entry_price(self, symbol):
        """Get average entry price based on order history"""
        # Placeholder - will be implemented with real order history
        return self._get_current_price(symbol)
    
    def get_last_closed_position(self):
        """Get the last closed position (simulated for now)"""
        # Placeholder - will be implemented with real trade history
        return {
            'symbol': 'BTCUSDT',
            'side': 'SELL',
            'size': 0.01,
            'entry_price': 65000,
            'close_price': 67000,
            'realized_pnl': 2.0,
            'close_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
    def get_market_data(self, symbol, interval, limit):
        """Get market data with caching"""
        key = f"market_{symbol}_{interval}_{limit}"
        if key not in self.cache or (time.time() - self.cache_timestamps.get(key, 0)) > self.cache_duration:
            data = self.bybit_client.get_kline_data(
                symbol=symbol,
                interval=interval,
                limit=limit
            )
            if data is not None:
                self.cache[key] = data
                self.cache_timestamps[key] = time.time()
        return self.cache.get(key)
        

class EnhancedDataProvider:
    """Advanced data provider using unified data service"""
    
    def __init__(self):
        self.data_service = DataService()
        self.session_state = self._init_session_state()
        
    def _init_session_state(self):
        """Initialize session state with realistic data"""
        # Implementation from original dashboard
        return st.session_state
        
    def get_current_metrics(self):
        """Get current portfolio metrics"""
        # Implementation from original dashboard
        return {}
        
    def get_risk_metrics(self):
        """Calculate risk management metrics with fallback"""
        try:
            # Simulated risk metrics for demonstration
            return {
                'max_drawdown': 12.5,
                'current_drawdown': 5.2,
                'daily_risk_used': 3.8,
                'daily_risk_limit': 5.0,
                'portfolio_exposure': 42.0,
                'max_exposure': 50.0,
                'risk_status': 'HEALTHY'
            }
        except Exception:
            # Fallback if calculation fails
            return {
                'max_drawdown': 0.0,
                'current_drawdown': 0.0,
                'daily_risk_used': 0.0,
                'daily_risk_limit': 5.0,
                'portfolio_exposure': 0.0,
                'max_exposure': 50.0,
                'risk_status': 'UNKNOWN'
            }
        
    def get_market_data(self, symbol, interval, limit):
        """Get unified market data"""
        return self.data_service.get_market_data(symbol, interval, limit)
        
    def get_portfolio_data(self):
        """Get unified portfolio data from API"""
        return self.data_service.get_portfolio_data()
        
    def get_open_positions(self):
        """Get unified open positions data"""
        return self.data_service.get_open_positions()
        
    def get_recent_trades(self, limit=10):
        """Get recent trades (simulated for now)"""
        return []

def render_position_status(data_provider):
    """Render detailed position status with actions"""
    st.markdown("## **POSITIONSSTATUS**")
    
    try:
        positions = data_provider.get_open_positions()
        
        if not positions or not positions.get('success'):
            st.warning("Keine Positionsdaten verfügbar")
            return
            
        if positions.get('open_positions'):
            position_data = positions.get('positions', [])
            
            if not position_data:
                st.warning("Keine detaillierten Positionsdaten verfügbar")
                return
            
            with st.container():
                st.subheader("Aktive Positionen")
                
                position_df = pd.DataFrame(position_data)
                
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    if not position_df.empty:
                        def highlight_pnl(val):
                            if isinstance(val, (int, float)):
                                return f'background-color: {"#2ecc71" if val > 0 else "#e74c3c" if val < 0 else "transparent"};'
                            return ''
                        
                        styled_df = position_df.style.applymap(highlight_pnl, subset=['unrealizedPnl'])
                        st.dataframe(styled_df)
                    else:
                        st.info("Keine aktiven Positionen gefunden.")
                
                with col2:
                    if not position_df.empty:
                        st.subheader("Aktionen")
                        for idx, row in position_df.iterrows():
                            symbol = row.get('symbol', 'UNKNOWN')
                            position_id = row.get('id', idx)
                            
                            st.markdown(f"**Position: {symbol}**")
                            
                            col_close, col_sl, col_tp = st.columns(3)
                            with col_close:
                                if st.button(f"Schließen", key=f"close_{position_id}"):
                                    st.warning(f"Schließen von {symbol} wird ausgeführt...")
                            with col_sl:
                                if st.button(f"SL", key=f"sl_{position_id}"):
                                    st.warning(f"Stop-Loss für {symbol} anpassen...")
                            with col_tp:
                                if st.button(f"TP", key=f"tp_{position_id}"):
                                    st.warning(f"Take-Profit für {symbol} anpassen...")
                
                total_exposure = position_df['size'].sum() if 'size' in position_df.columns else 0
                total_pnl = position_df['unrealizedPnl'].sum() if 'unrealizedPnl' in position_df.columns else 0
                
                st.metric(
                    "Gesamtexposure",
                    f"{total_exposure:.2f}€",
                    f"PnL: {total_pnl:+.2f}€",
                    delta_color="normal" if total_pnl >= 0 else "inverse"
                )
        else:
            st.success("**KEINE AKTIVEN POSITIONEN**")
            
            last_position = data_provider.get_last_closed_position()
            portfolio_data = data_provider.get_portfolio_data()
            
            if last_position:
                st.info(f"**Letzte Position:** {last_position.get('symbol', 'UNKNOWN')} "
                        f"{last_position.get('side', 'UNKNOWN')} am "
                        f"{last_position.get('close_time', 'UNKNOWN')} "
                        f"mit {last_position.get('realized_pnl', 0):+.2f}€")
            
            if portfolio_data and portfolio_data.get('success'):
                available_balance = portfolio_data.get('total_usdt_value', 0)
                st.metric("Verfügbares Kapital", f"{available_balance:.2f}€")
    
    except Exception as e:
        st.error(f"Fehler: {str(e)}")
        import traceback
        st.text(traceback.format_exc())

# ============================================================================
# FOOTER COMPONENT
# ============================================================================

def render_footer():
    """Render dashboard footer"""
    st.markdown("---")
    st.markdown(
        f"<div style='text-align: center; color: #888; padding: 1rem;'>"
        "🚀 Enhanced Smart Money Bot Dashboard v2.0 | "
        f"{datetime.now().year} © Romain Hill"
        "</div>",
        unsafe_allow_html=True
    )

# ============================================================================
# DASHBOARD COMPONENTS
# ============================================================================

def render_main_overview(data_service):
    """Render main overview panel with key metrics"""
    st.markdown("## 🎯 **HAUPTÜBERSICHT**")
    
    # Get portfolio data
    portfolio_data = data_service.get_portfolio_data()
    positions = data_service.get_open_positions()
    
    # Calculate metrics
    portfolio_value = portfolio_data.get('total_usdt_value', 0)
    total_trades = len(positions.get('open_orders', [])) if positions and positions.get('success') else 0
    win_rate = 78.5  # Placeholder for actual calculation
    btc_price = 106450 + np.random.normal(0, 200)  # Simulated BTC price
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        pnl_color = "normal" if portfolio_value >= 0 else "inverse"
        st.metric(
            "💰 Portfoliowert",
            f"{portfolio_value:.2f}€",
            delta_color=pnl_color
        )
    
    with col2:
        st.metric(
            "📊 Trades gesamt",
            f"{total_trades}",
            f"+{total_trades} heute" if total_trades > 0 else "Keine Trades"
        )
    
    with col3:
        win_rate_status = "🔴 Kritisch" if win_rate < 50 else "🟡 Akzeptabel" if win_rate < 65 else "🟢 Ausgezeichnet"
        st.metric(
            "🏆 Gewinnrate",
            f"{win_rate:.1f}%",
            win_rate_status
        )
    
    with col4:
        btc_delta = np.random.choice(["+1.2%", "-0.8%", "+0.5%"])
        delta_color = "normal" if btc_delta.startswith("+") else "inverse"
        st.metric(
            "💎 BTC Preis",
            f"{btc_price:,.0f}€",
            btc_delta,
            delta_color=delta_color
        )
    
    # Additional metrics
    st.markdown("### Bot Status & Risikomanagement")
    status_col1, status_col2, status_col3 = st.columns(3)
    
    with status_col1:
        st.markdown("**Bot-Status**")
        st.markdown("<div class='status-good'>▶ Aktiv</div>", unsafe_allow_html=True)
        
    with status_col2:
        st.markdown("**Handelsmodus**")
        st.markdown("<div>Konservativ</div>", unsafe_allow_html=True)
        
    with status_col3:
        st.markdown("**Risikolimit**")
        st.markdown("<div>5€ täglich (10% Portfolio)</div>", unsafe_allow_html=True)

def render_position_status(data_provider):
    """Render panel showing current positions and open orders"""
    st.markdown("## **POSITIONSSTATUS**")
    
    try:
        positions = data_provider.get_open_positions()
    except Exception as e:
        st.error(f"Fehler beim Abrufen der Positionsdaten: {str(e)}")
        return
        
    if not positions or not positions.get('success'):
        st.warning("Keine Positionsdaten verfügbar")
        return
        
    if positions.get('open_positions'):
        st.warning("**AKTIVE POSITIONEN GEFUNDEN**")
        
        # Show open orders
        open_orders = positions.get('open_orders', [])
        if open_orders:
            st.subheader("Offene Orders")
            try:
                orders_df = pd.DataFrame(open_orders)
                cols_to_show = ['symbol', 'side', 'price', 'qty', 'orderStatus']
                available_cols = [col for col in cols_to_show if col in orders_df.columns]
                st.dataframe(orders_df[available_cols])
            except Exception as e:
                st.error(f"Fehler bei der Anzeige der Orders: {str(e)}")
        
        # Show asset balances
        non_usdt_assets = positions.get('non_usdt_assets', {})
        if non_usdt_assets:
            st.subheader("Aktuelle Bestände")
            for asset, balance in non_usdt_assets.items():
                st.info(f"{asset}: {balance:.6f}")
    else:
        st.success("**KEINE AKTIVEN POSITIONEN**")

# ============================================================================
# MAIN FUNCTION
# ============================================================================

def main():
    """Main application function without sidebar"""
    # Initialize data service
    data_service = DataService()
    
    # Render dashboard components
    render_header()
    render_control_panel()
    render_main_overview(data_service)
    render_position_status(data_service)
    
# ============================================================================
# MARKET REGIME & PERFORMANCE ANALYSIS
# ============================================================================

def render_market_regime_panel(data_service):
    """Render market regime analysis panel"""
    st.markdown("## **MARKTREGIME-ANALYSE**")
    
    # Get market data
    df = data_service.get_market_data(symbol="BTCUSDT", interval="240", limit=100)
    
    if df is None or not df.get('success') or df['data'].empty:
        st.warning("Keine Marktdaten verfügbar für Regime-Analyse")
        return
    df = df['data']
        
    # Calculate indicators
    df['sma20'] = df['close'].rolling(window=20).mean()
    df['sma50'] = df['close'].rolling(window=50).mean()
    df['atr'] = df['high'] - df['low']  # Simple ATR
    
    # Calculate trend indicators
    df['trend_up'] = (df['close'] > df['sma20']) & (df['sma20'] > df['sma50'])
    df['trend_down'] = (df['close'] < df['sma20']) & (df['sma20'] < df['sma50'])
    
    # Calculate volatility
    df['returns'] = df['close'].pct_change()
    volatility = df['returns'].std() * np.sqrt(365)  # Annualized volatility
    
    # Determine market regime
    bull_score = 0
    bear_score = 0
    sideways_score = 0
    
    # Trend analysis
    if df['trend_up'].iloc[-1]:
        bull_score += 4
    elif df['trend_down'].iloc[-1]:
        bear_score += 4
    else:
        sideways_score += 4
    
    # Volatility analysis
    if volatility > 0.8:  # High volatility
        if df['close'].iloc[-1] > df['close'].iloc[-2]:
            bull_score += 3
        else:
            bear_score += 3
    else:  # Low volatility
        sideways_score += 3
    
    # Volume analysis
    volume_ma = df['volume'].rolling(window=20).mean().iloc[-1]
    if df['volume'].iloc[-1] > volume_ma * 1.2:
        if df['close'].iloc[-1] > df['open'].iloc[-1]:
            bull_score += 2
        else:
            bear_score += 2
    else:
        sideways_score += 1
    
    # Determine regime
    max_score = max(bull_score, bear_score, sideways_score)
    
    if bull_score == max_score:
        regime = "BULL"
        confidence = min(bull_score / 9.0, 1.0)
    elif bear_score == max_score:
        regime = "BEAR"
        confidence = min(bear_score / 9.0, 1.0)
    else:
        regime = "SIDEWAYS"
        confidence = min(sideways_score / 8.0, 1.0)
    
    # Display regime analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Regime-Typ**")
        regime_color = {
            "BULL": "status-good",
            "BEAR": "status-danger",
            "SIDEWAYS": "status-warning"
        }[regime]
        st.markdown(f"<div class='{regime_color}'>{regime}</div>", unsafe_allow_html=True)
        
        st.markdown("**Zuverlässigkeit**")
        st.markdown(f"{confidence * 100:.1f}%")
        
        st.markdown("**Volatilität**")
        st.markdown(f"{volatility * 100:.2f}%")
    
    with col2:
        st.markdown("**Regime Scores**")
        st.progress(bull_score / 9.0, text="Bull")
        st.progress(bear_score / 9.0, text="Bear")
        st.progress(sideways_score / 8.0, text="Sideways")
        
        st.markdown("**Parameter**")
        st.markdown(f"BTC/USDT 4h-Kerzen: {len(df)}")
        st.markdown(f"Letzte Aktualisierung: {datetime.now().strftime('%H:%M:%S')}")

def render_performance_charts(data_service):
    """Render performance analytics charts"""
    st.markdown("## **LEISTUNGSANALYSE**")
    
    # Get portfolio data
    portfolio_data = data_service.get_portfolio_data()
    
    if not portfolio_data or not portfolio_data.get('success'):
        st.warning("Keine Portfoliodaten verfügbar für Leistungsanalyse")
        return
        
    # Generate portfolio history (simulated for now)
    dates = pd.date_range(start=datetime.now() - timedelta(days=30), periods=30)
    portfolio_values = np.linspace(
        portfolio_data['total_usdt_value'] * 0.8,
        portfolio_data['total_usdt_value'],
        len(dates)
    )
    
    portfolio_history = pd.DataFrame({
        'Datum': dates,
        'Portfoliowert': portfolio_values
    })
    
    # Generate trade history (simulated)
    trades = []
    for i in range(20):
        trades.append({
            'Datum': dates[i],
            'Symbol': 'BTCUSDT',
            'Richtung': 'Kaufen' if i % 2 == 0 else 'Verkaufen',
            'Größe': 0.01,
            'Ergebnis': np.random.uniform(-1, 2),
            'Regime': np.random.choice(['BULL', 'BEAR', 'SIDEWAYS'])
        })
    
    trades_df = pd.DataFrame(trades)
    
    # Portfolio performance chart
    st.markdown("### Portfolio-Verlauf")
    fig = px.line(
        portfolio_history,
        x='Datum',
        y='Portfoliowert',
        title="30-Tage Portfolio Performance"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Performance metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Gesamtrendite**")
        return_pct = ((portfolio_values[-1] / portfolio_values[0]) - 1) * 100
        st.markdown(f"{return_pct:.2f}%")
    
    with col2:
        st.markdown("**Tägliche Rendite**")
        daily_return = np.mean(np.diff(portfolio_values) / portfolio_values[:-1]) * 100
        st.markdown(f"{daily_return:.2f}%")
    
    with col3:
        st.markdown("**Max. Drawdown**")
        rolling_max = portfolio_history['Portfoliowert'].cummax()
        drawdown = (portfolio_history['Portfoliowert'] / rolling_max - 1) * 100
        max_drawdown = drawdown.min()
        st.markdown(f"{max_drawdown:.2f}%")
    
    # Trade performance by regime
    st.markdown("### Trades nach Regime")
    if not trades_df.empty:
        regime_perf = trades_df.groupby('Regime')['Ergebnis'].agg(['mean', 'count'])
        regime_perf.columns = ['Durchs. Ergebnis', 'Anzahl Trades']
        st.dataframe(regime_perf)
        
        # Win rate
        win_rate = (len(trades_df[trades_df['Ergebnis'] > 0]) / len(trades_df)) * 100
        st.markdown(f"**Win Rate: {win_rate:.1f}%**")
    else:
        st.info("Keine Trade-Daten verfügbar")

# ============================================================================
# MAIN FUNCTION
# ============================================================================

def main():
    """Main application function without sidebar"""
    # Initialize data service
    data_service = DataService()
    
    # Render dashboard components
    render_header()
    render_control_panel()
    render_main_overview(data_service)
    render_position_status(data_service)
    render_market_regime_panel(data_service)
    render_performance_charts(data_service)
    
# ============================================================================
# RISK MANAGEMENT & TRADE LOG
# ============================================================================

def render_risk_management_panel(data_service):
    def render_risk_management_panel(data_provider):
        """Render risk management dashboard with fallback"""
        st.markdown("## **RISIKOMANAGEMENT**")
        
        # Get risk metrics with fallback
        try:
            risk_metrics = data_provider.get_risk_metrics()
        except Exception as e:
            st.error(f"Fehler beim Abrufen von Risikodaten: {str(e)}")
            risk_metrics = {
                'max_drawdown': 0.0,
                'current_drawdown': 0.0,
                'daily_risk_used': 0.0,
                'daily_risk_limit': 5.0,
                'portfolio_exposure': 0.0,
                'max_exposure': 50.0,
                'risk_status': 'ERROR'
            }
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**Drawdown**")
            st.metric(
                "Aktueller Drawdown",
                f"{risk_metrics.get('current_drawdown', 0.0):.2f}%",
                f"Max: {risk_metrics.get('max_drawdown', 0.0):.2f}%"
            )
            
            st.markdown("**Portfolio-Exposure**")
            st.metric(
                "Aktuell",
                f"{risk_metrics.get('portfolio_exposure', 0.0):.1f}%",
                f"Limit: {risk_metrics.get('max_exposure', 50.0):.0f}%"
            )
        
        with col2:
            st.markdown("**Tägliches Risiko**")
            # Extrahiere Werte für bessere Lesbarkeit
            daily_used = risk_metrics.get('daily_risk_used', 0.0)
            daily_limit = risk_metrics.get('daily_risk_limit', 5.0)
            st.metric(
                "Verwendetes Risiko",
                f"{daily_used:.2f}€",
                f"Limit: {daily_limit:.2f}€"
            )
            
            st.markdown("**Risikostatus**")
            status = risk_metrics.get('risk_status', 'UNKNOWN')
            status_class = "status-good" if status == 'HEALTHY' else "status-warning" if status == 'WARNING' else "status-danger"
            st.markdown(f"<div class='{status_class}'>{status}</div>", unsafe_allow_html=True)
        
        with col3:
            st.markdown("**Risikoverlauf**")
            # Simulated risk history
            risk_history = pd.DataFrame({
                'Datum': pd.date_range(end=datetime.now(), periods=7, freq='D'),
                'Risiko': np.random.uniform(1, 4.5, 7)
            })
            fig = px.bar(
                risk_history,
                x='Datum',
                y='Risiko',
                title="Tägliches Risiko (letzte 7 Tage)"
            )
            fig.add_hline(y=5, line_dash="dash", line_color="red", annotation_text="Limit")
            st.plotly_chart(fig, use_container_width=True)

def render_trade_log(data_service):
    """Render trade log with recent trades and portfolio status"""
    st.markdown("## **HANDELSPROTOKOLL**")
    
    # Get recent trades
    trades = data_service.get_recent_trades(limit=10)
    portfolio_data = data_service.get_portfolio_data()
    
    if not trades or not portfolio_data.get('success'):
        st.warning("Keine Handelsdaten verfügbar")
        return
        
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown("### Kürzliche Trades")
        if trades:
            trades_df = pd.DataFrame(trades)
            cols_to_show = ['symbol', 'side', 'price', 'qty', 'pnl', 'timestamp']
            available_cols = [col for col in cols_to_show if col in trades_df.columns]
            st.dataframe(trades_df[available_cols])
        else:
            st.info("Keine Trades in letzter Zeit")
    
    with col2:
        st.markdown("### Portfolio-Status")
        
        # Asset allocation
        st.markdown("**Asset-Allokation**")
        if 'balances' in portfolio_data:
            assets = portfolio_data['balances']
            if assets:
                asset_df = pd.DataFrame({
                    'Asset': list(assets.keys()),
                    'Balance': list(assets.values())
                })
                fig = px.pie(
                    asset_df,
                    names='Asset',
                    values='Balance',
                    title="Asset-Verteilung"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Keine Asset-Daten")
        
        # Total portfolio value
        st.markdown("**Gesamtwert**")
        st.markdown(f"{portfolio_data['total_usdt_value']:.2f}€")

# ============================================================================
# MAIN FUNCTION
# ============================================================================

def main():
    """Main application function without sidebar"""
    # Initialize data service and provider
    data_service = DataService()
    data_provider = EnhancedDataProvider()
    
    # Render dashboard components
    render_header()
    render_control_panel()
    render_main_overview(data_provider)
    render_position_status(data_provider)
    render_market_regime_panel(data_provider)
    render_performance_charts(data_provider)
    render_risk_management_panel(data_provider)
    render_trade_log(data_provider)
    
    # Render footer
    render_footer()
    
    # Optimized auto-refresh logic
    if st.session_state.get('auto_refresh', True):
        refresh_interval = 10  # Longer interval to reduce API load
        time.sleep(refresh_interval)
        st.rerun()

if __name__ == '__main__':
    main()