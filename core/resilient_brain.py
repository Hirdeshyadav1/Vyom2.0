"""
Vyom - Resilient Brain (Error Recovery)
Cloud API fail ho to automatically local model par fallback karta hai.
"""

from context_reliability_personalization import CircuitBreaker


class ResilientBrain:
    def __init__(self, primary_brain, fallback_brain=None):
        self.primary = primary_brain
        self.fallback = fallback_brain
        self.circuit = CircuitBreaker(failure_threshold=3, cooldown_seconds=60)
        self.system_prompt = getattr(primary_brain, "system_prompt", "")

    def simple_ask(self, prompt, system=None):
        def try_primary():
            result = self.primary.simple_ask(prompt, system=system)
            if result.startswith("[Vyom Error]") or result.startswith("[Vyom Local Error]"):
                raise RuntimeError(result)
            return result

        def try_fallback():
            if not self.fallback:
                return "[Vyom] Primary brain fail ho gaya aur koi fallback nahi hai."
            result = self.fallback.simple_ask(prompt, system=system)
            return "[Vyom - fallback mode] " + result

        return self.circuit.call(try_primary, fallback=try_fallback)

    def chat(self, messages, system=None, max_tokens=1500, tools=None):
        def try_primary():
            result = self.primary.chat(messages, system=system, max_tokens=max_tokens, tools=tools)
            if "error" in result:
                raise RuntimeError(result["error"])
            return result

        def try_fallback():
            if not self.fallback:
                return {"error": "Primary fail hua, koi fallback nahi hai.", "content": []}
            return self.fallback.chat(messages, system=system, max_tokens=max_tokens)

        return self.circuit.call(try_primary, fallback=try_fallback)

    def reason_step_by_step(self, problem):
        return self.simple_ask("Is problem ko step-by-step reasoning se analyze karo: " + problem)


def safe_hardware_call(fn, fallback_message="Ye feature abhi available nahi hai."):
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            return {"ok": False, "error": fallback_message + " (Detail: " + str(e) + ")"}
    return wrapper
