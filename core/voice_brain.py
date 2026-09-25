"""
Vyom - Voice Brain
Real STT/TTS integration.
SETUP: pip install SpeechRecognition pyttsx3 pyaudio
"""


class VoiceBrain:
    def __init__(self, wake_word="vyom"):
        self.wake_word = wake_word.lower()
        self.listening = False
        self._recognizer = None
        self._tts_engine = None

    def _lazy_init_stt(self):
        if self._recognizer is None:
            import speech_recognition as sr
            self._recognizer = sr.Recognizer()

    def _lazy_init_tts(self):
        if self._tts_engine is None:
            import pyttsx3
            self._tts_engine = pyttsx3.init()

    def detect_wake_word(self, audio_transcript_chunk):
        return self.wake_word in audio_transcript_chunk.lower()

    def listen_from_microphone(self, timeout=5, phrase_time_limit=10, use_offline=False, offline_model_path=None):
        if use_offline:
            from offline_voice import VoskOfflineSTT
            if not offline_model_path:
                return "[Vyom Voice Error] Offline mode ke liye offline_model_path do."
            stt = VoskOfflineSTT(offline_model_path)
            return stt.listen_once_offline(duration_seconds=phrase_time_limit)

        import speech_recognition as sr
        self._lazy_init_stt()

        with sr.Microphone() as source:
            self._recognizer.adjust_for_ambient_noise(source, duration=0.5)
            try:
                audio = self._recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            except sr.WaitTimeoutError:
                return ""

        try:
            text = self._recognizer.recognize_google(audio, language="hi-IN")
            return text
        except sr.UnknownValueError:
            return ""
        except sr.RequestError as e:
            return "[Vyom Voice Error] Speech recognition service error: " + str(e)

    def transcribe(self, audio_bytes):
        import speech_recognition as sr
        import io
        self._lazy_init_stt()
        with sr.AudioFile(io.BytesIO(audio_bytes)) as source:
            audio = self._recognizer.record(source)
        try:
            return self._recognizer.recognize_google(audio, language="hi-IN")
        except Exception as e:
            return "[Vyom Voice Error] " + str(e)

    def speak(self, text):
        import pyttsx3
        self._lazy_init_tts()
        self._tts_engine.say(text)
        self._tts_engine.runAndWait()

    def handle_interrupt(self):
        if self._tts_engine:
            self._tts_engine.stop()
        self.listening = False
