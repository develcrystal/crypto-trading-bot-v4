#!/usr/bin/env python3
"""
🚀 ADVANCED LIVE TRADING DASHBOARD LAUNCHER
Professional launcher for production-ready trading dashboard
Version: 2.1 - Ready for 50€ Mainnet Deployment
"""

import os
import sys
import subprocess
import time
from pathlib import Path
import webbrowser
from dotenv import load_dotenv

def print_banner():
    """Display professional banner"""
    banner = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║     🚀 ADVANCED LIVE TRADING DASHBOARD LAUNCHER 🚀            ║
    ║                                                               ║
    ║     Professional Real-time Dashboard                          ║
    ║     Enhanced Smart Money Strategy                             ║
    ║     Production Ready for 50€ Mainnet Deployment              ║
    ║                                                               ║
    ║     Version: 2.1 - Professional Grade                        ║
    ║     © 2025 Advanced Trading Systems                           ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def check_environment():
    """Check Python environment and dependencies"""
    print("🔍 ENVIRONMENT CHECK")
    print("=" * 50)
    
    # Python version check
    python_version = sys.version_info
    print(f"🐍 Python Version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("❌ ERROR: Python 3.8+ required")
        return False
    else:
        print("✅ Python version OK")
    
    # Check critical packages
    required_packages = [
        'streamlit',
        'plotly', 
        'pandas',
        'numpy',
        'requests',
        'python-dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ MISSING PACKAGES: {', '.join(missing_packages)}")
        print("\n📦 INSTALL COMMAND:")
        print(f"pip install {' '.join(missing_packages)}")
        
        install_now = input("\n❓ Install missing packages now? (y/n): ").lower().strip()
        if install_now == 'y':
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
                print("\n✅ Packages installed successfully!")
                return True
            except subprocess.CalledProcessError:
                print("\n❌ Failed to install packages")
                return False
        else:
            return False
    
    print("\n✅ All dependencies satisfied")
    return True


def check_api_config():
    """Check API configuration"""
    print("\n🔧 API CONFIGURATION CHECK")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    api_key = os.getenv('BYBIT_API_KEY')
    api_secret = os.getenv('BYBIT_API_SECRET')
    testnet = os.getenv('TESTNET', 'true').lower()
    
    config_status = []
    
    if api_key:
        masked_key = api_key[:8] + "*" * (len(api_key) - 12) + api_key[-4:] if len(api_key) > 12 else "*" * len(api_key)
        print(f"✅ API Key: {masked_key}")
        config_status.append(True)
    else:
        print("❌ API Key: NOT SET")
        config_status.append(False)
    
    if api_secret:
        print("✅ API Secret: SET")
        config_status.append(True)
    else:
        print("❌ API Secret: NOT SET")
        config_status.append(False)
    
    # Environment check
    environment = "TESTNET" if testnet == 'true' else "MAINNET"
    env_color = "🟡" if environment == "TESTNET" else "🟢"
    print(f"{env_color} Environment: {environment}")
    
    if environment == "MAINNET":
        print("⚠️  WARNING: MAINNET MODE - Real money at risk!")
        confirm = input("   Continue with MAINNET? (yes/no): ").lower().strip()
        if confirm != 'yes':
            print("🛑 Switching to TESTNET for safety")
            os.environ['TESTNET'] = 'true'
    
    if not all(config_status):
        print("\n❌ API configuration incomplete!")
        print("\n📝 SETUP INSTRUCTIONS:")
        print("1. Create .env file in project root")
        print("2. Add the following lines:")
        print("   BYBIT_API_KEY=your_api_key_here")
        print("   BYBIT_API_SECRET=your_api_secret_here")
        print("   TESTNET=true")
        print("\n🔗 Get API keys: https://testnet.bybit.com (Testnet) or https://bybit.com (Mainnet)")
        return False
    
    print("\n✅ API configuration complete")
    return True


def check_project_structure():
    """Check project file structure"""
    print("\n📁 PROJECT STRUCTURE CHECK")
    print("=" * 50)
    
    current_dir = Path.cwd()
    print(f"📂 Current Directory: {current_dir}")
    
    # Check for dashboard files
    dashboard_files = [
        'advanced_live_dashboard_final.py',
        'advanced_dashboard_part1.py',
        'advanced_dashboard_part2.py', 
        'advanced_dashboard_part3.py',
        'advanced_dashboard_part4.py'
    ]
    
    missing_files = []
    
    for file in dashboard_files:
        if Path(file).exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - MISSING")
            missing_files.append(file)
    
    # Check components directory
    components_dir = Path('components')
    if components_dir.exists():
        print(f"✅ components/")
        
        component_files = [
            'live_widgets.py',
            'portfolio_monitor.py',
            'professional_charts.py',
            'trading_controls.py'
        ]
        
        for file in component_files:
            if (components_dir / file).exists():
                print(f"  ✅ {file}")
            else:
                print(f"  ⚠️ {file} - Optional component missing")
    else:
        print("⚠️ components/ - Directory missing (using built-in functions)")
    
    # Check static directory
    static_dir = Path('static')
    if static_dir.exists():
        print(f"✅ static/")
        if (static_dir / 'advanced_dashboard_styles.css').exists():
            print("  ✅ advanced_dashboard_styles.css")
        else:
            print("  ⚠️ CSS file missing (using fallback styles)")
    else:
        print("⚠️ static/ - Directory missing (using fallback styles)")
    
    if missing_files:
        print(f"\n❌ CRITICAL FILES MISSING: {', '.join(missing_files)}")
        return False
    
    print("\n✅ Project structure OK")
    return True


def get_dashboard_choice():
    """Get user choice for dashboard version"""
    print("\n🎯 DASHBOARD SELECTION")
    print("=" * 50)
    
    dashboards = {
        '1': {
            'name': 'Advanced Live Dashboard (Final)',
            'file': 'advanced_live_dashboard_final.py',
            'description': 'Complete integrated dashboard with all features'
        },
        '2': {
            'name': 'Bybit Focused Dashboard',
            'file': 'bybit_focused_dashboard.py', 
            'description': 'Simple focused dashboard for quick trading'
        },
        '3': {
            'name': 'Enhanced Dashboard',
            'file': 'enhanced_dashboard.py',
            'description': 'Enhanced version with advanced features'
        }
    }
    
    print("Available Dashboards:")
    for key, dashboard in dashboards.items():
        status = "✅" if Path(dashboard['file']).exists() else "❌"
        print(f"  {key}. {status} {dashboard['name']}")
        print(f"     📄 {dashboard['file']}")
        print(f"     📝 {dashboard['description']}")
        print()
    
    while True:
        choice = input("Select dashboard (1-3): ").strip()
        if choice in dashboards:
            selected = dashboards[choice]
            if Path(selected['file']).exists():
                return selected['file']
            else:
                print(f"❌ File {selected['file']} not found!")
        else:
            print("❌ Invalid choice. Please select 1, 2, or 3.")


def launch_dashboard(dashboard_file, port=8501):
    """Launch the selected dashboard"""
    print(f"\n🚀 LAUNCHING DASHBOARD")
    print("=" * 50)
    
    print(f"📄 Dashboard: {dashboard_file}")
    print(f"🌐 Port: {port}")
    print(f"🔗 URL: http://localhost:{port}")
    
    # Check if port is available
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    
    if result == 0:
        print(f"⚠️  Port {port} is already in use")
        port += 1
        print(f"🔄 Trying port {port}")
    
    print("\n🔥 Starting Streamlit server...")
    print("=" * 50)
    
    # Launch dashboard
    cmd = [
        sys.executable, '-m', 'streamlit', 'run',
        dashboard_file,
        '--server.port', str(port),
        '--server.headless', 'false',
        '--browser.gatherUsageStats', 'false',
        '--theme.base', 'dark'
    ]
    
    try:
        # Start process
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Wait a moment for server to start
        print("⏳ Waiting for server to start...")
        time.sleep(3)
        
        # Check if process is still running
        if process.poll() is None:
            print("✅ Dashboard server started successfully!")
            print(f"\n🌐 Opening browser: http://localhost:{port}")
            
            # Open browser
            try:
                webbrowser.open(f'http://localhost:{port}')
                print("✅ Browser opened")
            except Exception as e:
                print(f"⚠️  Could not open browser automatically: {e}")
                print(f"📖 Manually open: http://localhost:{port}")
            
            print("\n" + "=" * 60)
            print("🎉 DASHBOARD IS NOW RUNNING!")
            print("=" * 60)
            print("📊 Monitor your Enhanced Smart Money Strategy")
            print("💰 Ready for 50€ Mainnet Trading")
            print("🛑 Press Ctrl+C to stop the dashboard")
            print("=" * 60)
            
            # Wait for process to finish
            try:
                process.wait()
            except KeyboardInterrupt:
                print("\n\n🛑 Stopping dashboard...")
                process.terminate()
                print("✅ Dashboard stopped")
        
        else:
            # Process failed to start
            stdout, stderr = process.communicate()
            print("❌ Failed to start dashboard")
            print(f"Error: {stderr}")
            return False
    
    except Exception as e:
        print(f"❌ Launch error: {e}")
        return False
    
    return True


def main():
    """Main launcher function"""
    print_banner()
    
    # Environment check
    if not check_environment():
        print("\n❌ Environment check failed!")
        input("Press Enter to exit...")
        return
    
    # API configuration check
    if not check_api_config():
        print("\n❌ API configuration failed!")
        input("Press Enter to exit...")
        return
    
    # Project structure check
    if not check_project_structure():
        print("\n❌ Project structure check failed!")
        input("Press Enter to exit...")
        return
    
    # Dashboard selection
    try:
        dashboard_file = get_dashboard_choice()
        if not dashboard_file:
            print("❌ No dashboard selected")
            return
    except KeyboardInterrupt:
        print("\n🛑 Launch cancelled")
        return
    
    # Final confirmation
    print(f"\n🎯 READY TO LAUNCH")
    print("=" * 50)
    print(f"📄 Dashboard: {dashboard_file}")
    print("🌐 Server: Streamlit")
    print("💰 Ready for: 50€ Mainnet Deployment")
    print("🧠 Strategy: Enhanced Smart Money")
    
    confirm = input("\n🚀 Launch dashboard? (Y/n): ").lower().strip()
    if confirm in ['', 'y', 'yes']:
        launch_dashboard(dashboard_file)
    else:
        print("🛑 Launch cancelled")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Launcher interrupted")
    except Exception as e:
        print(f"\n❌ Launcher error: {e}")
    finally:
        input("\nPress Enter to exit...")
