"""
Vyom - Vector / Semantic Memory (pure Python, no scikit-learn needed)
Meaning ke hisaab se search karta hai — TF-IDF khud implement kiya hai,
taaki phone/Android par heavy libraries (scikit-learn/scipy) install
nahi karni padein.
"""

import json
import sqlite3
import math
import re
from collections import Counter


def tokenize(text):
    return re.findall(r"[a-zA-Z0-9]+", text.lower())


def compute_tf(tokens):
    counts = Counter(tokens)
    total = len(tokens) or 1
    return {word: count / total for word, count in counts.items()}


def compute_idf(all_token_lists):
    n_docs = len(all_token_lists)
    doc_freq = Counter()
    for tokens in all_token_lists:
        for word in set(tokens):
            doc_freq[word] += 1
    return {word: math.log((n_docs + 1) / (freq + 1)) + 1 for word, freq in doc_freq.items()}


def compute_tfidf_vector(tokens, idf):
    tf = compute_tf(tokens)
    return {word: tf_val * idf.get(word, 0) for word, tf_val in tf.items()}


def cosine_similarity(vec1, vec2):
    common_words = set(vec1.keys()) & set(vec2.keys())
    dot_product = sum(vec1[w] * vec2[w] for w in common_words)
    mag1 = math.sqrt(sum(v * v for v in vec1.values()))
    mag2 = math.sqrt(sum(v * v for v in vec2.values()))
    if mag1 == 0 or mag2 == 0:
        return 0.0
    return dot_product / (mag1 * mag2)


class VectorMemory:
    def __init__(self, db_path="vyom_vector_memory.db", use_neural=False):
        self.db_path = db_path
        self._init_db()
        self.use_neural = False

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS vector_memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT,
                metadata TEXT,
                created_at TEXT
            )
        """)
        conn.commit()
        conn.close()

    def add(self, content, metadata=None):
        from datetime import datetime
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(
            "INSERT INTO vector_memories (content, metadata, created_at) VALUES (?, ?, ?)",
            (content, json.dumps(metadata or {}), datetime.utcnow().isoformat()),
        )
        conn.commit()
        conn.close()

    def _all_memories(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT id, content, metadata, created_at FROM vector_memories")
        rows = c.fetchall()
        conn.close()
        return [{"id": r[0], "content": r[1], "metadata": json.loads(r[2]), "created_at": r[3]} for r in rows]

    def semantic_search(self, query, top_k=5):
        memories = self._all_memories()
        if not memories:
            return []

        all_tokens = [tokenize(m["content"]) for m in memories]
        query_tokens = tokenize(query)

        idf = compute_idf(all_tokens + [query_tokens])
        query_vector = compute_tfidf_vector(query_tokens, idf)

        results = []
        for m, tokens in zip(memories, all_tokens):
            doc_vector = compute_tfidf_vector(tokens, idf)
            sim = cosine_similarity(query_vector, doc_vector)
            if sim > 0:
                m["similarity"] = sim
                results.append(m)

        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:top_k]
