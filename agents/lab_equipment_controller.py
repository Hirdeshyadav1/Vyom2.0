"""
Vyom - Lab Equipment Controller
Serial, MQTT, HTTP - teen protocols se lab instruments control karta hai.
"""

ALLOWED_LAB_COMMANDS = [
    "READ_TEMPERATURE", "READ_PRESSURE", "READ_PH", "START_HEATER",
    "STOP_HEATER", "START_PUMP", "STOP_PUMP", "CALIBRATE", "EMERGENCY_STOP",
]


class LabEquipmentController:
    def __init__(self, security=None):
        self.security = security
        self._serial_conn = None
        self._mqtt_client = None
        self._http_base_url = None
        self._http_headers = {}

    def connect_serial(self, port, baudrate=9600):
        try:
            import serial
            self._serial_conn = serial.Serial(port, baudrate, timeout=3)
            return {"ok": True, "message": "Serial connected: " + port}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def send_serial_command(self, user_id, user_level, command):
        result = self._check_command(user_id, user_level, command)
        if not result["ok"]:
            return result
        if not self._serial_conn:
            return {"ok": False, "error": "Serial connect nahi hua."}
        try:
            self._serial_conn.write((command + "\n").encode("utf-8"))
            response = self._serial_conn.readline().decode("utf-8").strip()
            return {"ok": True, "response": response}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def connect_mqtt(self, broker_host, broker_port=1883, topic_prefix="vyom/lab"):
        try:
            import paho.mqtt.client as mqtt
            self._mqtt_client = mqtt.Client()
            self._mqtt_client.connect(broker_host, broker_port, keepalive=60)
            self._mqtt_topic_prefix = topic_prefix
            return {"ok": True, "message": "MQTT connected: " + broker_host + ":" + str(broker_port)}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def send_mqtt_command(self, user_id, user_level, command):
        result = self._check_command(user_id, user_level, command)
        if not result["ok"]:
            return result
        if not self._mqtt_client:
            return {"ok": False, "error": "MQTT connect nahi hua."}
        try:
            topic = self._mqtt_topic_prefix + "/command"
            self._mqtt_client.publish(topic, command)
            return {"ok": True, "message": "Published '" + command + "' to " + topic}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def connect_http(self, base_url, api_key=None):
        self._http_base_url = base_url.rstrip("/")
        self._http_headers = {"Authorization": "Bearer " + api_key} if api_key else {}

    def send_http_command(self, user_id, user_level, command, params=None):
        result = self._check_command(user_id, user_level, command)
        if not result["ok"]:
            return result
        if not self._http_base_url:
            return {"ok": False, "error": "HTTP endpoint configure nahi hua."}
        import requests
        try:
            resp = requests.post(
                self._http_base_url + "/command",
                json={"command": command, "params": params or {}},
                headers=self._http_headers, timeout=10,
            )
            resp.raise_for_status()
            return {"ok": True, "result": resp.json()}
        except requests.exceptions.RequestException as e:
            return {"ok": False, "error": str(e)}

    def _check_command(self, user_id, user_level, command):
        command = command.upper().strip()
        if command not in ALLOWED_LAB_COMMANDS:
            return {"ok": False, "error": "'" + command + "' allowlisted nahi hai."}

        if command == "EMERGENCY_STOP":
            return {"ok": True}

        if self.security:
            auth = self.security.authorize(user_id, user_level, "control_physical_device", details={"command": command})
            if not auth["allowed"]:
                return {"ok": False, "error": "Blocked: " + auth["reason"]}
        return {"ok": True}
