"""
Advanced TradingView-Style Chart für das Crypto Trading Bot Dashboard.

Diese Komponente stellt einen fortschrittlichen Chart mit professionellen
Trading-Indikatoren wie Fair Value Gaps, Break of Structure und
Smart Money Concepts dar.
"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Füge Root-Verzeichnis zum Path hinzu für saubere Imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import der API-Client Klasse aus dem Core-Modul
from core.api_client import BybitAPIClient

class SmartMoneyChart:
    """
    Fortschrittliche Chart-Komponente mit Smart Money Konzepten,
    Fair Value Gaps, Break of Structure und weiteren professionellen
    Trading-Indikatoren.
    """
    
    def __init__(self, api_client=None, symbol="BTCUSDT", timeframe="5"):
        """Initialisiert die Chart-Komponente mit API-Client und Parametern."""
        self.api_client = api_client or BybitAPIClient()
        self.symbol = symbol
        self.timeframe = timeframe
        self.data = None
        
    def load_data(self, limit=500):
        """Lädt die Kerzendaten vom API-Client."""
        response = self.api_client.get_kline_data(
            symbol=self.symbol,
            interval=self.timeframe,
            limit=limit
        )
        
        if response['success']:
            self.data = response['data']
            return True
        else:
            st.error(f"Error loading chart data: {response.get('error', 'Unknown error')}")
            return False
    
    def _calculate_ema(self, period=20):
        """Berechnet EMA für die Daten."""
        if self.data is not None:
            self.data[f'ema_{period}'] = self.data['close'].ewm(span=period, adjust=False).mean()
    
    def _calculate_fair_value_gaps(self):
        """Identifiziert Fair Value Gaps in den Daten."""
        if self.data is None or len(self.data) < 3:
            return []
        
        fvgs = []
        
        # Bullish FVGs (wenn Kerze 1 Low > Kerze 3 High)
        for i in range(2, len(self.data)):
            if self.data.iloc[i-2]['low'] > self.data.iloc[i]['high']:
                fvgs.append({
                    'type': 'bullish',
                    'start_time': self.data.iloc[i-2]['timestamp'],
                    'end_time': self.data.iloc[i]['timestamp'],
                    'price_top': self.data.iloc[i-2]['low'],
                    'price_bottom': self.data.iloc[i]['high'],
                    'filled': False,
                    'index': i
                })
        
        # Bearish FVGs (wenn Kerze 1 High < Kerze 3 Low)
        for i in range(2, len(self.data)):
            if self.data.iloc[i-2]['high'] < self.data.iloc[i]['low']:
                fvgs.append({
                    'type': 'bearish',
                    'start_time': self.data.iloc[i-2]['timestamp'],
                    'end_time': self.data.iloc[i]['timestamp'],
                    'price_top': self.data.iloc[i]['low'],
                    'price_bottom': self.data.iloc[i-2]['high'],
                    'filled': False,
                    'index': i
                })
        
        return fvgs
    
    def _identify_structure_breaks(self):
        """Identifiziert Break of Structure (BOS) Punkte."""
        if self.data is None or len(self.data) < 20:
            return []
        
        bos_points = []
        
        # Berechne lokale Hochs und Tiefs (vereinfacht)
        highs = []
        lows = []
        
        window = 5  # Schau 5 Kerzen links und rechts
        
        for i in range(window, len(self.data) - window):
            try:
                # Ist dies ein lokales Hoch?
                is_high = all(self.data.iloc[i]['high'] > self.data.iloc[i-j]['high'] for j in range(1, window+1)) and \
                         all(self.data.iloc[i]['high'] > self.data.iloc[i+j]['high'] for j in range(1, window+1))
                
                if is_high:
                    highs.append({
                        'index': i,
                        'timestamp': self.data.iloc[i]['timestamp'],
                        'price': self.data.iloc[i]['high']
                    })
                
                # Ist dies ein lokales Tief?
                is_low = all(self.data.iloc[i]['low'] < self.data.iloc[i-j]['low'] for j in range(1, window+1)) and \
                        all(self.data.iloc[i]['low'] < self.data.iloc[i+j]['low'] for j in range(1, window+1))
                
                if is_low:
                    lows.append({
                        'index': i,
                        'timestamp': self.data.iloc[i]['timestamp'],
                        'price': self.data.iloc[i]['low']
                    })
            except (IndexError, KeyError):
                continue
        
        # Identifiziere Breaks (vereinfacht)
        for i in range(2, len(highs)):
            try:
                # Bullish BOS (niedrigeres Hoch gebrochen)
                if (len(highs) >= 3 and i >= 2 and 
                    highs[i-1]['price'] < highs[i-2]['price'] and 
                    highs[i]['price'] > highs[i-2]['price']):
                    bos_points.append({
                        'type': 'bullish',
                        'index': highs[i]['index'],
                        'timestamp': highs[i]['timestamp'],
                        'price': highs[i]['price']
                    })
            except (IndexError, KeyError):
                continue
        
        for i in range(2, len(lows)):
            try:
                # Bearish BOS (höheres Tief gebrochen)
                if (len(lows) >= 3 and i >= 2 and 
                    lows[i-1]['price'] > lows[i-2]['price'] and 
                    lows[i]['price'] < lows[i-2]['price']):
                    bos_points.append({
                        'type': 'bearish',
                        'index': lows[i]['index'],
                        'timestamp': lows[i]['timestamp'],
                        'price': lows[i]['price']
                    })
            except (IndexError, KeyError):
                continue
        
        return bos_points
    
    def _identify_change_of_character(self):
        """Identifiziert Change of Character / Channel Breaks."""
        if self.data is None or len(self.data) < 30:
            return []
        
        # Berechne Trends mit linearer Regression über 20 Perioden
        coc_points = []
        window = 20
        
        for i in range(window, len(self.data) - 5):
            try:
                # Berechne Trend der letzten 20 Kerzen
                x = np.arange(window)
                y = self.data.iloc[i-window:i]['close'].values
                
                # Lineare Regression
                if len(y) == window:
                    slope, _ = np.polyfit(x, y, 1)
                    
                    # Berechne Trend der nächsten 5 Kerzen
                    x_next = np.arange(5)
                    y_next = self.data.iloc[i:i+5]['close'].values
                    
                    if len(y_next) == 5:
                        slope_next, _ = np.polyfit(x_next, y_next, 1)
                        
                        # Change of Character wenn sich Steigung deutlich ändert
                        if (slope > 0 and slope_next < -0.001) or (slope < 0 and slope_next > 0.001):
                            if abs(slope_next - slope) > 0.001:  # Signifikante Änderung
                                coc_points.append({
                                    'type': 'bullish' if slope_next > slope else 'bearish',
                                    'index': i,
                                    'timestamp': self.data.iloc[i]['timestamp'],
                                    'price': self.data.iloc[i]['close']
                                })
            except (IndexError, KeyError, ValueError, np.linalg.LinAlgError):
                continue
        
        return coc_points
    
    def _identify_support_resistance(self):
        """Identifiziert wichtige Support- und Resistance-Levels."""
        if self.data is None or len(self.data) < 20:
            return []
        
        levels = []
        
        # Berechne Preishistogramm
        price_ranges = np.linspace(
            self.data['low'].min() * 0.99,
            self.data['high'].max() * 1.01,
            100
        )
        
        # Zähle, wie oft Preise in jedem Bereich waren
        hist, _ = np.histogram(
            np.concatenate([self.data['high'].values, self.data['low'].values]),
            bins=price_ranges
        )
        
        # Finde lokale Maxima im Histogramm (häufig getestete Levels)
        for i in range(1, len(hist) - 1):
            if hist[i] > hist[i-1] and hist[i] > hist[i+1] and hist[i] > np.mean(hist) * 1.5:
                level_price = (price_ranges[i] + price_ranges[i+1]) / 2
                
                # Bestimme Typ (Support oder Resistance)
                current_price = self.data.iloc[-1]['close']
                
                level_type = 'resistance' if level_price > current_price else 'support'
                
                # Stärke basierend auf Häufigkeit
                strength = min(hist[i] / np.mean(hist), 3)
                
                levels.append({
                    'price': level_price,
                    'type': level_type,
                    'strength': strength
                })
        
        return levels
    
    def render_chart(self, height=600, width=None):
        """Rendert den fortschrittlichen Trading-Chart."""
        if self.data is None:
            if not self.load_data():
                return None
        
        # Berechne Indikatoren
        self._calculate_ema(20)
        self._calculate_ema(50)
        
        fvgs = self._calculate_fair_value_gaps()
        bos_points = self._identify_structure_breaks()
        coc_points = self._identify_change_of_character()
        levels = self._identify_support_resistance()
        
        # Create subplot with volume
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.02,
            row_heights=[0.8, 0.2],
            subplot_titles=("", "Volume")
        )
        
        # Add candlestick chart
        fig.add_trace(
            go.Candlestick(
                x=self.data['timestamp'],
                open=self.data['open'],
                high=self.data['high'],
                low=self.data['low'],
                close=self.data['close'],
                name="BTCUSDT",
                increasing=dict(line=dict(color="#26A69A", width=1), fillcolor="#26A69A"),
                decreasing=dict(line=dict(color="#EF5350", width=1), fillcolor="#EF5350"),
            ),
            row=1, col=1
        )
        
        # Add EMA lines
        fig.add_trace(
            go.Scatter(
                x=self.data['timestamp'],
                y=self.data['ema_20'],
                name="EMA 20",
                line=dict(color='rgba(255, 255, 0, 0.7)', width=1)
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=self.data['timestamp'],
                y=self.data['ema_50'],
                name="EMA 50",
                line=dict(color='rgba(30, 144, 255, 0.7)', width=1)
            ),
            row=1, col=1
        )
        
        # Add volume chart
        colors = ['#26A69A' if close >= open else '#EF5350' for open, close 
                 in zip(self.data['open'], self.data['close'])]
        
        fig.add_trace(
            go.Bar(
                x=self.data['timestamp'],
                y=self.data['volume'],
                marker_color=colors,
                marker_line_width=0,
                name="Volume",
                opacity=0.8
            ),
            row=2, col=1
        )
        
        # Add Fair Value Gaps
        for fvg in fvgs:
            # Nur die letzten 10 FVGs anzeigen für bessere Übersicht
            if len(self.data) - fvg['index'] > 50:
                continue
                
            # Für jeden FVG zeichne ein Rechteck
            fig.add_shape(
                type="rect",
                x0=fvg['start_time'],
                x1=self.data.iloc[-1]['timestamp'],  # Bis zum Ende des Charts
                y0=fvg['price_bottom'],
                y1=fvg['price_top'],
                fillcolor="rgba(250, 0, 0, 0.2)" if fvg['type'] == 'bearish' else "rgba(0, 250, 0, 0.2)",
                opacity=0.5,
                line=dict(width=0),
                row=1, col=1
            )
            
            # Beschriftung für den FVG
            fig.add_annotation(
                x=fvg['start_time'],
                y=fvg['price_bottom'] if fvg['type'] == 'bullish' else fvg['price_top'],
                text="FVG" if fvg['type'] == 'bullish' else "FVG",
                showarrow=True,
                arrowhead=2,
                arrowcolor="green" if fvg['type'] == 'bullish' else "red",
                arrowsize=1,
                arrowwidth=1,
                ax=-30,
                ay=-30 if fvg['type'] == 'bullish' else 30,
                font=dict(size=8, color="white"),
                row=1, col=1
            )
        
        # Add Break of Structure Points
        for bos in bos_points:
            # Nur die letzten BOS-Punkte anzeigen
            if len(self.data) - bos['index'] > 50:
                continue
                
            fig.add_trace(
                go.Scatter(
                    x=[bos['timestamp']],
                    y=[bos['price']],
                    mode="markers+text",
                    marker=dict(
                        symbol="triangle-up" if bos['type'] == 'bullish' else "triangle-down",
                        size=12,
                        color="green" if bos['type'] == 'bullish' else "red",
                        line=dict(width=2, color="white")
                    ),
                    text=["BOS"],
                    textposition="top center" if bos['type'] == 'bullish' else "bottom center",
                    textfont=dict(size=10),
                    showlegend=False
                ),
                row=1, col=1
            )
        
        # Add Change of Character Points
        for coc in coc_points:
            # Nur die letzten CoC-Punkte anzeigen
            if len(self.data) - coc['index'] > 50:
                continue
                
            fig.add_trace(
                go.Scatter(
                    x=[coc['timestamp']],
                    y=[coc['price']],
                    mode="markers+text",
                    marker=dict(
                        symbol="circle",
                        size=10,
                        color="orange",
                        line=dict(width=2, color="white")
                    ),
                    text=["CoC"],
                    textposition="top center",
                    textfont=dict(size=10),
                    showlegend=False
                ),
                row=1, col=1
            )
        
        # Add Support/Resistance Levels
        for level in levels:
            # Nur die 5 stärksten Levels anzeigen
            if level['strength'] < 1.8:
                continue
                
            fig.add_shape(
                type="line",
                x0=self.data.iloc[0]['timestamp'],
                x1=self.data.iloc[-1]['timestamp'],
                y0=level['price'],
                y1=level['price'],
                line=dict(
                    color="blue" if level['type'] == 'support' else "red",
                    width=1,
                    dash="solid" if level['strength'] > 2 else "dash"
                ),
                opacity=min(level['strength'] * 0.3, 0.8),
                row=1, col=1
            )
        
        # Set layout
        fig.update_layout(
            title=f"{self.symbol} {self.timeframe}m - Smart Money Concepts Chart",
            xaxis_title="Time",
            yaxis_title="Price (USDT)",
            height=height,
            width=width,
            margin=dict(l=0, r=0, t=50, b=0),
            xaxis_rangeslider_visible=False,
            template="plotly_dark",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        # Styling für Volume Chart
        fig.update_yaxes(title_text="Volume", row=2, col=1)
        
        # Finales Styling
        fig.update_layout(
            plot_bgcolor='rgba(23, 23, 23, 1)',
            paper_bgcolor='rgba(23, 23, 23, 1)',
            font=dict(color='white'),
            xaxis=dict(
                showgrid=True,
                gridcolor='rgba(80, 80, 80, 0.2)'
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='rgba(80, 80, 80, 0.2)'
            )
        )
        
        return fig

# Beispiel für die Verwendung
def main():
    # Streamlit Setup
    st.set_page_config(page_title="Smart Money Chart", layout="wide")
    st.title("Smart Money Concepts Chart")
    
    # API-Client erstellen
    api_client = BybitAPIClient()
    
    # Chart erstellen
    chart = SmartMoneyChart(api_client=api_client, symbol="BTCUSDT", timeframe="5")
    fig = chart.render_chart(height=800)
    
    # Chart anzeigen
    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()