"""
Vyom - Background Daemon (24/7 always-on mode)
Voice + autonomous worker + scheduler sab ek saath hamesha chalate hain.
"""

import time
import signal
import sys
from orchestrator import VyomOrchestrator
from security_brain import UserLevel


class VyomBackgroundDaemon:
    def __init__(self, mode="cloud", user_id="default_user", user_level=UserLevel.TRUSTED,
                 enable_voice=True, enable_autonomy=True, enable_scheduler=True):
        self.orchestrator = VyomOrchestrator(mode=mode)
        self.user_id = user_id
        self.user_level = user_level
        self.enable_voice = enable_voice
        self.enable_autonomy = enable_autonomy
        self.enable_scheduler = enable_scheduler
        self._running = False

    def _on_voice_command(self, command):
        response = self.orchestrator.handle_message(self.user_id, self.user_level, command)
        self.orchestrator.vector_memory.add(
            "User said: " + command + " | Vyom replied: " + response,
            metadata={"source": "voice", "user_id": self.user_id},
        )
        self.orchestrator.feedback_logger.log_interaction(self.user_id, command, response)
        try:
            self.orchestrator.voice.speak(response)
        except Exception:
            pass

    def start(self):
        self._running = True
        print("[Vyom Daemon] Starting 24/7 background mode...")

        if self.enable_voice:
            try:
                self.orchestrator.wake_word_listener.on_command = self._on_voice_command
                self.orchestrator.wake_word_listener.start()
                print("[Vyom Daemon] Wake-word listener active.")
            except Exception as e:
                print("[Vyom Daemon] Voice listener start nahi ho saka: " + str(e))

        if self.enable_autonomy:
            self.orchestrator.autonomous_worker.start()
            print("[Vyom Daemon] Autonomous worker active.")

        if self.enable_scheduler:
            self.orchestrator.scheduler.start()
            print("[Vyom Daemon] Task scheduler active.")

        print("[Vyom Daemon] Ab hamesha ke liye chal raha hai. Ctrl+C se rokne ke liye.")

        signal.signal(signal.SIGINT, self._handle_shutdown)
        signal.signal(signal.SIGTERM, self._handle_shutdown)

        while self._running:
            time.sleep(1)

    def _handle_shutdown(self, signum, frame):
        print("\n[Vyom Daemon] Shutdown signal mila, safely ruk raha hoon...")
        self.stop()
        sys.exit(0)

    def stop(self):
        self._running = False
        try:
            self.orchestrator.wake_word_listener.stop()
        except Exception:
            pass
        self.orchestrator.autonomous_worker.stop()
        self.orchestrator.scheduler.stop()


if __name__ == "__main__":
    daemon = VyomBackgroundDaemon(mode="cloud")
    daemon.start()
