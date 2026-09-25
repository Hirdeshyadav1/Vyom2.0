"""
Vyom - Authentication System
Password/token verify karke hi UserLevel milta hai.
"""

import hashlib
import hmac
import os
import secrets
import time
from security_brain import UserLevel


class AuthenticationSystem:
    def __init__(self, credentials_file="vyom_credentials.json"):
        self.credentials_file = credentials_file
        self._sessions = {}
        self._failed_attempts = {}
        self.max_failed_attempts = 5
        self.lockout_seconds = 300
        self._load_credentials()

    def _load_credentials(self):
        import json
        if os.path.exists(self.credentials_file):
            with open(self.credentials_file, "r") as f:
                self._credentials = json.load(f)
        else:
            self._credentials = {}
            self._save_credentials()

    def _save_credentials(self):
        import json
        with open(self.credentials_file, "w") as f:
            json.dump(self._credentials, f)
        os.chmod(self.credentials_file, 0o600)

    def _hash_password(self, password, salt):
        return hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 200000).hex()

    def register_user(self, user_id, password, level):
        if user_id in self._credentials:
            return {"ok": False, "error": "User already exists."}
        salt = secrets.token_bytes(16)
        password_hash = self._hash_password(password, salt)
        self._credentials[user_id] = {
            "salt": salt.hex(),
            "password_hash": password_hash,
            "level": level.value,
        }
        self._save_credentials()
        return {"ok": True, "message": "User '" + user_id + "' registered as " + level.value + "."}

    def _is_locked_out(self, user_id):
        attempts = self._failed_attempts.get(user_id, [])
        recent = [t for t in attempts if time.time() - t < self.lockout_seconds]
        self._failed_attempts[user_id] = recent
        return len(recent) >= self.max_failed_attempts

    def _record_failed_attempt(self, user_id):
        self._failed_attempts.setdefault(user_id, []).append(time.time())

    def login(self, user_id, password, session_duration_seconds=3600):
        if self._is_locked_out(user_id):
            return {"ok": False, "error": "Account locked. " + str(self.lockout_seconds) + "s baad try karo."}

        record = self._credentials.get(user_id)
        if not record:
            self._record_failed_attempt(user_id)
            return {"ok": False, "error": "Invalid user_id ya password."}

        salt = bytes.fromhex(record["salt"])
        computed_hash = self._hash_password(password, salt)

        if not hmac.compare_digest(computed_hash, record["password_hash"]):
            self._record_failed_attempt(user_id)
            return {"ok": False, "error": "Invalid user_id ya password."}

        token = secrets.token_urlsafe(32)
        self._sessions[token] = {
            "user_id": user_id,
            "level": UserLevel(record["level"]),
            "expires_at": time.time() + session_duration_seconds,
        }
        return {"ok": True, "token": token, "level": record["level"], "expires_in": session_duration_seconds}

    def verify_token(self, token):
        session = self._sessions.get(token)
        if not session:
            return None
        if time.time() > session["expires_at"]:
            del self._sessions[token]
            return None
        return session

    def logout(self, token):
        self._sessions.pop(token, None)

    def change_password(self, user_id, old_password, new_password):
        login_result = self.login(user_id, old_password, session_duration_seconds=1)
        if not login_result["ok"]:
            return {"ok": False, "error": "Purana password galat hai."}
        salt = secrets.token_bytes(16)
        self._credentials[user_id]["salt"] = salt.hex()
        self._credentials[user_id]["password_hash"] = self._hash_password(new_password, salt)
        self._save_credentials()
        return {"ok": True, "message": "Password change ho gaya."}
