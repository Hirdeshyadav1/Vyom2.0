"""
Vyom - Tamper-Evident Audit Log
Har entry mein pichli entry ka hash hota hai (blockchain-style chaining).
"""

import json
import hashlib
import os
from datetime import datetime


class TamperEvidentLog:
    def __init__(self, log_path="vyom_tamper_evident_audit.log"):
        self.log_path = log_path
        if not self._file_exists():
            self._write_genesis_block()

    def _file_exists(self):
        return os.path.exists(self.log_path) and os.path.getsize(self.log_path) > 0

    def _write_genesis_block(self):
        genesis = {
            "index": 0,
            "timestamp": datetime.utcnow().isoformat(),
            "event": {"type": "genesis"},
            "previous_hash": "0" * 64,
        }
        genesis["hash"] = self._compute_hash(genesis)
        with open(self.log_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(genesis) + "\n")

    def _compute_hash(self, entry_without_hash):
        canonical = json.dumps(entry_without_hash, sort_keys=True)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def _read_all_entries(self):
        with open(self.log_path, "r", encoding="utf-8") as f:
            return [json.loads(line) for line in f if line.strip()]

    def append(self, event):
        entries = self._read_all_entries()
        last_entry = entries[-1]

        new_entry = {
            "index": last_entry["index"] + 1,
            "timestamp": datetime.utcnow().isoformat(),
            "event": event,
            "previous_hash": last_entry["hash"],
        }
        new_entry["hash"] = self._compute_hash(new_entry)

        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(new_entry) + "\n")

        return new_entry

    def verify_integrity(self):
        entries = self._read_all_entries()

        for i, entry in enumerate(entries):
            stored_hash = entry["hash"]
            entry_copy = {k: v for k, v in entry.items() if k != "hash"}
            recomputed_hash = self._compute_hash(entry_copy)

            if recomputed_hash != stored_hash:
                return {
                    "valid": False,
                    "error": "Entry #" + str(i) + " ka hash match nahi hua — tamper hua hai!",
                    "broken_at_index": entry["index"],
                }

            if i > 0 and entry["previous_hash"] != entries[i - 1]["hash"]:
                return {
                    "valid": False,
                    "error": "Entry #" + str(i) + " ki chain break hai.",
                    "broken_at_index": entry["index"],
                }

        return {"valid": True, "total_entries": len(entries)}
