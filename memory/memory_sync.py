"""
Vyom - Multi-Device Memory Sync
Phone, laptop, home-server sab ek hi memory dekh sakein.
"""

import requests


class MemorySyncClient:
    def __init__(self, server_url):
        self.server_url = server_url.rstrip("/")

    def push_memory(self, category, content, metadata=None):
        try:
            resp = requests.post(
                self.server_url + "/api/memory/push",
                json={"category": category, "content": content, "metadata": metadata or {}},
                timeout=10,
            )
            resp.raise_for_status()
            return {"ok": True, "result": resp.json()}
        except requests.exceptions.RequestException as e:
            return {"ok": False, "error": str(e)}

    def pull_memory(self, since_id=0):
        try:
            resp = requests.get(
                self.server_url + "/api/memory/pull", params={"since_id": since_id}, timeout=10,
            )
            resp.raise_for_status()
            return {"ok": True, "memories": resp.json().get("memories", [])}
        except requests.exceptions.RequestException as e:
            return {"ok": False, "error": str(e)}

    def full_sync(self, local_memory_system):
        pull_result = self.pull_memory(since_id=0)
        if not pull_result["ok"]:
            return pull_result

        synced_count = 0
        for mem in pull_result["memories"]:
            local_memory_system.long_term.store(mem["category"], mem["content"], mem.get("metadata", {}))
            synced_count += 1

        return {"ok": True, "synced_count": synced_count}
