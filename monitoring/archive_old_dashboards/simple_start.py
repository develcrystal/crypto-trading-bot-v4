"""
🚀 SIMPLE DASHBOARD START
Verwendet BESTEHENDE crypto-bot_V2 Umgebung ohne Neuinstallation
"""

import subprocess
import sys
import os

def main():
    print("🚀 SIMPLE DASHBOARD START")
    print("=" * 35)
    print("🐍 Using EXISTING crypto-bot_V2 environment")
    print("📊 NO package installation!")
    print()
    
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    print("🐍 Starting dashboard in crypto-bot_V2...")
    print("🌐 URL: http://localhost:8501") 
    print("💡 Press CTRL+C to stop")
    print("-" * 40)
    
    try:
        # Start streamlit directly in existing conda environment
        subprocess.call([
            'conda', 'run', '-n', 'crypto-bot_V2',
            'streamlit', 'run', 'dashboard.py',
            '--server.port', '8501'
        ])
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped!")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Make sure:")
        print("• crypto-bot_V2 conda environment exists")
        print("• streamlit is installed in that environment")
        print("• You're in the monitoring directory")

if __name__ == "__main__":
    main()
