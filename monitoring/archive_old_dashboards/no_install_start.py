"""
✅ NO-INSTALL DASHBOARD LAUNCHER  
Verwendet deine bestehende Umgebung OHNE Neuinstallation
"""

import subprocess
import sys
import os

def check_existing_environment():
    """Check if crypto-bot_V2 exists (no installation)"""
    try:
        result = subprocess.run(['conda', 'env', 'list'], capture_output=True, text=True)
        if 'crypto-bot_V2' in result.stdout:
            print("✅ crypto-bot_V2 environment found!")
            return True
        else:
            print("❌ crypto-bot_V2 environment NOT found!")
            print("💡 Please create it first or use a different launcher")
            return False
    except:
        print("❌ Conda not available!")
        return False

def test_existing_packages():
    """Test if required packages are already installed"""
    print("🧪 Testing existing packages...")
    
    test_cmd = [
        'conda', 'run', '-n', 'crypto-bot_V2', 'python', '-c',
        'import streamlit, plotly, pandas, numpy; print("✅ All packages available!")'
    ]
    
    try:
        result = subprocess.run(test_cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ All required packages found!")
            return True
        else:
            print("❌ Some packages missing!")
            print("💡 You may need to install streamlit and plotly")
            return False
    except:
        print("⚠️ Could not test packages")
        return True  # Continue anyway

def start_dashboard_no_install():
    """Start dashboard without any installation"""
    print("\n🚀 Starting dashboard with EXISTING setup...")
    print("🌐 URL: http://localhost:8501")
    print("💡 Press CTRL+C to stop")
    print("-" * 45)
    
    try:
        subprocess.call([
            'conda', 'run', '-n', 'crypto-bot_V2',
            'streamlit', 'run', 'dashboard.py',
            '--server.port', '8501'
        ])
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped!")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    print("✅ NO-INSTALL DASHBOARD LAUNCHER")
    print("=" * 40)
    print("🐍 Uses your EXISTING crypto-bot_V2 setup")
    print("📦 NO package installation!")
    print()
    
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Check environment exists
    if not check_existing_environment():
        print("\n❌ Environment not found!")
        input("Press Enter to exit...")
        return
    
    # Optional: Test packages
    test_existing_packages()
    
    # Start dashboard
    start_dashboard_no_install()

if __name__ == "__main__":
    main()
