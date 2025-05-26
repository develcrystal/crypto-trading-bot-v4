"""
Optimiertes Dark Mode Modul für das Crypto Trading Bot Dashboard.

Diese Datei stellt die CSS-Styles für Dark Mode und Light Mode bereit.
"""

def get_dark_mode_css():
    """Gibt optimiertes CSS für den Dark Mode zurück."""
    return """
    <style>
        /* Basis Dark Mode - weniger dunkel für bessere Lesbarkeit */
        .stApp {
            background-color: #1a202c;  /* Helleres Dunkelblau */
            color: #f7fafc;  /* Helleres Weiß für Text */
        }
        
        /* Header-Styling */
        .main-header {
            background: linear-gradient(90deg, #2a4365 0%, #2c5282 100%);
            border: 1px solid #3182ce;
            box-shadow: 0 4px 12px rgba(49, 130, 206, 0.4);
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 25px;
            position: relative;
            overflow: hidden;
        }
        
        .main-header::before {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, #4299e1, #38b2ac, #f6ad55);
            z-index: 1;
        }
        
        .main-header h1 {
            color: #f7fafc;
            font-weight: 700;
            margin: 0;
            font-size: 2.2rem;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        }
        
        .main-header h2 {
            color: #fed7d7;
            font-size: 1.6rem;
            margin-top: 5px;
            text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
        }
        
        /* Warning Banner */
        .mainnet-warning {
            background: linear-gradient(90deg, #c53030, #e53e3e);
            color: #fff5f5;
            border-radius: 6px;
            padding: 10px 15px;
            font-weight: 600;
            margin: 10px 0;
            text-align: center;
            animation: pulse 2s infinite;
            box-shadow: 0 2px 8px rgba(229, 62, 62, 0.4);
            border: 1px solid #fc8181;
        }
        
        /* Live Indicator */
        .live-indicator { 
            animation: pulse 1.5s infinite;
            color: #38b2ac;
            font-weight: 700;
            font-size: 18px;
            text-shadow: 0 0 8px rgba(56, 178, 172, 0.6);
        }
        
        /* Danger Indicator */
        .danger-indicator {
            animation: pulse 1s infinite;
            color: #f56565;
            font-weight: 700;
            text-shadow: 0 0 8px rgba(245, 101, 101, 0.6);
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.7; }
            100% { opacity: 1; }
        }
        
        /* Widgets und Karten */
        .metric-container {
            background: #2d3748;
            border-radius: 8px;
            padding: 15px;
            border-left: 4px solid #4299e1;
            margin: 10px 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        /* Price Widget mit modernem Glasmorphism - heller und lesbarer */
        .price-widget {
            background: rgba(45, 55, 72, 0.85);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(66, 153, 225, 0.3);
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
            position: relative;
            overflow: hidden;
        }
        
        .price-widget::before {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(135deg, rgba(66, 153, 225, 0.1), rgba(56, 178, 172, 0.1));
            z-index: -1;
        }
        
        .price-widget h1 {
            font-size: 3.5rem;
            margin: 0;
            background: linear-gradient(90deg, #4299e1, #38b2ac);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        }
        
        /* Order Book - heller für bessere Lesbarkeit */
        .order-book {
            font-family: 'JetBrains Mono', 'Fira Code', monospace;
            font-size: 12px;
            background-color: #2d3748;
            border-radius: 8px;
            border: 1px solid #4a5568;
            padding: 15px;
        }
        
        .buy-price { 
            color: #38b2ac; 
            font-weight: 700; 
            text-shadow: 0 0 5px rgba(56, 178, 172, 0.3);
        }
        
        .sell-price { 
            color: #f56565; 
            font-weight: 700; 
            text-shadow: 0 0 5px rgba(245, 101, 101, 0.3);
        }
        
        /* Trading Controls - heller für bessere Lesbarkeit */
        .trading-control {
            background: #2d3748;
            color: #f7fafc;
            border-radius: 8px;
            padding: 18px;
            margin: 12px 0;
            border: 1px solid #4a5568;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .trading-control h4 {
            color: #63b3ed;
            margin-top: 0;
            border-bottom: 1px solid #4a5568;
            padding-bottom: 8px;
        }
        
        /* Buttons */
        .emergency-button {
            background: linear-gradient(to right, #e53e3e, #c53030) !important;
            color: white !important;
            font-weight: 700 !important;
            border: none !important;
            padding: 12px 24px !important;
            border-radius: 6px !important;
            box-shadow: 0 4px 6px rgba(229, 62, 62, 0.4) !important;
            transition: all 0.3s ease !important;
        }
        
        .emergency-button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 8px rgba(229, 62, 62, 0.5) !important;
        }
        
        .success-button {
            background: linear-gradient(to right, #2f855a, #38b2ac) !important;
            color: white !important;
            font-weight: 700 !important;
            border: none !important;
            border-radius: 6px !important;
            box-shadow: 0 4px 6px rgba(47, 133, 90, 0.4) !important;
            transition: all 0.3s ease !important;
        }
        
        .success-button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 8px rgba(47, 133, 90, 0.5) !important;
        }
        
        /* Streamlit Elements Optimierung - heller und lesbarer */
        div.stButton > button {
            background-color: #4a5568;
            color: #f7fafc;
            border: 1px solid #718096;
            border-radius: 6px;
            padding: 0.5rem 1rem;
            font-weight: 500;
            transition: all 0.2s ease;
        }
        
        div.stButton > button:hover {
            background-color: #2b6cb0;
            border-color: #63b3ed;
            transform: translateY(-1px);
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
        }
        
        .stTextInput > div > div > input {
            background-color: #2d3748;
            color: #f7fafc;
            border: 1px solid #4a5568;
            border-radius: 6px;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: #63b3ed;
            box-shadow: 0 0 0 1px #63b3ed;
        }
        
        .stCheckbox > div > label > div[role="checkbox"] {
            background-color: #2d3748 !important;
            border: 1px solid #4a5568 !important;
        }
        
        .stSelectbox > div > div > div {
            background-color: #2d3748;
            color: #f7fafc;
            border: 1px solid #4a5568;
            border-radius: 6px;
        }
        
        /* Alerts */
        .stAlert {
            background-color: #2d3748;
            color: #f7fafc;
            border: 1px solid #4a5568;
            border-radius: 6px;
        }
        
        /* Info Alert */
        .stAlert[data-baseweb="notification"] {
            background-color: rgba(66, 153, 225, 0.2);
            border-left: 4px solid #4299e1;
        }
        
        /* Success Alert */
        .stAlert[data-baseweb="notification"][data-testid="stNotificationSuccess"] {
            background-color: rgba(47, 133, 90, 0.2);
            border-left: 4px solid #38b2ac;
        }
        
        /* Warning Alert */
        .stAlert[data-baseweb="notification"][data-testid="stNotificationWarning"] {
            background-color: rgba(237, 137, 54, 0.2);
            border-left: 4px solid #ed8936;
        }
        
        /* Error Alert */
        .stAlert[data-baseweb="notification"][data-testid="stNotificationError"] {
            background-color: rgba(229, 62, 62, 0.2);
            border-left: 4px solid #f56565;
        }
        
        /* Tabellen - heller für bessere Lesbarkeit */
        .stDataFrame {
            background-color: #2d3748;
            border-radius: 8px;
            overflow: hidden;
        }
        
        .stDataFrame table {
            background-color: #2d3748;
            border-collapse: separate;
            border-spacing: 0;
        }
        
        .stDataFrame th {
            background-color: #4a5568;
            color: #f7fafc !important;
            font-weight: 600;
            padding: 10px;
            border-bottom: 2px solid #718096;
            text-transform: uppercase;
            font-size: 0.8rem;
        }
        
        .stDataFrame td {
            background-color: #2d3748;
            color: #f7fafc !important;
            padding: 10px;
            border-bottom: 1px solid #4a5568;
        }
        
        .stDataFrame tr:hover td {
            background-color: #4a5568;
        }
        
        /* Expander */
        .stExpander {
            background-color: #2d3748;
            border: 1px solid #4a5568;
            border-radius: 8px;
            overflow: hidden;
        }
        
        .stExpander > details > summary {
            background-color: #4a5568;
            padding: 10px 15px;
            border-bottom: 1px solid #718096;
        }
        
        .stExpander > details > summary:hover {
            background-color: #2c5282;
        }
        
        .stExpander > details > summary > span {
            color: #f7fafc;
            font-weight: 600;
        }
        
        /* Sidebar */
        .css-6qob1r {
            background-color: #2d3748;
            border-right: 1px solid #4a5568;
        }
        
        /* Markdown */
        .stMarkdown {
            color: #f7fafc;
        }
        
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {
            color: #f7fafc;
        }
        
        .stMarkdown a {
            color: #63b3ed;
            text-decoration: none;
        }
        
        .stMarkdown a:hover {
            text-decoration: underline;
        }
        
        .stMarkdown strong {
            color: #f7fafc;
            font-weight: 600;
        }
        
        .stMarkdown code {
            background-color: #4a5568;
            color: #f7fafc;
            padding: 2px 5px;
            border-radius: 4px;
            font-family: 'JetBrains Mono', monospace;
        }
        
        /* Metrics */
        .stMetric {
            background-color: #4a5568;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        /* Dark Mode Toggle */
        .dark-mode-toggle {
            background: linear-gradient(to right, #4299e1, #63b3ed) !important;
            color: white !important;
            border: none !important;
            border-radius: 25px !important;
            padding: 5px 15px !important;
            font-weight: 600 !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            gap: 8px !important;
            box-shadow: 0 2px 8px rgba(66, 153, 225, 0.4) !important;
            transition: all 0.3s ease !important;
        }
        
        .dark-mode-toggle:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 12px rgba(66, 153, 225, 0.5) !important;
        }
        
        /* Charts - hellerer Hintergrund für bessere Lesbarkeit */
        .js-plotly-plot .plotly .main-svg {
            background-color: #2d3748 !important;
        }
        
        .js-plotly-plot .plotly .bg {
            fill: #2d3748 !important;
        }
        
        .js-plotly-plot .plotly .xaxis .xtick text,
        .js-plotly-plot .plotly .yaxis .ytick text {
            fill: #f7fafc !important;
        }
        
        .js-plotly-plot .plotly .xaxis .xtick line,
        .js-plotly-plot .plotly .yaxis .ytick line {
            stroke: #718096 !important;
        }
        
        .js-plotly-plot .plotly .xaxis path,
        .js-plotly-plot .plotly .yaxis path {
            stroke: #718096 !important;
        }
        
        .js-plotly-plot .plotly .xgrid, 
        .js-plotly-plot .plotly .ygrid {
            stroke: #4a5568 !important;
        }
        
        .js-plotly-plot .plotly .annotation-text {
            fill: #f7fafc !important;
        }
        
        .js-plotly-plot .plotly .hoverlayer .hover {
            fill: #4a5568 !important;
            stroke: #4299e1 !important;
        }
        
        /* FVG Highlights in Chart */
        .bullish-fvg {
            background-color: rgba(56, 178, 172, 0.2) !important;
            border: 1px solid rgba(56, 178, 172, 0.5) !important;
        }
        
        .bearish-fvg {
            background-color: rgba(245, 101, 101, 0.2) !important;
            border: 1px solid rgba(245, 101, 101, 0.5) !important;
        }
        
        /* Scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: #4a5568;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #718096;
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: #63b3ed;
        }
    </style>
    """

def get_light_mode_css():
    """Gibt CSS für den Light Mode zurück."""
    return """
    <style>
        /* Basis Light Mode */
        .stApp {
            background-color: #f8fafc;
            color: #1e293b;
        }
        
        /* Header-Styling */
        .main-header {
            background: linear-gradient(90deg, #0369a1 0%, #0284c7 100%);
            border: 1px solid #0ea5e9;
            box-shadow: 0 4px 12px rgba(3, 105, 161, 0.3);
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 25px;
            position: relative;
            overflow: hidden;
        }
        
        .main-header::before {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, #f59e0b, #10b981, #3b82f6);
            z-index: 1;
        }
        
        .main-header h1 {
            color: white;
            font-weight: 700;
            margin: 0;
            font-size: 2.2rem;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        }
        
        .main-header h2 {
            color: #fef2f2;
            font-size: 1.6rem;
            margin-top: 5px;
            text-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
        }
        
        /* Warning Banner */
        .mainnet-warning {
            background: linear-gradient(90deg, #dc2626, #b91c1c);
            color: white;
            border-radius: 6px;
            padding: 10px 15px;
            font-weight: 600;
            margin: 10px 0;
            text-align: center;
            animation: pulse 2s infinite;
            box-shadow: 0 2px 8px rgba(220, 38, 38, 0.4);
            border: 1px solid #ef4444;
        }
        
        /* Live Indicator */
        .live-indicator { 
            animation: pulse 1.5s infinite;
            color: #059669;
            font-weight: 700;
            font-size: 18px;
            text-shadow: 0 0 8px rgba(5, 150, 105, 0.3);
        }
        
        /* Rest des Light Mode CSS... */
        
        /* Wichtige Komponenten fürs Chart */
        .js-plotly-plot .plotly .main-svg {
            background-color: #f8fafc !important;
        }
        
        .js-plotly-plot .plotly .bg {
            fill: #f8fafc !important;
        }
        
        .js-plotly-plot .plotly .xaxis .xtick text,
        .js-plotly-plot .plotly .yaxis .ytick text {
            fill: #1e293b !important;
        }
    </style>
    """
