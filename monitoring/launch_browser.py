"""
🌐 BROWSER DASHBOARD LAUNCHER
Startet Dashboard und öffnet Browser automatisch
"""

import subprocess
import sys
import time
import webbrowser
import threading
import os

def check_streamlit():
    """Check if streamlit is installed"""
    try:
        import streamlit
        return True
    except ImportError:
        print("📦 Installing Streamlit...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit", "plotly"])
        return True

def start_streamlit():
    """Start streamlit in background"""
    try:
        subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", 
            "dashboard.py",
            "--server.port", "8501",
            "--server.headless", "true",
            "--server.runOnSave", "true"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"Error starting Streamlit: {e}")

def open_browser():
    """Open browser after delay"""
    time.sleep(3)  # Wait for Streamlit to start
    print("🌐 Opening browser...")
    webbrowser.open("http://localhost:8501")

def main():
    print("🚀 ENHANCED SMART MONEY BOT - DASHBOARD LAUNCHER")
    print("=" * 50)
    
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Check dependencies
    if not check_streamlit():
        print("❌ Failed to install dependencies")
        return
    
    print("🚀 Starting dashboard...")
    print("📊 This will open in your browser automatically!")
    
    # Start Streamlit in background
    start_streamlit()
    
    # Open browser after delay
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.start()
    
    print("✅ Dashboard starting...")
    print("🌐 URL: http://localhost:8501")
    print("💡 Press CTRL+C to stop")
    
    try:
        # Keep script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped by user")

if __name__ == "__main__":
    main()
