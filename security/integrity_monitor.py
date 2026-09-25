"""
Vyom - Integrity Monitor (Tamper-Detection Kill-Switch)
Agar koi file bina authorization ke change ho, Vyom crash ho jaata hai.
"""

import hashlib
import hmac
import json
import os
import sys
from security_brain import UserLevel


class IntegrityViolationError(Exception):
    pass


class IntegrityMonitor:
    IGNORED_DIRS = {"__pycache__", "_self_edit_backups", ".git", "tests"}

    def __init__(self, package_root, baseline_file, secret_key):
        self.package_root = os.path.abspath(package_root)
        self.baseline_file = baseline_file
        self.secret_key = secret_key

    def _iter_source_files(self):
        for dirpath, dirnames, filenames in os.walk(self.package_root):
            dirnames[:] = [d for d in dirnames if d not in self.IGNORED_DIRS]
            for fname in filenames:
                if fname.endswith(".py"):
                    yield os.path.join(dirpath, fname)

    def _hash_file(self, path):
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()

    def _compute_snapshot(self):
        snapshot = {}
        for path in sorted(self._iter_source_files()):
            rel = os.path.relpath(path, self.package_root)
            snapshot[rel] = self._hash_file(path)
        return snapshot

    def _sign(self, snapshot):
        canonical = json.dumps(snapshot, sort_keys=True).encode("utf-8")
        return hmac.new(self.secret_key, canonical, hashlib.sha256).hexdigest()

    def create_baseline(self):
        snapshot = self._compute_snapshot()
        signature = self._sign(snapshot)
        with open(self.baseline_file, "w", encoding="utf-8") as f:
            json.dump({"snapshot": snapshot, "signature": signature}, f)
        os.chmod(self.baseline_file, 0o600)
        return {"ok": True, "files_tracked": len(snapshot)}

    def verify(self):
        if not os.path.exists(self.baseline_file):
            return {"ok": False, "reason": "no_baseline"}

        with open(self.baseline_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        stored_snapshot = data["snapshot"]
        stored_signature = data["signature"]

        expected_sig = self._sign(stored_snapshot)
        if not hmac.compare_digest(expected_sig, stored_signature):
            return {"ok": False, "reason": "baseline_signature_invalid"}

        current_snapshot = self._compute_snapshot()
        added = sorted(set(current_snapshot) - set(stored_snapshot))
        removed = sorted(set(stored_snapshot) - set(current_snapshot))
        changed = sorted(
            f for f in current_snapshot
            if f in stored_snapshot and current_snapshot[f] != stored_snapshot[f]
        )

        if added or removed or changed:
            return {"ok": False, "reason": "tampered", "added": added, "removed": removed, "changed": changed}

        return {"ok": True}

    def verify_or_crash(self, allow_first_run_baseline=True):
        result = self.verify()
        if result["ok"]:
            return

        if result["reason"] == "no_baseline" and allow_first_run_baseline:
            self.create_baseline()
            return

        self._crash(result)

    def _crash(self, result):
        print("=" * 60, file=sys.stderr)
        print("VYOM INTEGRITY VIOLATION — UNAUTHORIZED CHANGE DETECTED", file=sys.stderr)
        print("Reason: " + result["reason"], file=sys.stderr)
        if "changed" in result:
            print("Changed files: " + str(result["changed"]), file=sys.stderr)
        print("=" * 60, file=sys.stderr)
        raise IntegrityViolationError("Unauthorized modification detected — Vyom halted.")

    def reauthorize_changes(self, auth_system, user_id, password):
        login_result = auth_system.login(user_id, password, session_duration_seconds=60)
        if not login_result["ok"]:
            return {"ok": False, "error": "Authentication fail — reauthorize nahi ho saka."}
        if login_result["level"] != UserLevel.MASTER.value:
            return {"ok": False, "error": "Sirf MASTER user reauthorize kar sakta hai."}

        return self.create_baseline()


def load_or_create_secret_key(key_path):
    import secrets
    if os.path.exists(key_path):
        with open(key_path, "rb") as f:
            return f.read()
    key = secrets.token_bytes(32)
    with open(key_path, "wb") as f:
        f.write(key)
    os.chmod(key_path, 0o600)
    return key
