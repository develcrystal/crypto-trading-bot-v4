"""
🚨 DASHBOARD TROUBLESHOOT & FIX
Behebt das Problem mit dem hängenden Launcher
"""

import sys
import os
import subprocess

def test_streamlit():
    """Test if streamlit works"""
    try:
        print("🧪 Testing Streamlit installation...")
        result = subprocess.run([sys.executable, "-c", "import streamlit; print('Streamlit version:', streamlit.__version__)"], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Streamlit installed:", result.stdout.strip())
            return True
        else:
            print("❌ Streamlit error:", result.stderr)
            return False
    except Exception as e:
        print(f"❌ Streamlit test failed: {e}")
        return False

def install_streamlit():
    """Install streamlit and dependencies"""
    print("📦 Installing Streamlit and dependencies...")
    packages = ["streamlit", "plotly", "pandas", "numpy"]
    
    for package in packages:
        print(f"Installing {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ {package} installed")
        except Exception as e:
            print(f"❌ {package} failed: {e}")

def test_dashboard_file():
    """Test if dashboard.py exists and is valid"""
    if os.path.exists("dashboard.py"):
        print("✅ dashboard.py found")
        
        # Test basic syntax
        try:
            with open("dashboard.py", 'r') as f:
                content = f.read()
            
            # Check if it has main components
            if "streamlit" in content and "def main" in content:
                print("✅ Dashboard file looks valid")
                return True
            else:
                print("⚠️ Dashboard file may have issues")
                return False
        except Exception as e:
            print(f"❌ Error reading dashboard file: {e}")
            return False
    else:
        print("❌ dashboard.py not found!")
        return False

def start_dashboard_direct():
    """Start dashboard directly without menu"""
    print("\n🚀 STARTING DASHBOARD DIRECTLY...")
    print("🌐 URL: http://localhost:8501")
    print("💡 This should open automatically in ~10 seconds")
    print("🛑 Press CTRL+C to stop")
    print("-" * 50)
    
    try:
        # Start streamlit directly
        subprocess.call([
            sys.executable, "-m", "streamlit", "run", 
            "dashboard.py",
            "--server.port", "8501"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")

def main():
    print("🚨 DASHBOARD TROUBLESHOOT & FIX")
    print("=" * 40)
    print("🔍 Diagnosing the hanging issue...")
    print()
    
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    print(f"📁 Working in: {script_dir}")
    
    # Test dashboard file
    if not test_dashboard_file():
        print("❌ Dashboard file problem detected!")
        return
    
    # Test streamlit
    if not test_streamlit():
        print("📦 Installing Streamlit...")
        install_streamlit()
        
        # Test again
        if not test_streamlit():
            print("❌ Streamlit installation failed!")
            return
    
    print("\n🎯 All checks passed! Starting dashboard...")
    start_dashboard_direct()

if __name__ == "__main__":
    main()
