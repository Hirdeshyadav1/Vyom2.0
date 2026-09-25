"""
Vyom - Autonomous Background Worker
Continuously background mein chalta hai, approved goals par kaam karta rehta hai.
"""

import threading
import time
from autonomy import AutonomyLevel


class AutonomousWorker:
    def __init__(self, planner, autonomy, security, user_id, user_level, poll_interval=5.0):
        self.planner = planner
        self.autonomy = autonomy
        self.security = security
        self.user_id = user_id
        self.user_level = user_level
        self.poll_interval = poll_interval
        self._running = False
        self._thread = None
        self.active_goal_ids = []
        self.log = []
        self.on_task_complete = None

    def add_goal(self, goal):
        plan = self.planner.create_plan(goal)
        self.active_goal_ids.append(plan.id)
        return plan.id

    def _process_goal(self, goal_id):
        task = self.planner.next_actionable_task(goal_id)
        if not task:
            return

        needs_confirm = self.autonomy.should_ask_confirmation(action_name=task.title, risk_is_high=False)
        if needs_confirm and self.autonomy.default_level in (
            AutonomyLevel.ANSWER_ONLY, AutonomyLevel.SUGGEST, AutonomyLevel.APPROVE_THEN_ACT,
        ):
            self.log.append({"goal_id": goal_id, "task": task.title, "status": "waiting_for_approval"})
            return

        try:
            self.planner.mark_done(goal_id, task.id)
            entry = {"goal_id": goal_id, "task": task.title, "status": "done"}
            self.log.append(entry)
            if self.on_task_complete:
                self.on_task_complete(entry)
        except Exception as e:
            self.planner.replan(task.id, reason=str(e))
            self.log.append({"goal_id": goal_id, "task": task.title, "status": "failed", "error": str(e)})

    def _loop(self):
        while self._running:
            for goal_id in list(self.active_goal_ids):
                self._process_goal(goal_id)
            time.sleep(self.poll_interval)

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False

    def get_log(self):
        return self.log
