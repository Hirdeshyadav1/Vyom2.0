"""
Vyom - Gemini Brain (FREE, koi credit card nahi chahiye)
Google AI Studio se free API key milti hai: https://aistudio.google.com
"""

import os
import requests

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{}:generateContent"
DEFAULT_MODEL = "gemini-3.6-flash"


class GeminiBrain:
    def __init__(self, api_key=None, model=DEFAULT_MODEL):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self.model = model
        self.system_prompt = "Tum Vyom ho, ek intelligent AI assistant jo Hindi, English aur Hinglish teeno mein baat kar sakta hai."

    def chat(self, messages, system=None, max_tokens=1500, tools=None):
        if not self.api_key:
            return {"error": "GEMINI_API_KEY not set.", "content": []}

        combined_text = (system or self.system_prompt) + "\n\n"
        for m in messages:
            content = m["content"]
            if isinstance(content, str):
                combined_text += content
            else:
                combined_text += " ".join(b.get("text", "") for b in content if isinstance(b, dict))

        payload = {
            "contents": [{"parts": [{"text": combined_text}]}],
            "generationConfig": {"maxOutputTokens": max_tokens},
        }

        url = GEMINI_API_URL.format(self.model) + "?key=" + self.api_key

        try:
            resp = requests.post(url, json=payload, timeout=60)
            resp.raise_for_status()
            data = resp.json()
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            return {"content": [{"type": "text", "text": text}]}
        except Exception as e:
            error_detail = ""
            try:
                error_detail = resp.text
            except Exception:
                pass
            return {"error": "Gemini error: " + str(e) + " " + error_detail, "content": []}

    def simple_ask(self, prompt, system=None):
        result = self.chat([{"role": "user", "content": prompt}], system=system)
        if "error" in result:
            return "[Vyom Gemini Error] " + result["error"]
        parts = [b["text"] for b in result.get("content", []) if b.get("type") == "text"]
        return "\n".join(parts).strip()

    def reason_step_by_step(self, problem):
        prompt = "Is problem ko step-by-step reasoning se analyze karo: " + problem
        return self.simple_ask(prompt)

    def self_check(self, original_answer, question):
        prompt = "Question: " + question + "\nAnswer: " + original_answer + "\nIs answer ko check karo."
        return self.simple_ask(prompt)
