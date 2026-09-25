"""
Vyom - Computer Control Agent
Apps kholna, system status, allowlisted commands — sab security-gated.
"""

import subprocess
import platform
import os

ALLOWED_COMMANDS = {
    "list_directory": ["ls", "-la"],
    "disk_usage": ["df", "-h"],
    "current_processes": ["ps", "aux"],
    "system_uptime": ["uptime"],
}


class ComputerControlAgent:
    def __init__(self, security):
        self.security = security

    def system_status(self):
        return {
            "os": platform.system(),
            "os_version": platform.version(),
            "machine": platform.machine(),
            "cwd": os.getcwd(),
        }

    def list_files(self, path):
        return os.listdir(path)

    def run_allowed_command(self, user_id, user_level, command_key):
        if command_key not in ALLOWED_COMMANDS:
            return {"ok": False, "error": "'" + command_key + "' allowlisted nahi hai."}

        auth = self.security.authorize(user_id, user_level, "execute_system_command", details={"command_key": command_key})
        if not auth["allowed"]:
            return {"ok": False, "error": "Blocked: " + auth["reason"]}

        try:
            result = subprocess.run(ALLOWED_COMMANDS[command_key], capture_output=True, text=True, timeout=10)
            return {"ok": True, "stdout": result.stdout, "stderr": result.stderr}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def open_application(self, user_id, user_level, app_name):
        auth = self.security.authorize(user_id, user_level, "execute_system_command", details={"app_name": app_name})
        if not auth["allowed"]:
            return {"ok": False, "error": "Blocked: " + auth["reason"]}

        system = platform.system()
        try:
            if system == "Windows":
                os.startfile(app_name)
            elif system == "Darwin":
                subprocess.Popen(["open", "-a", app_name])
            else:
                subprocess.Popen([app_name])
            return {"ok": True, "message": "'" + app_name + "' open karne ki koshish ki."}
        except FileNotFoundError:
            return {"ok": False, "error": "'" + app_name + "' nahi mila."}
        except Exception as e:
            return {"ok": False, "error": str(e)}
