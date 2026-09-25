"""
Vyom - Smart Home Control
Home Assistant REST API se lights/AC/plugs control karta hai.
"""

import requests


class SmartHomeController:
    def __init__(self, base_url, access_token, security=None):
        self.base_url = base_url.rstrip("/")
        self.headers = {"Authorization": "Bearer " + access_token, "Content-Type": "application/json"}
        self.security = security

    def _call_service(self, domain, service, entity_id, extra_data=None):
        url = self.base_url + "/api/services/" + domain + "/" + service
        payload = {"entity_id": entity_id}
        if extra_data:
            payload.update(extra_data)
        try:
            resp = requests.post(url, headers=self.headers, json=payload, timeout=10)
            resp.raise_for_status()
            return {"ok": True, "result": resp.json()}
        except requests.exceptions.RequestException as e:
            return {"ok": False, "error": str(e)}

    def turn_on(self, user_id, user_level, entity_id):
        if self.security:
            auth = self.security.authorize(user_id, user_level, "control_physical_device", details={"entity_id": entity_id, "action": "on"})
            if not auth["allowed"]:
                return {"ok": False, "error": "Blocked: " + auth["reason"]}
        domain = entity_id.split(".")[0]
        return self._call_service(domain, "turn_on", entity_id)

    def turn_off(self, user_id, user_level, entity_id):
        if self.security:
            auth = self.security.authorize(user_id, user_level, "control_physical_device", details={"entity_id": entity_id, "action": "off"})
            if not auth["allowed"]:
                return {"ok": False, "error": "Blocked: " + auth["reason"]}
        domain = entity_id.split(".")[0]
        return self._call_service(domain, "turn_off", entity_id)

    def set_temperature(self, user_id, user_level, entity_id, temperature):
        if self.security:
            auth = self.security.authorize(user_id, user_level, "control_physical_device", details={"entity_id": entity_id, "temperature": temperature})
            if not auth["allowed"]:
                return {"ok": False, "error": "Blocked: " + auth["reason"]}
        return self._call_service("climate", "set_temperature", entity_id, {"temperature": temperature})

    def get_state(self, entity_id):
        url = self.base_url + "/api/states/" + entity_id
        try:
            resp = requests.get(url, headers=self.headers, timeout=10)
            resp.raise_for_status()
            return {"ok": True, "state": resp.json()}
        except requests.exceptions.RequestException as e:
            return {"ok": False, "error": str(e)}
