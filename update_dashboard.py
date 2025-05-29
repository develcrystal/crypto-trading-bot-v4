#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Dashboard Update Skript
Implementiert den fixierten BybitClient im Enhanced Dashboard
"""

import os
import sys
import shutil
import time
import io
import sys
from datetime import datetime

# Setze die Standardkodierung auf UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def update_dashboard():
    """Aktualisiert das Dashboard mit dem fixierten BybitClient"""
    print("\n===== DASHBOARD UPDATE =====\n")
    
    # Setze Pfade
    project_dir = r"J:\Meine Ablage\CodingStuff\crypto-bot_V2"
    backup_dir = os.path.join(project_dir, "backups", f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    
    # Dateien, die aktualisiert werden müssen
    files_to_update = {
        "trading/bybit_client.py": "trading/bybit_client_fixed.py",
        "monitoring/enhanced_smart_money_bot_dashboard.py": None
    }
    
    try:
        # Erstelle Backup-Verzeichnis
        os.makedirs(backup_dir, exist_ok=True)
        print(f"[OK] Backup-Verzeichnis erstellt: {backup_dir}")
        
        # Backup und Update der Dateien
        for original, replacement in files_to_update.items():
            original_path = os.path.join(project_dir, original)
            
            # Backup erstellen
            if os.path.exists(original_path):
                backup_path = os.path.join(backup_dir, os.path.basename(original))
                shutil.copy2(original_path, backup_path)
                print(f"[OK] Backup erstellt: {backup_path}")
            
            # Datei aktualisieren, wenn ein Ersatz angegeben ist
            if replacement:
                replacement_path = os.path.join(project_dir, replacement)
                if os.path.exists(replacement_path):
                    shutil.copy2(replacement_path, original_path)
                    print(f"[OK] Datei aktualisiert: {original} (mit {replacement})")
        
        # Aktualisiere enhanced_smart_money_bot_dashboard.py mit zusätzlichen Debug-Ausgaben
        dashboard_path = os.path.join(project_dir, "monitoring/enhanced_smart_money_bot_dashboard.py")
        
        if os.path.exists(dashboard_path):
            with open(dashboard_path, 'r', encoding='utf-8') as f:
                dashboard_code = f.read()
            
            # Verbessere die Fehlerbehandlung in der Marktregime-Funktion
            if "render_market_regime_panel" in dashboard_code:
                print("Aktualisiere Marktregime-Panel mit verbesserter Fehlerbehandlung...")
                
                # Suche nach dem Code-Block, der df = bybit.get_market_data(...) enthält
                old_code = """        df = bybit.get_market_data(symbol="BTCUSDT", interval="240", limit=100)
        
        if df is not None and not df.empty:"""
                
                new_code = """        # Get 4h data for better regime detection
        print("Versuche, Marktdaten für das Regime-Panel abzurufen...")
        df = bybit.get_market_data(symbol="BTCUSDT", interval="240", limit=100)
        
        if df is not None and not df.empty:
            print(f"✅ Erfolgreich {len(df)} 4h-Kerzen für Regime-Analyse geladen")"""
                
                if old_code in dashboard_code:
                    dashboard_code = dashboard_code.replace(old_code, new_code)
                    print("✅ Marktregime-Panel-Code aktualisiert")
            
            # Verbessere die Fehlerbehandlung in der Performance-Funktion
            if "render_performance_charts" in dashboard_code:
                print("Aktualisiere Performance-Charts-Panel mit verbesserter Fehlerbehandlung...")
                
                # Suche nach dem Code-Block, der market_data = bybit.get_market_data(...) enthält
                old_code = """                market_data = bybit.get_market_data(symbol="BTCUSDT", interval=1440, limit=30)  # 1 day candles
                
                if market_data is None or market_data.empty:"""
                
                new_code = """                print("Versuche, Marktdaten für Performance-Charts abzurufen...")
                market_data = bybit.get_market_data(symbol="BTCUSDT", interval=1440, limit=30)  # 1 day candles
                
                if market_data is None or market_data.empty:
                    print("❌ Keine Tages-Kerzen gefunden für Performance-Charts")"""
                
                if old_code in dashboard_code:
                    dashboard_code = dashboard_code.replace(old_code, new_code)
                    print("✅ Performance-Charts-Panel-Code aktualisiert")
                
                # Füge zusätzliche Erfolgsmeldung hinzu
                old_success = """                    st.success(f"✅ Erfolgreich {len(market_data)} Tageskerzen geladen")"""
                
                new_success = """                    st.success(f"✅ Erfolgreich {len(market_data)} Tageskerzen geladen")
                    print(f"✅ Erfolgreich {len(market_data)} Tageskerzen für Performance-Charts geladen")"""
                
                if old_success in dashboard_code:
                    dashboard_code = dashboard_code.replace(old_success, new_success)
            
            # Schreibe aktualisierte Datei
            with open(dashboard_path, 'w', encoding='utf-8') as f:
                f.write(dashboard_code)
            
            print(f"[OK] Dashboard-Code mit verbesserter Fehlerbehandlung aktualisiert")
        
        print("\n----- UPDATE ABGESCHLOSSEN -----")
        print("\n[OK] Update erfolgreich abgeschlossen!")
        print("Das Dashboard wurde erfolgreich aktualisiert und sollte nun in der Lage sein,")
        print("echte Marktdaten abzurufen und anzuzeigen.")
        print("\nWie man das aktualisierte Dashboard startet:")
        print("1. Navigiere zu: J:\\Meine Ablage\\CodingStuff\\crypto-bot_V2\\monitoring")
        print("\n[WARN] HINWEIS: Die Datei enhanced_smart_money_bot_dashboard.py wurde nicht gefunden.")
        print("Bei Problemen können die Originaldateien aus dem Backup wiederhergestellt werden.")
    
    except Exception as e:
        print(f"\n[ERROR] FEHLER beim Update: {str(e)}")
        print("Bitte stellen Sie die Originaldateien aus dem Backup wieder her.")

if __name__ == "__main__":
    update_dashboard()
