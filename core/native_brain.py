"""
Vyom - Native Trainable Brain (khud ka dimag)
Pure Python neural network, koi PyTorch/API nahi. Tumhare text se seekhta hai.
HONEST: chhota, simple, character-level hai. Real conversation nahi kar payega.
"""

import json
import math
import random
import os


class NativeBrain:
    def __init__(self, context_length=4, hidden_size=24, weights_file="vyom_native_brain.json"):
        self.context_length = context_length
        self.hidden_size = hidden_size
        self.weights_file = weights_file
        self.vocab = []
        self.char_to_idx = {}
        self.idx_to_char = {}
        self.W1 = None
        self.b1 = None
        self.W2 = None
        self.b2 = None
        self._load_if_exists()

    def _build_vocab(self, text):
        chars = sorted(set(text))
        self.vocab = chars
        self.char_to_idx = {c: i for i, c in enumerate(chars)}
        self.idx_to_char = {i: c for i, c in enumerate(chars)}

    def _init_weights(self):
        vocab_size = len(self.vocab)
        input_size = vocab_size * self.context_length
        scale1 = 1.0 / math.sqrt(input_size) if input_size else 0.1
        scale2 = 1.0 / math.sqrt(self.hidden_size)
        self.W1 = [[random.gauss(0, scale1) for _ in range(self.hidden_size)] for _ in range(input_size)]
        self.b1 = [0.0 for _ in range(self.hidden_size)]
        self.W2 = [[random.gauss(0, scale2) for _ in range(vocab_size)] for _ in range(self.hidden_size)]
        self.b2 = [0.0 for _ in range(vocab_size)]

    def _one_hot_context(self, context_chars):
        vocab_size = len(self.vocab)
        x = [0.0] * (vocab_size * self.context_length)
        for i, ch in enumerate(context_chars):
            idx = self.char_to_idx.get(ch)
            if idx is not None:
                x[i * vocab_size + idx] = 1.0
        return x

    def _forward(self, x):
        hidden = []
        for j in range(self.hidden_size):
            s = self.b1[j]
            for i, xi in enumerate(x):
                if xi:
                    s += xi * self.W1[i][j]
            hidden.append(math.tanh(s))

        vocab_size = len(self.vocab)
        logits = []
        for k in range(vocab_size):
            s = self.b2[k]
            for j in range(self.hidden_size):
                s += hidden[j] * self.W2[j][k]
            logits.append(s)

        max_logit = max(logits)
        exps = [math.exp(l - max_logit) for l in logits]
        total = sum(exps)
        probs = [e / total for e in exps]
        return x, hidden, probs

    def train_on_text(self, text, epochs=10, learning_rate=0.1):
        if not text or len(text) <= self.context_length:
            return {"ok": False, "error": "Text bahut chhota hai training ke liye."}

        if not self.vocab:
            self._build_vocab(text)
            self._init_weights()

        vocab_size = len(self.vocab)
        samples = []
        for i in range(len(text) - self.context_length):
            context = text[i:i + self.context_length]
            target = text[i + self.context_length]
            if target in self.char_to_idx:
                samples.append((context, target))

        losses = []
        for epoch in range(epochs):
            random.shuffle(samples)
            total_loss = 0.0
            for context, target in samples:
                x = self._one_hot_context(context)
                x, hidden, probs = self._forward(x)
                target_idx = self.char_to_idx[target]
                total_loss += -math.log(max(probs[target_idx], 1e-9))

                dlogits = list(probs)
                dlogits[target_idx] -= 1.0

                dhidden = [0.0] * self.hidden_size
                for j in range(self.hidden_size):
                    s = 0.0
                    for k in range(vocab_size):
                        s += self.W2[j][k] * dlogits[k]
                    dhidden[j] = s * (1 - hidden[j] * hidden[j])

                for j in range(self.hidden_size):
                    for k in range(vocab_size):
                        self.W2[j][k] -= learning_rate * hidden[j] * dlogits[k]

                for k in range(vocab_size):
                    self.b2[k] -= learning_rate * dlogits[k]

                for i2, xi in enumerate(x):
                    if xi:
                        for j in range(self.hidden_size):
                            self.W1[i2][j] -= learning_rate * dhidden[j] * xi

                for j in range(self.hidden_size):
                    self.b1[j] -= learning_rate * dhidden[j]

            avg_loss = total_loss / max(len(samples), 1)
            losses.append(avg_loss)

        self._save()
        return {"ok": True, "epochs": epochs, "samples": len(samples), "final_loss": round(losses[-1], 4)}

    def predict_next_char(self, context, temperature=1.0):
        if not self.vocab:
            return None
        context = context[-self.context_length:].rjust(self.context_length, " ")
        x = self._one_hot_context(context)
        _, _, probs = self._forward(x)

        if temperature != 1.0:
            probs = [p ** (1.0 / temperature) for p in probs]
            total = sum(probs)
            probs = [p / total for p in probs]

        r = random.random()
        cumulative = 0.0
        for i, p in enumerate(probs):
            cumulative += p
            if r <= cumulative:
                return self.idx_to_char[i]
        return self.idx_to_char[len(probs) - 1]

    def generate(self, seed_text, length=100, temperature=0.8):
        if not self.vocab:
            return "[NativeBrain] Abhi train nahi hua hai. Pehle train_on_text() call karo."
        result = seed_text
        for _ in range(length):
            next_char = self.predict_next_char(result, temperature=temperature)
            if next_char is None:
                break
            result += next_char
        return result

    def _save(self):
        data = {
            "vocab": self.vocab, "context_length": self.context_length,
            "hidden_size": self.hidden_size, "W1": self.W1, "b1": self.b1,
            "W2": self.W2, "b2": self.b2,
        }
        with open(self.weights_file, "w", encoding="utf-8") as f:
            json.dump(data, f)

    def _load_if_exists(self):
        if os.path.exists(self.weights_file):
            with open(self.weights_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.vocab = data["vocab"]
            self.char_to_idx = {c: i for i, c in enumerate(self.vocab)}
            self.idx_to_char = {i: c for i, c in enumerate(self.vocab)}
            self.context_length = data["context_length"]
            self.hidden_size = data["hidden_size"]
            self.W1 = data["W1"]
            self.b1 = data["b1"]
            self.W2 = data["W2"]
            self.b2 = data["b2"]
