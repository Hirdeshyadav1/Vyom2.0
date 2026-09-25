"""
Vyom - Task Scheduler
Reminders, scheduled tasks, recurring tasks, background jobs.
"""

import threading
import time
from datetime import datetime, timedelta
import uuid


class ScheduledJob:
    def __init__(self, name, run_at, callback, recurring_seconds=None):
        self.id = str(uuid.uuid4())[:8]
        self.name = name
        self.run_at = run_at
        self.callback = callback
        self.recurring_seconds = recurring_seconds
        self.cancelled = False


class TaskScheduler:
    def __init__(self):
        self.jobs = {}
        self._thread = None
        self._running = False

    def add_reminder(self, name, run_at, callback):
        job = ScheduledJob(name, run_at, callback)
        self.jobs[job.id] = job
        return job.id

    def add_recurring(self, name, every_seconds, callback):
        job = ScheduledJob(name, datetime.utcnow() + timedelta(seconds=every_seconds), callback, recurring_seconds=every_seconds)
        self.jobs[job.id] = job
        return job.id

    def cancel(self, job_id):
        if job_id in self.jobs:
            self.jobs[job_id].cancelled = True

    def start(self, poll_interval=1.0):
        if self._running:
            return
        self._running = True

        def loop():
            while self._running:
                now = datetime.utcnow()
                for job_id, job in list(self.jobs.items()):
                    if job.cancelled:
                        del self.jobs[job_id]
                        continue
                    if now >= job.run_at:
                        try:
                            job.callback()
                        except Exception as e:
                            print("[Scheduler] Job failed: " + str(e))
                        if job.recurring_seconds:
                            job.run_at = now + timedelta(seconds=job.recurring_seconds)
                        else:
                            del self.jobs[job_id]
                time.sleep(poll_interval)

        self._thread = threading.Thread(target=loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
