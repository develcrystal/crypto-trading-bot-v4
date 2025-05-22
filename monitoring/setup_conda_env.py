"""
🔧 CONDA ENVIRONMENT SETUP & VALIDATOR
Prüft und konfiguriert die crypto-bot_V2 Umgebung
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Run command and return success status"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            print(f"✅ {description} - SUCCESS")
            return True, result.stdout
        else:
            print(f"❌ {description} - FAILED")
            print(f"Error: {result.stderr}")
            return False, result.stderr
    except Exception as e:
        print(f"❌ {description} - EXCEPTION: {e}")
        return False, str(e)

def check_conda_environments():
    """List all conda environments"""
    print("🔍 Checking available conda environments...")
    success, output = run_command("conda env list", "Listing environments")
    
    if success:
        environments = []
        for line in output.split('\n'):
            if 'crypto-bot' in line.lower():
                env_name = line.split()[0]
                environments.append(env_name)
                print(f"📦 Found crypto environment: {env_name}")
        return environments
    return []

def validate_environment(env_name):
    """Validate specific environment"""
    print(f"\n🧪 Validating environment: {env_name}")
    
    # Check if environment exists and is accessible
    cmd = f"conda run -n {env_name} python --version"
    success, output = run_command(cmd, f"Testing {env_name} Python")
    
    if success:
        print(f"🐍 Python version in {env_name}: {output.strip()}")
        
        # Check key packages
        packages_to_check = [
            ("pandas", "import pandas; print(f'pandas: {pandas.__version__}')"),
            ("numpy", "import numpy; print(f'numpy: {numpy.__version__}')"),
            ("streamlit", "import streamlit; print(f'streamlit: {streamlit.__version__}')"),
            ("plotly", "import plotly; print(f'plotly: {plotly.__version__}')")
        ]
        
        missing_packages = []
        for package_name, test_code in packages_to_check:
            cmd = f'conda run -n {env_name} python -c "{test_code}"'
            success, output = run_command(cmd, f"Checking {package_name}")
            
            if success:
                print(f"✅ {output.strip()}")
            else:
                missing_packages.append(package_name)
                print(f"❌ {package_name} missing or error")
        
        return len(missing_packages) == 0, missing_packages
    
    return False, ["Python not accessible"]

def install_missing_packages(env_name, missing_packages):
    """Install missing packages in environment"""
    print(f"\n📦 Installing missing packages in {env_name}...")
    
    # Separate conda and pip packages
    conda_packages = ['pandas', 'numpy']
    pip_packages = ['streamlit', 'plotly']
    
    # Install conda packages
    conda_missing = [pkg for pkg in missing_packages if pkg in conda_packages]
    if conda_missing:
        cmd = f"conda install -n {env_name} {' '.join(conda_missing)} -y"
        run_command(cmd, f"Installing conda packages: {', '.join(conda_missing)}")
    
    # Install pip packages
    pip_missing = [pkg for pkg in missing_packages if pkg in pip_packages]
    if pip_missing:
        cmd = f"conda run -n {env_name} pip install {' '.join(pip_missing)}"
        run_command(cmd, f"Installing pip packages: {', '.join(pip_missing)}")

def test_dashboard_import(env_name):
    """Test if dashboard can be imported"""
    print(f"\n🧪 Testing dashboard import in {env_name}...")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dashboard_path = os.path.join(script_dir, "dashboard.py")
    
    # Test basic import
    test_code = '''
import sys
sys.path.append(r"''' + script_dir + '''")
try:
    import dashboard
    print("✅ Dashboard import successful")
except Exception as e:
    print(f"❌ Dashboard import failed: {e}")
'''
    
    cmd = f'conda run -n {env_name} python -c "{test_code}"'
    run_command(cmd, "Testing dashboard import")

def create_conda_start_script(env_name):
    """Create optimized start script for the environment"""
    script_content = f'''@echo off
echo 🐍 Starting Dashboard in {env_name} environment...
call conda activate {env_name}
if errorlevel 1 (
    echo ❌ Failed to activate {env_name}
    pause
    exit /b 1
)

echo ✅ Environment activated: {env_name}
echo 🚀 Starting dashboard...
streamlit run dashboard.py --server.port 8501

call conda deactivate
'''
    
    with open(f"START_{env_name.upper()}.bat", 'w') as f:
        f.write(script_content)
    
    print(f"✅ Created START_{env_name.upper()}.bat")

def main():
    print("🔧 CONDA ENVIRONMENT SETUP & VALIDATOR")
    print("=" * 45)
    print("🎯 Target: crypto-bot_V2 environment")
    print()
    
    # Check available environments
    envs = check_conda_environments()
    
    target_env = "crypto-bot_V2"
    if target_env not in envs:
        print(f"\n❌ Target environment '{target_env}' not found!")
        print("🛠️ Available crypto environments:", envs)
        
        if envs:
            print(f"💡 Using first available: {envs[0]}")
            target_env = envs[0]
        else:
            print("❌ No crypto environments found!")
            print("📦 Please create environment first:")
            print(f"   conda create -n {target_env} python=3.10 -y")
            return
    
    print(f"\n🎯 Validating environment: {target_env}")
    
    # Validate environment
    is_valid, missing = validate_environment(target_env)
    
    if not is_valid:
        print(f"\n🛠️ Environment needs setup. Missing: {missing}")
        install_missing_packages(target_env, missing)
        
        # Re-validate after installation
        print("\n🔄 Re-validating after installation...")
        is_valid, missing = validate_environment(target_env)
    
    if is_valid:
        print(f"\n✅ Environment {target_env} is ready!")
        
        # Test dashboard import
        test_dashboard_import(target_env)
        
        # Create optimized start script
        create_conda_start_script(target_env)
        
        print(f"\n🚀 Ready to launch dashboard!")
        print(f"📝 Use: START_{target_env.upper()}.bat")
        print(f"🌐 URL: http://localhost:8501")
        
    else:
        print(f"\n❌ Environment {target_env} still has issues: {missing}")
        print("🛠️ Manual setup may be required")

if __name__ == "__main__":
    main()
