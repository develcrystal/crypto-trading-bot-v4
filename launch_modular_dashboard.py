#!/usr/bin/env python3
"""
🚀 MODULAR DASHBOARD LAUNCHER
Launch the new modular Advanced Live Trading Dashboard

Features:
- Modular architecture with separate components
- Reduced file sizes and better maintainability  
- Professional trading interface
- Real-time data for MAINNET trading with $50 USDT
"""

import streamlit as st
import subprocess
import sys
import os
from pathlib import Path

def main():
    # Get the absolute path to the main dashboard
    dashboard_path = Path(__file__).parent / "ui" / "main_dashboard.py"
    
    print("🚀 LAUNCHING MODULAR ADVANCED LIVE TRADING DASHBOARD")
    print("=" * 60)
    print(f"📁 Dashboard Path: {dashboard_path}")
    print("🔴 MAINNET MODE - REAL $50.00 USDT!")
    print("💼 Professional Trading Interface")
    print("⚡ Modular Architecture - Optimized Performance")
    print("=" * 60)
    
    # Launch the Streamlit dashboard
    try:
        cmd = [
            sys.executable, "-m", "streamlit", "run", 
            str(dashboard_path),
            "--server.port", "8505",
            "--server.address", "localhost",
            "--theme.base", "dark",
            "--theme.primaryColor", "#e74c3c",
            "--theme.backgroundColor", "#0E1117",
            "--theme.secondaryBackgroundColor", "#1E1E1E"
        ]
        
        print("🎯 Starting dashboard on http://localhost:8505")
        print("📊 Loading modular components...")
        
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error launching dashboard: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Check if all dependencies are installed: pip install -r requirements.txt")
        print("2. Verify your .env file has correct API credentials")
        print("3. Ensure you're in the correct directory")

if __name__ == "__main__":
    main()
