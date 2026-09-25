
"""
Vyom - Multi-Agent System
Specialized agents + router jo sahi agent ko task bhejta hai.
"""

import base64
import os


class BaseAgent:
    name = "base"

    def __init__(self, brain):
        self.brain = brain

    def can_handle(self, task):
        raise NotImplementedError

    def handle(self, task, context=None):
        raise NotImplementedError


class VisionAgent(BaseAgent):
    name = "vision"

    def __init__(self, brain, security=None):
        super().__init__(brain)
        self.security = security

    def can_handle(self, task):
        keywords = ["image", "photo", "screen", "screenshot", "dekho", "picture", "ocr", "camera"]
        return 0.9 if any(k in task.lower() for k in keywords) else 0.05

    def handle(self, task, context=None):
        return "Image dekhne ke liye analyze_image(user_id, user_level, image_path, question) use karo."

    def _media_type(self, path):
        ext = os.path.splitext(path)[1].lower()
        mapping = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".gif": "image/gif", ".webp": "image/webp"}
        return mapping.get(ext, "image/jpeg")

    def analyze_image(self, user_id, user_level, image_path, question="Is image mein kya hai, detail mein batao."):
        if self.security:
            auth = self.security.authorize(user_id, user_level, "camera_access", details={"image_path": image_path})
            if not auth["allowed"]:
                return {"ok": False, "error": "Blocked: " + auth["reason"]}

        if not os.path.exists(image_path):
            return {"ok": False, "error": "Image not found: " + image_path}

        with open(image_path, "rb") as f:
            image_b64 = base64.b64encode(f.read()).decode("utf-8")

        result = self.brain.chat(
            [{
                "role": "user",
                "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": self._media_type(image_path), "data": image_b64}},
                    {"type": "text", "text": question},
                ],
            }],
            max_tokens=1000,
        )

        if "error" in result:
            return {"ok": False, "error": result["error"]}

        texts = [b["text"] for b in result.get("content", []) if b.get("type") == "text"]
        return {"ok": True, "answer": "\n".join(texts).strip()}

    def ocr(self, user_id, user_level, image_path, language="auto"):
        lang_instruction = "kisi bhi bhasha mein ho, use detect karke" if language == "auto" else "'" + language + "' bhasha mein"
        return self.analyze_image(
            user_id, user_level, image_path,
            question="Is image mein jo bhi text hai, " + lang_instruction + " exactly extract karo.",
        )


class SecurityAgent(BaseAgent):
    name = "security"

    def can_handle(self, task):
        keywords = ["delete", "permission", "install", "password", "security", "hataye"]
        return 0.85 if any(k in task.lower() for k in keywords) else 0.05

    def handle(self, task, context=None):
        return "[SecurityAgent] Ye request SecurityBrain.authorize() se guzarni chahiye."


class ResearchAgent(BaseAgent):
    name = "research"

    def can_handle(self, task):
        keywords = ["search", "find", "latest", "news", "compare", "khoj", "dhundo"]
        return 0.8 if any(k in task.lower() for k in keywords) else 0.1

    def handle(self, task, context=None):
        prompt = "Tum ek research agent ho. User ka request: " + task
        return self.brain.simple_ask(prompt)


class CodingAgent(BaseAgent):
    name = "coding"

    def can_handle(self, task):
        keywords = ["code", "bug", "function", "debug", "refactor", "program", "script"]
        return 0.9 if any(k in task.lower() for k in keywords) else 0.1

    def handle(self, task, context=None):
        prompt = "Tum ek expert coding agent ho. Task: " + task
        return self.brain.simple_ask(prompt)

    def write_code(self, task, language=None):
        from language_knowledge import get_language_metadata
        if language:
            meta = get_language_metadata(language)
            if meta:
                prompt = "Tum ek expert " + language + " developer ho (" + meta["paradigm"] + " paradigm). Task: " + task
            else:
                prompt = "Tum ek expert " + language + " developer ho. Task: " + task
        else:
            prompt = "Tum ek expert coding agent ho. Task: " + task
        return self.brain.simple_ask(prompt)

    def debug(self, code, error):
        from language_knowledge import detect_language_from_code
        detected = detect_language_from_code(code)
        lang_hint = " (detected: " + detected + ")" if detected else ""
        prompt = "Is code" + lang_hint + " mein error hai:\n" + code + "\n\nError:\n" + error + "\n\nFix karo."
        return self.brain.simple_ask(prompt)

    def review(self, code):
        prompt = "Is code ko review karo:\n" + code
        return self.brain.simple_ask(prompt)


class PlanningAgentWrapper(BaseAgent):
    name = "planning"

    def can_handle(self, task):
        keywords = ["plan", "goal", "steps", "todo", "schedule", "roadmap"]
        return 0.8 if any(k in task.lower() for k in keywords) else 0.1

    def handle(self, task, context=None):
        return self.brain.reason_step_by_step(task)


class ScienceMathAgent(BaseAgent):
    name = "science_math"

    def can_handle(self, task):
        keywords = [
            "solve", "equation", "physics", "math", "calculate", "formula",
            "integral", "derivative", "chemistry", "science", "kitna hoga",
            "biology", "dna", "rna", "protein", "gene", "cell", "molecular weight",
            "balance", "reaction", "ph ", "mole", "gc content",
        ]
        return 0.85 if any(k in task.lower() for k in keywords) else 0.1

    def handle(self, task, context=None):
        prompt = "Tum ek physics/math/science expert ho. Step-by-step solve karo: " + task
        return self.brain.simple_ask(prompt)


class AgentRouter:
    def __init__(self, brain, security=None):
        self.agents = [
            CodingAgent(brain),
            VisionAgent(brain, security=security),
            SecurityAgent(brain),
            ResearchAgent(brain),
            PlanningAgentWrapper(brain),
            ScienceMathAgent(brain),
        ]
        self.default_brain = brain

    def route(self, task):
        scored = [(a, a.can_handle(task)) for a in self.agents]
        scored.sort(key=lambda x: x[1], reverse=True)
        best_agent, best_score = scored[0]
        return best_agent if best_score >= 0.5 else None

    def handle(self, task, context=None):
        agent = self.route(task)
        if agent is None:
            return self.default_brain.simple_ask(task)
        return agent.handle(task, context)
