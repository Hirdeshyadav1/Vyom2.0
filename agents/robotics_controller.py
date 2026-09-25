"""
Vyom - Robotics / Physical World Control
Serial port se Arduino/robot ko commands bhejta hai.
"""

ALLOWED_ROBOT_COMMANDS = ["FORWARD", "BACKWARD", "LEFT", "RIGHT", "STOP", "ARM_UP", "ARM_DOWN"]


class RoboticsController:
    def __init__(self, port="/dev/ttyUSB0", baudrate=9600, security=None):
        self.port = port
        self.baudrate = baudrate
        self.security = security
        self._serial = None

    def connect(self):
        try:
            import serial
            self._serial = serial.Serial(self.port, self.baudrate, timeout=2)
            return {"ok": True, "message": "Connected to " + self.port}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def send_command(self, user_id, user_level, command):
        command = command.upper().strip()
        if command not in ALLOWED_ROBOT_COMMANDS:
            return {"ok": False, "error": "'" + command + "' allowlisted nahi hai."}

        if self.security:
            auth = self.security.authorize(user_id, user_level, "control_physical_device", details={"command": command})
            if not auth["allowed"]:
                return {"ok": False, "error": "Blocked: " + auth["reason"]}

        if not self._serial:
            return {"ok": False, "error": "Robot se connect nahi hua."}

        try:
            self._serial.write((command + "\n").encode("utf-8"))
            return {"ok": True, "message": "Sent: " + command}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def emergency_stop(self, user_id, user_level):
        if not self._serial:
            return {"ok": False, "error": "Robot se connect nahi hua."}
        try:
            self._serial.write(b"STOP\n")
            return {"ok": True, "message": "Emergency STOP sent."}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def disconnect(self):
        if self._serial:
            self._serial.close()
