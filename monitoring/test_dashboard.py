"""
🧪 QUICK DASHBOARD TEST
Testet das Dashboard schnell ohne Dependencies
"""

import sys
import os

def test_imports():
    """Test basic imports"""
    print("🧪 Testing Dashboard Components...")
    
    try:
        import pandas as pd
        print("✅ pandas: OK")
    except:
        print("❌ pandas: MISSING")
        return False
    
    try:
        import numpy as np
        print("✅ numpy: OK")
    except:
        print("❌ numpy: MISSING")
        return False
        
    try:
        import streamlit as st
        print("✅ streamlit: OK")
    except:
        print("❌ streamlit: MISSING - Installing...")
        os.system("pip install streamlit")
        
    try:
        import plotly
        print("✅ plotly: OK")
    except:
        print("❌ plotly: MISSING - Installing...")
        os.system("pip install plotly")
    
    return True

def test_dashboard_structure():
    """Test dashboard file structure"""
    print("\n📁 Testing File Structure...")
    
    required_files = [
        "dashboard.py",
        "data_processor.py", 
        "start_dashboard.py",
        "README.md"
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}: EXISTS")
        else:
            print(f"❌ {file}: MISSING")
            return False
    
    return True

def test_demo_data():
    """Test demo data generation"""
    print("\n📊 Testing Demo Data Generation...")
    
    try:
        from data_processor import MonitoringDataProcessor
        processor = MonitoringDataProcessor()
        
        # Test data methods
        portfolio_data = processor._get_mock_portfolio_data()
        print(f"✅ Portfolio Data: ${portfolio_data['portfolio_value']:,.2f}")
        
        trading_metrics = processor._get_mock_trading_metrics()
        print(f"✅ Trading Metrics: {trading_metrics['win_rate']:.1%} Win Rate")
        
        regime_data = processor._get_mock_regime_data()
        print(f"✅ Market Regime: {regime_data['current_regime']} ({regime_data['confidence']:.2f})")
        
        return True
        
    except Exception as e:
        print(f"❌ Demo Data Error: {e}")
        return False

def main():
    print("🚀 ENHANCED SMART MONEY BOT - DASHBOARD QUICK TEST")
    print("=" * 55)
    
    all_good = True
    
    # Test imports
    if not test_imports():
        all_good = False
    
    # Test structure
    if not test_dashboard_structure():
        all_good = False
    
    # Test demo data
    if not test_demo_data():
        all_good = False
    
    print("\n" + "=" * 55)
    
    if all_good:
        print("🎉 ALL TESTS PASSED! Dashboard ready to launch!")
        print("🚀 Run: python start_dashboard.py")
        print("🌐 Or double-click: START_DASHBOARD.bat")
    else:
        print("⚠️ Some tests failed. Check dependencies.")
        print("💡 Try: pip install streamlit plotly pandas numpy")

if __name__ == "__main__":
    main()
