"""
Vyom - Security Brain
Authentication, authorization, permission levels, dangerous-action protection.
Architecture: LLM -> Policy Engine -> Permission Check -> Tool -> Result
"""

import json
import time
from datetime import datetime
from enum import Enum


class UserLevel(Enum):
    NORMAL = "normal_user"
    TRUSTED = "trusted_user"
    MASTER = "master"


class RiskLevel(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


DANGEROUS_ACTIONS = {
    "delete_data": RiskLevel.HIGH,
    "execute_system_command": RiskLevel.CRITICAL,
    "install_software": RiskLevel.HIGH,
    "change_security_settings": RiskLevel.CRITICAL,
    "access_private_files": RiskLevel.MEDIUM,
    "send_message": RiskLevel.MEDIUM,
    "make_purchase": RiskLevel.HIGH,
    "control_physical_device": RiskLevel.HIGH,
    "modify_network_config": RiskLevel.CRITICAL,
    "modify_own_code": RiskLevel.CRITICAL,
    "camera_access": RiskLevel.MEDIUM,
}

RISK_TO_MIN_LEVEL = {
    RiskLevel.LOW: UserLevel.NORMAL,
    RiskLevel.MEDIUM: UserLevel.TRUSTED,
    RiskLevel.HIGH: UserLevel.TRUSTED,
    RiskLevel.CRITICAL: UserLevel.MASTER,
}


class AuditLog:
    def __init__(self, path="vyom_audit.log"):
        self.path = path

    def record(self, event):
        event["timestamp"] = datetime.utcnow().isoformat()
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")


class RateLimiter:
    def __init__(self, max_calls=30, window_seconds=60):
        self.max_calls = max_calls
        self.window_seconds = window_seconds
        self._calls = {}

    def allow(self, key):
        now = time.time()
        history = self._calls.setdefault(key, [])
        history[:] = [t for t in history if now - t < self.window_seconds]
        if len(history) >= self.max_calls:
            return False
        history.append(now)
        return True


class SecurityBrain:
    def __init__(self):
        self.audit = AuditLog()
        self.rate_limiter = RateLimiter()
        self.confirmation_callback = None

    def set_confirmation_callback(self, fn):
        self.confirmation_callback = fn

    def _level_rank(self, level):
        return {UserLevel.NORMAL: 0, UserLevel.TRUSTED: 1, UserLevel.MASTER: 2}[level]

    def authorize(self, user_id, user_level, action, details=None):
        details = details or {}

        if not self.rate_limiter.allow(user_id):
            result = {"allowed": False, "reason": "rate_limited", "risk": RiskLevel.LOW}
            self._log(user_id, action, result, details)
            return result

        risk = DANGEROUS_ACTIONS.get(action, RiskLevel.LOW)
        required_level = RISK_TO_MIN_LEVEL[risk]

        if self._level_rank(user_level) < self._level_rank(required_level):
            result = {
                "allowed": False,
                "reason": "insufficient_permission (needs " + required_level.value + ")",
                "risk": risk,
            }
            self._log(user_id, action, result, details)
            return result

        if risk in (RiskLevel.HIGH, RiskLevel.CRITICAL):
            if self.confirmation_callback:
                confirmed = self.confirmation_callback(action, risk, details)
            else:
                confirmed = False
            if not confirmed:
                result = {"allowed": False, "reason": "not_confirmed_by_user", "risk": risk}
                self._log(user_id, action, result, details)
                return result

        result = {"allowed": True, "reason": "ok", "risk": risk}
        self._log(user_id, action, result, details)
        return result

    def _log(self, user_id, action, result, details):
        self.audit.record({
            "user_id": user_id,
            "action": action,
            "allowed": result["allowed"],
            "reason": result["reason"],
            "risk": result["risk"].name,
            "details": details,
        })
