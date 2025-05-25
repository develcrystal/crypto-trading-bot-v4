#!/usr/bin/env python
"""
🔊 AUDIO ALERTS TEST - Teste alle Trading Bot Sounds!
"""

import time
import sys
import os

# Add parent directory to path to import AudioAlerts
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import winsound
    AUDIO_AVAILABLE = True
    print("✅ winsound module available!")
except ImportError:
    AUDIO_AVAILABLE = False
    print("❌ winsound module not available!")

# Import our AudioAlerts class
from live_trading_bot_clean import AudioAlerts

def test_all_sounds():
    """Testet alle Audio-Alert Sounds"""
    print("\n🔊 AUDIO ALERTS TEST SUITE")
    print("=" * 50)
    
    if not AUDIO_AVAILABLE:
        print("⚠️ Audio nicht verfügbar - nur visueller Test")
        return
    
    sounds_to_test = [
        ("🚀 Bot Startup Sound", lambda: AudioAlerts.startup_sound()),
        ("🎯 BUY Signal", lambda: AudioAlerts.signal_detected("BUY")),
        ("🎯 SELL Signal", lambda: AudioAlerts.signal_detected("SELL")),
        ("✅ Success Sound", lambda: AudioAlerts.play_system_sound("success")),
        ("❌ Error Sound", lambda: AudioAlerts.play_system_sound("error")),
        ("⚠️ Warning Sound", lambda: AudioAlerts.play_system_sound("warning")),
        ("🔔 Notification", lambda: AudioAlerts.play_system_sound("notify")),
        ("🎉 Profit Celebration", lambda: AudioAlerts.celebrate_profit()),
        ("💥 Loss Alert", lambda: AudioAlerts.alert_loss()),
        ("🔇 Custom Beep (300Hz)", lambda: AudioAlerts.play_custom_beep(300, 500)),
        ("🔊 Custom Beep (1000Hz)", lambda: AudioAlerts.play_custom_beep(1000, 500)),
        ("🛑 Bot Shutdown Sound", lambda: AudioAlerts.shutdown_sound()),
    ]
    
    for i, (description, sound_func) in enumerate(sounds_to_test, 1):
        print(f"\n[{i:2d}/12] {description}")
        print("        ⏵ Playing sound...")
        
        try:
            sound_func()
            time.sleep(1.5)  # Wait for sound to finish
            print("        ✅ Sound played successfully!")
        except Exception as e:
            print(f"        ❌ Error: {e}")
        
        if i < len(sounds_to_test):
            time.sleep(0.5)  # Short pause between sounds
    
    print("\n🎵 Audio Test Complete!")
    print("=" * 50)

def test_trading_scenario():
    """Simuliert eine Trading-Session mit Audio"""
    print("\n🎬 TRADING SESSION SIMULATION")
    print("=" * 50)
    
    scenarios = [
        ("🚀 Bot Starting Up", lambda: AudioAlerts.startup_sound()),
        ("🔍 Market Analysis", lambda: AudioAlerts.play_system_sound("notify")),
        ("🎯 BUY Signal Detected", lambda: AudioAlerts.signal_detected("BUY")),
        ("✅ BUY Order Successful", lambda: (
            AudioAlerts.play_system_sound("success"),
            time.sleep(0.3),
            AudioAlerts.celebrate_profit()
        )),
        ("🔍 Continue Analysis", lambda: AudioAlerts.play_system_sound("notify")),
        ("🎯 SELL Signal Detected", lambda: AudioAlerts.signal_detected("SELL")),
        ("✅ SELL Order Successful", lambda: AudioAlerts.play_system_sound("success")),
        ("😐 No Signal Period", lambda: AudioAlerts.play_custom_beep(200, 100)),
        ("⚠️ API Warning", lambda: AudioAlerts.play_system_sound("warning")),
        ("🛑 Bot Shutting Down", lambda: AudioAlerts.shutdown_sound()),
    ]
    
    for description, action in scenarios:
        print(f"📢 {description}")
        try:
            if callable(action):
                action()
            time.sleep(2)
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n🎭 Trading Simulation Complete!")

def main():
    print("🔊 ENHANCED TRADING BOT - AUDIO SYSTEM TEST")
    print("=" * 60)
    print("Dieses Script testet alle Audio-Alerts des Trading Bots")
    print("=" * 60)
    
    choice = input("\nWähle Test-Modus:\n1️⃣  Alle Sounds einzeln testen\n2️⃣  Trading Session simulieren\n3️⃣  Beide Tests\n\nEingabe (1/2/3): ").strip()
    
    if choice == "1":
        test_all_sounds()
    elif choice == "2":
        test_trading_scenario()
    elif choice == "3":
        test_all_sounds()
        print("\n" + "="*60)
        input("Drücke Enter für Trading-Simulation...")
        test_trading_scenario()
    else:
        print("❌ Ungültige Eingabe!")
        return
    
    print(f"\n✅ Audio Test beendet!")
    print("🚀 Ready für Live Trading mit Audio Alerts!")
    input("\nDrücke Enter zum Beenden...")

if __name__ == "__main__":
    main()
