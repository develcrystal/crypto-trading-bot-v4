"""
Bot Status Monitor - Prozessüberwachung für den Crypto Trading Bot

Funktionen:
- status_check(): Überprüft den aktuellen Status des Bot-Prozesses
- log_events(): Protokolliert wichtige Bot-Ereignisse
- emergency_stop(): Stoppt den Bot-Prozess sicher
"""

import psutil
import logging
import yaml
import os
import time
from datetime import datetime

# Konfiguration laden
CONFIG_PATH = os.path.join(os.path.dirname(__file__), '../config/monitoring_config.yaml')

class BotStatusMonitor:
    def __init__(self, bot_pid=None):
        """
        Initialisiert den Status-Monitor mit optionaler PID
        
        Args:
            bot_pid: Prozess-ID des Hauptbots (wenn nicht angegeben, wird automatisch gesucht)
        """
        self.logger = logging.getLogger(__name__)
        self.config = self.load_config()
        self.bot_pid = bot_pid or self.find_bot_process()
        self.status = "STOPPED"
        self.start_time = None
        self.last_check = datetime.now()
        
    def load_config(self):
        """Lädt die Monitoring-Konfiguration aus der YAML-Datei"""
        try:
            with open(CONFIG_PATH, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            self.logger.warning("Monitoring-Konfiguration nicht gefunden. Verwende Standardwerte.")
            return {
                'check_interval': 5,
                'max_restarts': 3,
                'log_path': '../logs/bot_monitor.log'
            }
    
    def find_bot_process(self):
        """
        Sucht den Bot-Prozess anhand des Skriptnamens
        
        Returns:
            int: Prozess-ID oder None wenn nicht gefunden
        """
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info['cmdline']
                if cmdline and 'enhanced_live_bot.py' in ' '.join(cmdline):
                    return proc.info['pid']
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return None
    
    def status_check(self):
        """Überprüft den aktuellen Status des Bot-Prozesses"""
        self.last_check = datetime.now()
        
        if not self.bot_pid:
            self.bot_pid = self.find_bot_process()
            if not self.bot_pid:
                self.status = "STOPPED"
                return self.status
        
        try:
            process = psutil.Process(self.bot_pid)
            if process.is_running():
                self.status = "RUNNING"
                if not self.start_time:
                    self.start_time = datetime.fromtimestamp(process.create_time())
                return self.status
        except psutil.NoSuchProcess:
            self.status = "STOPPED"
            self.start_time = None
        
        return self.status
    
    def log_events(self, event_type, message):
        """Protokolliert ein Ereignis im Bot-Monitor-Log"""
        log_entry = f"[{datetime.now()}] [{event_type}] {message}"
        
        # In Datei protokollieren
        log_path = os.path.abspath(os.path.join(os.path.dirname(__file__), self.config['general']['log_path']))
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        with open(log_path, 'a') as f:
            f.write(log_entry + '\n')
        
        # In Konsole protokollieren
        self.logger.info(log_entry)
    
    def emergency_stop(self):
        """Stoppt den Bot-Prozess sicher"""
        if self.status == "RUNNING":
            try:
                process = psutil.Process(self.bot_pid)
                process.terminate()
                self.log_events("EMERGENCY", "Bot-Prozess gestoppt")
                self.status = "STOPPED"
                return True
            except psutil.NoSuchProcess:
                self.log_events("WARNING", "Bot-Prozess bereits beendet")
                return False
        return False
    
    def get_uptime(self):
        """Berechnet die Laufzeit des Bot-Prozesses"""
        if self.status == "RUNNING" and self.start_time:
            return datetime.now() - self.start_time
        return timedelta(0)

# Testfunktion
if __name__ == "__main__":
    monitor = BotStatusMonitor()
    print(f"Bot Status: {monitor.status_check()}")
    monitor.log_events("INFO", "Test-Ereignis")