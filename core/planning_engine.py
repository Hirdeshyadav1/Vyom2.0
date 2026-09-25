"""
Vyom - Planning Engine
Goal -> tasks -> subtasks, priority, dependency-aware execution, replanning.
"""

import json
import uuid
from datetime import datetime
from typing import List, Dict, Optional


class Task:
    def __init__(self, title, priority=3, deadline=None, depends_on=None):
        self.id = str(uuid.uuid4())[:8]
        self.title = title
        self.priority = priority
        self.deadline = deadline
        self.depends_on = depends_on or []
        self.status = "pending"
        self.subtasks = []
        self.created_at = datetime.utcnow().isoformat()

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "priority": self.priority,
            "deadline": self.deadline,
            "depends_on": self.depends_on,
            "status": self.status,
            "subtasks": [s.to_dict() for s in self.subtasks],
            "created_at": self.created_at,
        }


class PlanningEngine:
    def __init__(self, llm_brain=None):
        self.llm_brain = llm_brain
        self.plans = {}

    def create_plan(self, goal, priority=3, deadline=None):
        root = Task(goal, priority=priority, deadline=deadline)

        if self.llm_brain:
            prompt = "Is goal ko chote-chote actionable subtasks mein todo (JSON array of strings only): " + goal
            raw = self.llm_brain.simple_ask(prompt)
            try:
                cleaned = raw.strip().strip("```json").strip("```").strip()
                subtasks = json.loads(cleaned)
                for st in subtasks:
                    root.subtasks.append(Task(st))
            except Exception:
                root.subtasks.append(Task("[unparsed] " + raw))
        else:
            root.subtasks.append(Task("Plan step 1 for: " + goal))

        self.plans[root.id] = root
        return root

    def replan(self, task_id, reason):
        task = self.plans.get(task_id)
        if not task:
            return None
        task.status = "failed"
        new_goal = task.title + " (replanned due to: " + reason + ")"
        return self.create_plan(new_goal, priority=task.priority, deadline=task.deadline)

    def next_actionable_task(self, root_id):
        root = self.plans.get(root_id)
        if not root:
            return None
        pending = [t for t in root.subtasks if t.status == "pending"]
        pending.sort(key=lambda t: t.priority)
        for t in pending:
            deps_done = all(
                any(s.id == d and s.status == "done" for s in root.subtasks)
                for d in t.depends_on
            )
            if deps_done:
                return t
        return None

    def mark_done(self, root_id, task_id):
        root = self.plans.get(root_id)
        if not root:
            return
        for t in root.subtasks:
            if t.id == task_id:
                t.status = "done"
