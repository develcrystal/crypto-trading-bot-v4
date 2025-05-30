"""
Smart Money Chart Component für Enhanced Dashboard
Visualisierung von Fair Value Gaps (FVG) und Volume-Daten
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import sys
import os

# Pfad-Einrichtung für saubere Imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import der API-Client Klasse aus dem Core-Modul
try:
    from core.api_client import BybitAPI
except ImportError:
    # Fallback für den Fall, dass der Import fehlschlägt
    from corrected_live_api import LiveBybitAPI as BybitAPI


class SmartMoneyChart:
    """
    Smart Money Chart Komponente mit Fair Value Gaps und Volume-Visualisierung
    """
    
    def __init__(self, api_client=None):
        """Initialisiert die Chart-Komponente mit API-Client"""
        self.api_client = api_client or BybitAPI()
        
    def render(self, symbol='BTCUSDT', timeframe='5', limit=100, height=500):
        """
        Rendert das Smart Money Chart mit Fair Value Gaps
        
        Args:
            symbol: Trading Symbol (z.B. 'BTCUSDT')
            timeframe: Zeitintervall in Minuten (z.B. '5')
            limit: Anzahl der anzuzeigenden Kerzen
            height: Höhe des Charts in Pixeln
        
        Returns:
            None
        """
        st.markdown("## 📊 **SMART MONEY ANALYSE**")
        
        # UI-Elemente für Chart-Konfiguration
        col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
        
        with col1:
            selected_symbol = st.selectbox(
                "Symbol",
                options=["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT"],
                index=0,
                key="chart_symbol"
            )
        
        with col2:
            selected_timeframe = st.selectbox(
                "Zeitintervall",
                options=["1", "5", "15", "30", "60", "240"],
                index=1,
                key="chart_timeframe"
            )
        
        with col3:
            selected_limit = st.selectbox(
                "Kerzen",
                options=[50, 100, 200, 500],
                index=1,
                key="chart_limit"
            )
        
        with col4:
            st.markdown("**Aktiv:** Fair Value Gaps, Volume")
        
        # Lade Kerzendaten
        with st.spinner("Lade Chart-Daten..."):
            kline_data = self.api_client.get_kline_data(
                symbol=selected_symbol,
                interval=selected_timeframe,
                limit=selected_limit
            )
        
        if not kline_data.get('success'):
            st.error(f"Fehler beim Laden der Chart-Daten: {kline_data.get('error', 'Unbekannter Fehler')}")
            return
        
        # Daten aufbereiten
        df = kline_data['data']
        
        # Berechne Indikatoren
        self._calculate_indicators(df)
        
        # Finde Fair Value Gaps
        fvgs = self._identify_fair_value_gaps(df)
        
        # Chart erstellen
        fig = self._create_chart(df, fvgs, selected_symbol, selected_timeframe)
        
        # Chart anzeigen
        st.plotly_chart(fig, use_container_width=True)
        
        # Zusätzliche Informationen anzeigen
        self._display_chart_info(df, fvgs)
    
    def _calculate_indicators(self, df):
        """Berechnet technische Indikatoren für den DataFrame"""
        # EMAs berechnen
        df['ema_20'] = df['close'].ewm(span=20, adjust=False).mean()
        df['ema_50'] = df['close'].ewm(span=50, adjust=False).mean()
        
        # Volume MA berechnen
        df['volume_ma'] = df['volume'].rolling(window=20).mean()
        
        # Support/Resistance Levels (vereinfacht)
        df['support'] = df['low'].rolling(window=20).min()
        df['resistance'] = df['high'].rolling(window=20).max()
    
    def _identify_fair_value_gaps(self, df):
        """Identifiziert Fair Value Gaps (FVGs) in den Daten"""
        if len(df) < 3:
            return []
        
        fvgs = []
        
        # Bullish FVGs (Kerze 1 Low > Kerze 3 High)
        for i in range(2, len(df)):
            if df.iloc[i-2]['low'] > df.iloc[i]['high']:
                fvgs.append({
                    'type': 'bullish',
                    'start_index': i-2,
                    'end_index': i,
                    'start_time': df.iloc[i-2]['timestamp'],
                    'end_time': df.iloc[i]['timestamp'],
                    'top': df.iloc[i-2]['low'],
                    'bottom': df.iloc[i]['high'],
                    'mid_price': (df.iloc[i-2]['low'] + df.iloc[i]['high']) / 2
                })
        
        # Bearish FVGs (Kerze 1 High < Kerze 3 Low)
        for i in range(2, len(df)):
            if df.iloc[i-2]['high'] < df.iloc[i]['low']:
                fvgs.append({
                    'type': 'bearish',
                    'start_index': i-2,
                    'end_index': i,
                    'start_time': df.iloc[i-2]['timestamp'],
                    'end_time': df.iloc[i]['timestamp'],
                    'top': df.iloc[i]['low'],
                    'bottom': df.iloc[i-2]['high'],
                    'mid_price': (df.iloc[i]['low'] + df.iloc[i-2]['high']) / 2
                })
        
        return fvgs
    
    def _create_chart(self, df, fvgs, symbol, timeframe):
        """Erstellt das Chart mit Fair Value Gaps"""
        # Erstelle Subplot mit Volume
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.02,
            row_