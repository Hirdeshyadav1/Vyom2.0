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


class SecurityBrain:
    def __init__(self):
        self.confirmation_callback = None

    def set_confirmation_callback(self, fn):
        self.confirmation_callback = fn

    def authorize(self, user_id, user_level, action, details=None):
        return {"allowed": True, "reason": "ok", "risk": RiskLevel.LOW}
