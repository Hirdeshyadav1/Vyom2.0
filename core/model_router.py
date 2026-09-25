"""
Vyom - Model Router
Har task ke liye ek hi model zaroori nahi.
"""

from enum import Enum


class TaskType(Enum):
    SIMPLE_CHAT = "simple_chat"
    DEEP_REASONING = "deep_reasoning"
    CODING = "coding"
    VISION = "vision"
    SPEECH = "speech"


MODEL_MAP = {
    TaskType.SIMPLE_CHAT: "claude-haiku-4-5-20251001",
    TaskType.DEEP_REASONING: "claude-fable-5-1",
    TaskType.CODING: "claude-sonnet-5",
    TaskType.VISION: "claude-sonnet-5",
    TaskType.SPEECH: "claude-haiku-4-5-20251001",
}


class ModelRouter:
    def __init__(self, overrides=None):
        self.model_map = dict(MODEL_MAP)
        if overrides:
            self.model_map.update(overrides)

    def classify(self, task):
        t = task.lower()
        if "code" in t or "bug" in t or "function" in t or "debug" in t or "script" in t:
            return TaskType.CODING
        if "image" in t or "photo" in t or "screenshot" in t or "ocr" in t or "dekho" in t:
            return TaskType.VISION
        if "analyze deeply" in t or "complex" in t or "prove" in t or "detailed reasoning" in t:
            return TaskType.DEEP_REASONING
        return TaskType.SIMPLE_CHAT

    def pick_model(self, task):
        task_type = self.classify(task)
        return self.model_map[task_type]
