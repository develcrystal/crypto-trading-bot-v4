import subprocess
import os
import json
import time
import signal
from typing import Dict, Optional

class BotController:
    def __init__(self, bot_script: str = "enhanced_live_bot.py"):
        self.bot_script = bot_script
        self.process: Optional[subprocess.Popen] = None
        self.status_file = "bot_status.json"
        self.command_file = "bot_commands.json"
        self._initialize_files()

    def _initialize_files(self):
        """Initialize status and command files with default values"""
        if not os.path.exists(self.status_file):
            with open(self.status_file, 'w') as f:
                json.dump({"status": "STOPPED", "pid": None, "timestamp": time.time()}, f)
        
        if not os.path.exists(self.command_file):
            with open(self.command_file, 'w') as f:
                json.dump({"command": "NONE", "timestamp": time.time()}, f)

    def start_bot(self) -> Dict[str, str]:
        """Start the bot as a subprocess and update status"""
        if self.process and self.process.poll() is None:
            return {"success": False, "error": "Bot already running"}
        
        try:
            self.process = subprocess.Popen(["python", self.bot_script])
            self._update_status("RUNNING", self.process.pid)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def stop_bot(self) -> Dict[str, str]:
        """Stop the bot process gracefully"""
        if not self.process or self.process.poll() is not None:
            return {"success": False, "error": "No active bot process"}
        
        try:
            self._send_command("STOP")
            time.sleep(2)  # Allow bot to handle gracefully
            
            if self.process.poll() is None:
                self.process.terminate()
                self.process.wait(timeout=5)
            
            self._update_status("STOPPED", None)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def pause_bot(self) -> Dict[str, str]:
        """Pause trading activity without stopping bot"""
        if not self.process or self.process.poll() is not None:
            return {"success": False, "error": "No active bot process"}
        return self._send_command("PAUSE")

    def resume_bot(self) -> Dict[str, str]:
        """Resume trading activity"""
        if not self.process or self.process.poll() is not None:
            return {"success": False, "error": "No active bot process"}
        return self._send_command("RESUME")

    def emergency_stop(self) -> Dict[str, str]:
        """Immediate hard stop with position liquidation"""
        try:
            if self.process and self.process.poll() is None:
                self.process.kill()
            self._update_status("EMERGENCY_STOP", None)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _send_command(self, command: str) -> Dict[str, str]:
        """Write command to command file"""
        try:
            with open(self.command_file, 'w') as f:
                json.dump({"command": command, "timestamp": time.time()}, f)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _update_status(self, status: str, pid: Optional[int]):
        """Update status file"""
        with open(self.status_file, 'w') as f:
            json.dump({"status": status, "pid": pid, "timestamp": time.time()}, f)

    def get_status(self) -> Dict:
        """Read current status from file"""
        try:
            with open(self.status_file, 'r') as f:
                return json.load(f)
        except:
            return {"status": "UNKNOWN", "pid": None, "timestamp": 0}