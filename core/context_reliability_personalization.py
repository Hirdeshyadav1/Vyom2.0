"""
Vyom - Context Engine, Reliability Layer, Personalization Engine
"""

import time
import functools
from datetime import datetime


class ContextEngine:
    def __init__(self, memory_system=None):
        self.memory_system = memory_system
        self._extra = {}

    def set(self, key, value):
        self._extra[key] = value

    def build(self, query=""):
        ctx = {"time": datetime.utcnow().isoformat()}
        ctx.update(self._extra)
        if self.memory_system:
            ctx["memory"] = self.memory_system.full_context(query)
        return ctx


class IdentitySystem:
    def __init__(self):
        self.sessions = {}

    def start_session(self, session_id, user_id, device, user_level):
        self.sessions[session_id] = {
            "user_id": user_id,
            "device": device,
            "user_level": user_level,
            "started_at": datetime.utcnow().isoformat(),
        }

    def get_session(self, session_id):
        return self.sessions.get(session_id)

    def end_session(self, session_id):
        self.sessions.pop(session_id, None)


def with_retry(max_attempts=3, backoff_seconds=1.0):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            last_err = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return fn(*args, **kwargs)
                except Exception as e:
                    last_err = e
                    if attempt < max_attempts:
                        time.sleep(backoff_seconds * (2 ** (attempt - 1)))
            raise last_err
        return wrapper
    return decorator


class CircuitBreaker:
    def __init__(self, failure_threshold=5, cooldown_seconds=30):
        self.failure_threshold = failure_threshold
        self.cooldown_seconds = cooldown_seconds
        self.failures = 0
        self.open_until = None

    def call(self, fn, *args, fallback=None, **kwargs):
        now = time.time()
        if self.open_until and now < self.open_until:
            return fallback() if callable(fallback) else fallback
        try:
            result = fn(*args, **kwargs)
            self.failures = 0
            return result
        except Exception:
            self.failures += 1
            if self.failures >= self.failure_threshold:
                self.open_until = now + self.cooldown_seconds
            if fallback is not None:
                return fallback() if callable(fallback) else fallback
            raise


class PersonalizationEngine:
    def __init__(self, memory_system):
        self.memory_system = memory_system

    def record_language_use(self, language):
        self.memory_system.remember_preference("User often writes in: " + language, metadata={"type": "language"})

    def record_tool_use(self, tool_name):
        self.memory_system.remember_fact("User frequently uses tool: " + tool_name, metadata={"type": "tool_usage"})

    def get_preferred_style(self):
        prefs = self.memory_system.recall("style", category="preference")
        if prefs:
            return prefs[0]["content"]
        return "default"
