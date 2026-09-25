"""
Vyom - Feedback & Beta Testing Logger
"""

import json
import traceback
import functools
from datetime import datetime


class FeedbackLogger:
    def __init__(self, log_path="vyom_feedback.log"):
        self.log_path = log_path

    def log_interaction(self, user_id, message, response, rating=None):
        entry = {
            "type": "interaction",
            "user_id": user_id,
            "message": message,
            "response": response,
            "rating": rating,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self._write(entry)

    def log_crash(self, error, context=None):
        entry = {
            "type": "crash",
            "error": str(error),
            "traceback": traceback.format_exc(),
            "context": context or {},
            "timestamp": datetime.utcnow().isoformat(),
        }
        self._write(entry)

    def log_user_feedback(self, user_id, feedback_text, category="general"):
        entry = {
            "type": "feedback",
            "user_id": user_id,
            "category": category,
            "feedback": feedback_text,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self._write(entry)

    def _write(self, entry):
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def get_recent_crashes(self, limit=20):
        entries = self._read_all()
        crashes = [e for e in entries if e.get("type") == "crash"]
        return crashes[-limit:]

    def get_average_rating(self):
        entries = self._read_all()
        ratings = [e["rating"] for e in entries if e.get("type") == "interaction" and e.get("rating")]
        return sum(ratings) / len(ratings) if ratings else 0.0

    def _read_all(self):
        try:
            with open(self.log_path, "r", encoding="utf-8") as f:
                return [json.loads(line) for line in f if line.strip()]
        except FileNotFoundError:
            return []


def with_crash_logging(logger):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except Exception as e:
                logger.log_crash(e, context={"function": fn.__name__})
                raise
        return wrapper
    return decorator
