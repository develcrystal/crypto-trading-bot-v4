"""
🐍 CONDA-AWARE DASHBOARD LAUNCHER
Startet das Dashboard in der richtigen Conda-Umgebung
"""

import subprocess
import sys
import os
import time

def check_conda_env():
    """Check if crypto-bot_V2 conda environment exists"""
    try:
        result = subprocess.run(['conda', 'env', 'list'], capture_output=True, text=True)
        if 'crypto-bot_V2' in result.stdout:
            print("✅ Conda environment 'crypto-bot_V2' found!")
            return True
        else:
            print("❌ Conda environment 'crypto-bot_V2' not found!")
            return False
    except Exception as e:
        print(f"⚠️ Could not check conda environments: {e}")
        return False

def create_conda_env():
    """Create crypto-bot_V2 conda environment"""
    print("📦 Creating conda environment 'crypto-bot_V2'...")
    try:
        subprocess.check_call(['conda', 'create', '-n', 'crypto-bot_V2', 'python=3.10', '-y'])
        print("✅ Conda environment created successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to create conda environment: {e}")
        return False

def install_packages_conda():
    """Install packages in conda environment"""
    print("📦 Installing packages in crypto-bot_V2 environment...")
    
    # Install conda packages
    conda_packages = ['pandas', 'numpy']
    for package in conda_packages:
        try:
            subprocess.check_call(['conda', 'install', '-n', 'crypto-bot_V2', package, '-y'])
            print(f"✅ {package} installed via conda")
        except:
            print(f"⚠️ {package} installation failed")
    
    # Install pip packages
    pip_packages = ['streamlit', 'plotly']
    pip_commands = [
        ['conda', 'run', '-n', 'crypto-bot_V2', 'pip', 'install'] + pip_packages
    ]
    
    for cmd in pip_commands:
        try:
            subprocess.check_call(cmd)
            print("✅ Streamlit and Plotly installed via pip")
        except:
            print("⚠️ Pip packages installation failed")

def start_dashboard_conda():
    """Start dashboard in conda environment"""
    print("\n🚀 Starting dashboard in crypto-bot_V2 environment...")
    print("🌐 URL: http://localhost:8501")
    print("💡 Press CTRL+C to stop")
    print("-" * 50)
    
    try:
        # Start streamlit in conda environment
        subprocess.call([
            'conda', 'run', '-n', 'crypto-bot_V2',
            'streamlit', 'run', 'dashboard.py',
            '--server.port', '8501'
        ])
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")

def check_conda_installation():
    """Check if conda is installed"""
    try:
        subprocess.run(['conda', '--version'], capture_output=True, check=True)
        return True
    except:
        return False

def main():
    print("🐍 CONDA-AWARE MONITORING DASHBOARD")
    print("=" * 45)
    print("🎯 Target Environment: crypto-bot_V2")
    print()
    
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Check if conda is available
    if not check_conda_installation():
        print("❌ Conda not found! Please install Miniconda/Anaconda first.")
        print("📥 Download: https://docs.conda.io/en/latest/miniconda.html")
        input("Press Enter to exit...")
        return
    
    # Check if environment exists
    if not check_conda_env():
        print("🛠️ Creating conda environment...")
        if not create_conda_env():
            print("❌ Failed to create environment!")
            input("Press Enter to exit...")
            return
    
    # Install packages
    install_packages_conda()
    
    # Start dashboard
    start_dashboard_conda()

if __name__ == "__main__":
    main()
