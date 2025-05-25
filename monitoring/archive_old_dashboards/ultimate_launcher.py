"""
🚀 ULTIMATE DASHBOARD LAUNCHER
All-in-One Lösung mit automatischer Conda-Erkennung
"""

import subprocess
import sys
import os
import time

class DashboardLauncher:
    def __init__(self):
        self.conda_env = "crypto-bot_V2"
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(self.script_dir)
    
    def print_header(self):
        print("🚀 ULTIMATE DASHBOARD LAUNCHER")
        print("=" * 45)
        print("🎯 Enhanced Smart Money Bot V2")
        print("📊 Real-time Monitoring Dashboard")
        print("🐍 Auto Conda Environment Detection")
        print("=" * 45)
    
    def check_conda(self):
        """Check if conda is available"""
        try:
            subprocess.run(['conda', '--version'], capture_output=True, check=True)
            print("✅ Conda found!")
            return True
        except:
            print("❌ Conda not found!")
            return False
    
    def check_environment(self):
        """Check if crypto-bot_V2 environment exists"""
        try:
            result = subprocess.run(['conda', 'env', 'list'], capture_output=True, text=True)
            if self.conda_env in result.stdout:
                print(f"✅ Environment '{self.conda_env}' found!")
                return True
            else:
                print(f"❌ Environment '{self.conda_env}' not found!")
                return False
        except:
            return False
    
    def create_environment(self):
        """Create conda environment"""
        print(f"📦 Creating environment '{self.conda_env}'...")
        try:
            subprocess.check_call(['conda', 'create', '-n', self.conda_env, 'python=3.10', '-y'])
            print("✅ Environment created!")
            return True
        except:
            print("❌ Environment creation failed!")
            return False
    
    def install_packages(self):
        """Install required packages"""
        print("📦 Installing packages...")
        
        # Install core packages via conda
        conda_cmd = ['conda', 'install', '-n', self.conda_env, 'pandas', 'numpy', '-y']
        try:
            subprocess.check_call(conda_cmd)
            print("✅ Conda packages installed!")
        except:
            print("⚠️ Conda packages installation failed!")
        
        # Install streamlit and plotly via pip
        pip_cmd = ['conda', 'run', '-n', self.conda_env, 'pip', 'install', 'streamlit', 'plotly']
        try:
            subprocess.check_call(pip_cmd)
            print("✅ Pip packages installed!")
            return True
        except:
            print("⚠️ Pip packages installation failed!")
            return False
    
    def test_installation(self):
        """Test if installation works"""
        print("🧪 Testing installation...")
        
        test_cmd = [
            'conda', 'run', '-n', self.conda_env, 'python', '-c',
            'import streamlit, plotly, pandas, numpy; print("✅ All packages working!")'
        ]
        
        try:
            result = subprocess.run(test_cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                print("✅ Package test successful!")
                return True
            else:
                print(f"❌ Package test failed: {result.stderr}")
                return False
        except:
            print("❌ Package test timed out or failed!")
            return False
    
    def start_dashboard_conda(self):
        """Start dashboard in conda environment"""
        print(f"\n🚀 Starting dashboard in {self.conda_env}...")
        print("🌐 URL: http://localhost:8501")
        print("💡 Press CTRL+C to stop")
        print("-" * 45)
        
        try:
            subprocess.call([
                'conda', 'run', '-n', self.conda_env,
                'streamlit', 'run', 'dashboard.py',
                '--server.port', '8501'
            ])
        except KeyboardInterrupt:
            print("\n🛑 Dashboard stopped!")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def start_dashboard_system(self):
        """Start dashboard with system Python"""
        print("\n🚀 Starting dashboard with system Python...")
        print("📦 Installing packages...")
        
        packages = ['streamlit', 'plotly', 'pandas', 'numpy']
        for package in packages:
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            except:
                print(f"⚠️ Failed to install {package}")
        
        print("🌐 URL: http://localhost:8501")
        print("💡 Press CTRL+C to stop")
        print("-" * 45)
        
        try:
            subprocess.call([
                sys.executable, '-m', 'streamlit', 'run', 'dashboard.py',
                '--server.port', '8501'
            ])
        except KeyboardInterrupt:
            print("\n🛑 Dashboard stopped!")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def show_menu(self):
        """Show launcher menu"""
        print("\n📋 LAUNCH OPTIONS:")
        print("1. 🐍 Auto Setup + Start (Conda)")
        print("2. 🚀 Quick Start (System Python)")
        print("3. 🔧 Setup Only (No Start)")
        print("4. 🧪 Test Environment")
        print("5. ❌ Exit")
        print("-" * 30)
    
    def run_setup_only(self):
        """Run setup without starting dashboard"""
        print("\n🔧 SETUP ONLY MODE")
        success = self.setup_conda_environment()
        if success:
            print("✅ Setup complete! Use option 1 to start dashboard.")
        else:
            print("❌ Setup failed! Check error messages above.")
    
    def test_environment_only(self):
        """Test environment without starting"""
        print("\n🧪 TESTING ENVIRONMENT")
        
        if not self.check_conda():
            print("❌ Conda not available!")
            return
        
        if not self.check_environment():
            print(f"❌ Environment {self.conda_env} not found!")
            return
        
        if self.test_installation():
            print("✅ Environment is ready!")
        else:
            print("❌ Environment has issues!")
    
    def setup_conda_environment(self):
        """Complete conda environment setup"""
        if not self.check_conda():
            print("❌ Conda not available! Using system Python instead.")
            return False
        
        if not self.check_environment():
            if not self.create_environment():
                return False
        
        if not self.install_packages():
            return False
        
        if not self.test_installation():
            print("⚠️ Installation test failed, but continuing...")
        
        return True
    
    def run(self):
        """Main launcher loop"""
        self.print_header()
        
        while True:
            self.show_menu()
            
            try:
                choice = input("Select option (1-5): ").strip()
                
                if choice == "1":
                    print("\n🐍 AUTO SETUP + START (CONDA)")
                    if self.setup_conda_environment():
                        self.start_dashboard_conda()
                    else:
                        print("❌ Conda setup failed! Trying system Python...")
                        self.start_dashboard_system()
                    break
                    
                elif choice == "2":
                    print("\n🚀 QUICK START (SYSTEM PYTHON)")
                    self.start_dashboard_system()
                    break
                    
                elif choice == "3":
                    self.run_setup_only()
                    
                elif choice == "4":
                    self.test_environment_only()
                    
                elif choice == "5":
                    print("👋 Goodbye!")
                    break
                    
                else:
                    print("❌ Invalid choice. Please select 1-5.")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

def main():
    launcher = DashboardLauncher()
    launcher.run()

if __name__ == "__main__":
    main()
