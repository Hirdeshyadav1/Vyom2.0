"""
Vyom - Fully Offline Voice (Vosk-based STT)
SETUP: pip install vosk sounddevice
Model download karo: https://alphacephei.com/vosk/models
"""

import json
import queue


class VoskOfflineSTT:
    def __init__(self, model_path, sample_rate=16000):
        self.model_path = model_path
        self.sample_rate = sample_rate
        self._model = None
        self._recognizer = None
        self._audio_queue = queue.Queue()

    def _lazy_init(self):
        if self._model is None:
            from vosk import Model, KaldiRecognizer
            self._model = Model(self.model_path)
            self._recognizer = KaldiRecognizer(self._model, self.sample_rate)

    def listen_once_offline(self, duration_seconds=5):
        import sounddevice as sd

        self._lazy_init()

        def callback(indata, frames, time_info, status):
            self._audio_queue.put(bytes(indata))

        result_text = ""
        with sd.RawInputStream(samplerate=self.sample_rate, blocksize=8000, dtype="int16", channels=1, callback=callback):
            frames_collected = 0
            max_frames = int(duration_seconds * self.sample_rate / 8000)
            while frames_collected < max_frames:
                data = self._audio_queue.get()
                frames_collected += 1
                if self._recognizer.AcceptWaveform(data):
                    res = json.loads(self._recognizer.Result())
                    result_text += " " + res.get("text", "")

            final = json.loads(self._recognizer.FinalResult())
            result_text += " " + final.get("text", "")

        return result_text.strip()

    def transcribe_file_offline(self, wav_path):
        import wave

        self._lazy_init()
        wf = wave.open(wav_path, "rb")
        result_text = ""
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if self._recognizer.AcceptWaveform(data):
                res = json.loads(self._recognizer.Result())
                result_text += " " + res.get("text", "")
        final = json.loads(self._recognizer.FinalResult())
        result_text += " " + final.get("text", "")
        wf.close()
        return result_text.strip()
