"""
🚀 QUICK DASHBOARD STARTUP SCRIPT
Startet das Monitoring Dashboard mit einem Klick
"""

import subprocess
import sys
import os
import time

def install_requirements():
    """Install required packages"""
    try:
        print("📦 Installing required packages...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit", "plotly", "pandas", "numpy"])
        print("✅ Packages installed successfully!")
    except Exception as e:
        print(f"⚠️ Installation error: {e}")
        print("Continuing anyway...")

def start_dashboard():
    """Start the Streamlit dashboard"""
    try:
        print("\n🚀 Starting Enhanced Smart Money Monitoring Dashboard...")
        print("📊 Dashboard will open in your browser automatically!")
        print("🌐 URL: http://localhost:8501")
        print("\n" + "="*60)
        print("🎯 DASHBOARD FEATURES:")
        print("• Real-time Portfolio Monitoring")
        print("• Market Regime Detection")
        print("• Live Trading Signals")
        print("• Performance Analytics")
        print("• Risk Management")
        print("• Trade History")
        print("="*60)
        print("\n💡 Press CTRL+C to stop the dashboard")
        
        # Start Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "dashboard.py",
            "--server.port", "8501",
            "--server.headless", "false"
        ])
        
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")

def main():
    print("🚀 CRYPTO TRADING BOT V2 - MONITORING DASHBOARD")
    print("=" * 50)
    
    # Change to monitoring directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Install requirements
    install_requirements()
    
    # Start dashboard
    start_dashboard()

if __name__ == "__main__":
    main()
