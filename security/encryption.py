"""
Vyom - Encryption / Secure Storage (pure Python, no external packages)
"""

import os
import hashlib
import hmac
import base64
import secrets


class SecureVault:
    def __init__(self, key=None, key_file="vyom_secret.key"):
        if key:
            self.key = key
        elif os.path.exists(key_file):
            with open(key_file, "rb") as f:
                self.key = f.read()
        else:
            self.key = secrets.token_bytes(32)
            with open(key_file, "wb") as f:
                f.write(self.key)
            os.chmod(key_file, 0o600)

    def _keystream(self, nonce, length):
        stream = b""
        counter = 0
        while len(stream) < length:
            block = hashlib.sha256(self.key + nonce + counter.to_bytes(4, "big")).digest()
            stream += block
            counter += 1
        return stream[:length]

    def encrypt(self, plaintext):
        data = plaintext.encode("utf-8")
        nonce = secrets.token_bytes(16)
        keystream = self._keystream(nonce, len(data))
        cipher_bytes = bytes(a ^ b for a, b in zip(data, keystream))
        mac = hmac.new(self.key, nonce + cipher_bytes, hashlib.sha256).digest()
        combined = nonce + mac + cipher_bytes
        return base64.urlsafe_b64encode(combined).decode("utf-8")

    def decrypt(self, ciphertext):
        combined = base64.urlsafe_b64decode(ciphertext.encode("utf-8"))
        nonce = combined[:16]
        mac = combined[16:48]
        cipher_bytes = combined[48:]
        expected_mac = hmac.new(self.key, nonce + cipher_bytes, hashlib.sha256).digest()
        if not hmac.compare_digest(mac, expected_mac):
            raise ValueError("Integrity check failed - data tampered ya galat key.")
        keystream = self._keystream(nonce, len(cipher_bytes))
        data = bytes(a ^ b for a, b in zip(cipher_bytes, keystream))
        return data.decode("utf-8")

    @staticmethod
    def generate_key():
        return secrets.token_bytes(32)


class EncryptedMemoryWrapper:
    SENSITIVE_CATEGORIES = {"password", "personal", "financial", "private"}

    def __init__(self, long_term_memory, vault):
        self.memory = long_term_memory
        self.vault = vault

    def store(self, category, content, metadata=None):
        if category in self.SENSITIVE_CATEGORIES:
            content = self.vault.encrypt(content)
            metadata = dict(metadata or {})
            metadata["encrypted"] = True
        self.memory.store(category, content, metadata)

    def search(self, keyword, category=None, limit=10):
        results = self.memory.search(keyword, category=category, limit=limit)
        for r in results:
            if r.get("metadata", {}).get("encrypted"):
                try:
                    r["content"] = self.vault.decrypt(r["content"])
                except Exception:
                    r["content"] = "[decryption failed]"
        return results
