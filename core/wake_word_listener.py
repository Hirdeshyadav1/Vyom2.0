"""
Vyom - Wake-Word Auto-Listener (low-latency, continuous background listening)
SETUP: pip install SpeechRecognition pyaudio
"""

import threading


class WakeWordListener:
    def __init__(self, voice_brain, on_command, energy_threshold=300):
        self.voice_brain = voice_brain
        self.on_command = on_command
        self.energy_threshold = energy_threshold
        self._stop_listening = None
        self._recognizer = None
        self._mic = None
        self._running = False

    def _on_audio(self, recognizer, audio):
        try:
            text = recognizer.recognize_google(audio, language="hi-IN")
        except Exception:
            return

        if not text:
            return

        if self.voice_brain.detect_wake_word(text):
            remainder = text.lower().split(self.voice_brain.wake_word, 1)
            command = remainder[1].strip() if len(remainder) > 1 and remainder[1].strip() else None

            if command:
                threading.Thread(target=self.on_command, args=(command,), daemon=True).start()
            else:
                threading.Thread(target=self.voice_brain.speak, args=("Haan?",), daemon=True).start()

    def start(self):
        import speech_recognition as sr

        if self._running:
            return

        self._recognizer = sr.Recognizer()
        self._recognizer.energy_threshold = self.energy_threshold
        self._recognizer.dynamic_energy_threshold = True
        self._mic = sr.Microphone()

        with self._mic as source:
            self._recognizer.adjust_for_ambient_noise(source, duration=1)

        self._stop_listening = self._recognizer.listen_in_background(self._mic, self._on_audio, phrase_time_limit=6)
        self._running = True

    def stop(self):
        if self._stop_listening:
            self._stop_listening(wait_for_stop=False)
        self._running = False
