"""
🚀 MONITORING DASHBOARD - ALL-IN-ONE LAUNCHER
Quick Version mit allen Optionen
"""

import os
import sys
import subprocess
import time

def print_header():
    print("🚀 ENHANCED SMART MONEY BOT V2")
    print("=" * 50)
    print("📊 Real-time Monitoring Dashboard")
    print("🚀 Quick Version - Ready to Launch!")
    print("=" * 50)

def show_menu():
    print("\n📋 LAUNCH OPTIONS:")
    print("1. 🚀 Quick Start (Auto-Browser)")
    print("2. 📊 Standard Start (Manual)")
    print("3. 🧪 Test Dashboard")
    print("4. 📖 Show Info")
    print("5. 🛠️ Install Dependencies")
    print("6. ❌ Exit")
    print("-" * 30)

def quick_start():
    """Launch dashboard with auto browser opening"""
    print("\n🚀 QUICK START - Auto Browser Opening...")
    os.system("python launch_browser.py")

def standard_start():
    """Standard streamlit launch"""
    print("\n📊 STANDARD START - Manual Browser...")
    print("🌐 Dashboard URL: http://localhost:8501")
    os.system("python start_dashboard.py")

def test_dashboard():
    """Run dashboard tests"""
    print("\n🧪 TESTING DASHBOARD...")
    os.system("python test_dashboard.py")

def show_info():
    """Show dashboard information"""
    print("\n📖 DASHBOARD INFORMATION")
    print("=" * 40)
    print("🎯 Features:")
    print("• Real-time Portfolio Monitoring")
    print("• Market Regime Detection (Bull/Bear/Sideways)")
    print("• Live Trading Signals & Filters")
    print("• Performance Analytics & Charts")
    print("• Risk Management Dashboard")
    print("• Trade History & Export")
    print("\n⚙️ Technical:")
    print("• Streamlit Web Interface")
    print("• Plotly Interactive Charts")
    print("• Auto-refresh every 5 seconds")
    print("• Mobile responsive design")
    print("• Live/Demo mode auto-detection")
    print("\n🔧 Controls:")
    print("• Auto-refresh toggle")
    print("• Emergency stop buttons")
    print("• Export functions (CSV/JSON)")
    print("• Filter options")
    print("\n🌐 Access: http://localhost:8501")

def install_dependencies():
    """Install required packages"""
    print("\n📦 INSTALLING DEPENDENCIES...")
    packages = [
        "streamlit",
        "plotly", 
        "pandas",
        "numpy"
    ]
    
    for package in packages:
        print(f"Installing {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ {package} installed")
        except:
            print(f"❌ {package} failed")
    
    print("🎉 Dependencies installation complete!")

def main():
    # Change to monitoring directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    print_header()
    
    while True:
        show_menu()
        
        try:
            choice = input("Select option (1-6): ").strip()
            
            if choice == "1":
                quick_start()
                break
            elif choice == "2":
                standard_start()
                break
            elif choice == "3":
                test_dashboard()
            elif choice == "4":
                show_info()
            elif choice == "5":
                install_dependencies()
            elif choice == "6":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please select 1-6.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
