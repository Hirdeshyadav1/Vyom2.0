"""
Vyom - Local LLM Brain (free, apne home-server par chalta hai)
"""

import requests
from typing import List, Dict, Optional, Any


class LocalLLMBrain:
    def __init__(self, model="llama3.2", host="localhost", port=11434):
        self.model = model
        self.host = host
        self.port = port
        self.base_url = "http://" + host + ":" + str(port)
        self.system_prompt = "Tum Vyom ho, ek free aur offline AI assistant. Tum apne khud ke home server par chal rahe ho."

    def is_available(self):
        try:
            resp = requests.get(self.base_url, timeout=3)
            return resp.status_code == 200
        except Exception:
            return False

    def chat(self, messages, system=None, max_tokens=1500, tools=None):
        ollama_messages = [{"role": "system", "content": system or self.system_prompt}]
        for m in messages:
            content = m["content"]
            if isinstance(content, list):
                content = " ".join(b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text")
            ollama_messages.append({"role": m["role"], "content": content})

        payload = {"model": self.model, "messages": ollama_messages, "stream": False}

        if not self.is_available():
            return {"error": "Home server tak pahunch nahi ho payi. Check karo Ollama chal raha hai ya nahi.", "content": []}

        try:
            resp = requests.post(self.base_url + "/api/chat", json=payload, timeout=120)
            resp.raise_for_status()
            data = resp.json()
            text = data.get("message", {}).get("content", "")
            return {"content": [{"type": "text", "text": text}]}
        except Exception as e:
            return {"error": "Local model error: " + str(e), "content": []}

    def simple_ask(self, prompt, system=None):
        result = self.chat([{"role": "user", "content": prompt}], system=system)
        if "error" in result:
            return "[Vyom Local Error] " + result["error"]
        parts = [b["text"] for b in result.get("content", []) if b.get("type") == "text"]
        return "\n".join(parts).strip()

    def reason_step_by_step(self, problem):
        prompt = "Is problem ko step-by-step reasoning se analyze karo: " + problem
        return self.simple_ask(prompt)

    def self_check(self, original_answer, question):
        prompt = "Question: " + question + "\nAnswer: " + original_answer + "\nIs answer ko check karo."
        return self.simple_ask(prompt)
