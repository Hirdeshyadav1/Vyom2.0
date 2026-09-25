"""
Vyom - Core LLM Brain
"""

import os
import requests

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
DEFAULT_MODEL = "claude-sonnet-5"


class LLMBrain:
    def __init__(self, api_key=None, model=DEFAULT_MODEL):
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.model = model
        self.system_prompt = "Tum Vyom ho, ek intelligent AI assistant jo Hindi, English aur Hinglish teeno mein baat kar sakta hai."

    def _headers(self):
        return {
            "x-api-key": self.api_key or "",
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

    def chat(self, messages, system=None, max_tokens=1500, tools=None):
        payload = {
            "model": self.model,
            "max_tokens": max_tokens,
            "system": system or self.system_prompt,
            "messages": messages,
        }
        if tools:
            payload["tools"] = tools

        if not self.api_key:
            return {"error": "ANTHROPIC_API_KEY not set.", "content": []}

        resp = requests.post(ANTHROPIC_API_URL, headers=self._headers(), json=payload, timeout=60)
        resp.raise_for_status()
        return resp.json()

    def simple_ask(self, prompt, system=None):
        result = self.chat([{"role": "user", "content": prompt}], system=system)
        if "error" in result:
            return "[Vyom Error] " + result["error"]
        text_parts = [b["text"] for b in result.get("content", []) if b.get("type") == "text"]
        return "\n".join(text_parts).strip()

    def reason_step_by_step(self, problem):
        prompt = "Is problem ko step-by-step reasoning se analyze karo: " + problem
        return self.simple_ask(prompt)

    def self_check(self, original_answer, question):
        prompt = "Question: " + question + "\nAnswer: " + original_answer + "\nIs answer ko check karo."
        return self.simple_ask(prompt)
