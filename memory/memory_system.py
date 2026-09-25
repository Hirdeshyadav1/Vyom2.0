"""
Vyom - Memory System
Long-term memory, working memory, episodic memory, semantic memory.
"""

import json
import sqlite3
from datetime import datetime


class WorkingMemory:
    def __init__(self):
        self.state = {
            "current_conversation": [],
            "current_task": None,
            "current_files": [],
            "current_application": None,
            "temp_vars": {},
            "current_objective": None,
        }

    def update(self, key, value):
        self.state[key] = value

    def append_message(self, role, content):
        self.state["current_conversation"].append({"role": role, "content": content})

    def get(self, key, default=None):
        return self.state.get(key, default)

    def clear(self):
        self.__init__()


class LongTermMemory:
    def __init__(self, db_path="vyom_memory.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT,
                content TEXT,
                metadata TEXT,
                created_at TEXT
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS episodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                summary TEXT,
                outcome TEXT,
                metadata TEXT,
                created_at TEXT
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS semantic_facts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                concept TEXT,
                relation TEXT,
                target TEXT,
                created_at TEXT
            )
        """)
        conn.commit()
        conn.close()

    def store(self, category, content, metadata=None):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(
            "INSERT INTO memories (category, content, metadata, created_at) VALUES (?, ?, ?, ?)",
            (category, content, json.dumps(metadata or {}), datetime.utcnow().isoformat()),
        )
        conn.commit()
        conn.close()

    def store_episode(self, summary, outcome, metadata=None):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(
            "INSERT INTO episodes (summary, outcome, metadata, created_at) VALUES (?, ?, ?, ?)",
            (summary, outcome, json.dumps(metadata or {}), datetime.utcnow().isoformat()),
        )
        conn.commit()
        conn.close()

    def store_fact(self, concept, relation, target):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(
            "INSERT INTO semantic_facts (concept, relation, target, created_at) VALUES (?, ?, ?, ?)",
            (concept, relation, target, datetime.utcnow().isoformat()),
        )
        conn.commit()
        conn.close()

    def search(self, keyword, category=None, limit=10):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        query = "SELECT id, category, content, metadata, created_at FROM memories WHERE content LIKE ?"
        params = ["%" + keyword + "%"]
        if category:
            query += " AND category = ?"
            params.append(category)
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        c.execute(query, params)
        rows = c.fetchall()
        conn.close()
        return [
            {"id": r[0], "category": r[1], "content": r[2], "metadata": json.loads(r[3]), "created_at": r[4]}
            for r in rows
        ]

    def get_past_episodes(self, keyword=None, limit=10):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        if keyword:
            c.execute(
                "SELECT id, summary, outcome, metadata, created_at FROM episodes WHERE summary LIKE ? ORDER BY created_at DESC LIMIT ?",
                ("%" + keyword + "%", limit),
            )
        else:
            c.execute(
                "SELECT id, summary, outcome, metadata, created_at FROM episodes ORDER BY created_at DESC LIMIT ?",
                (limit,),
            )
        rows = c.fetchall()
        conn.close()
        return [
            {"id": r[0], "summary": r[1], "outcome": r[2], "metadata": json.loads(r[3]), "created_at": r[4]}
            for r in rows
        ]

    def get_related_facts(self, concept):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(
            "SELECT concept, relation, target FROM semantic_facts WHERE concept LIKE ? OR target LIKE ?",
            ("%" + concept + "%", "%" + concept + "%"),
        )
        rows = c.fetchall()
        conn.close()
        return [{"concept": r[0], "relation": r[1], "target": r[2]} for r in rows]


class MemorySystem:
    def __init__(self, db_path="vyom_memory.db"):
        self.working = WorkingMemory()
        self.long_term = LongTermMemory(db_path)

    def remember_preference(self, text, metadata=None):
        self.long_term.store("preference", text, metadata)

    def remember_fact(self, text, metadata=None):
        self.long_term.store("fact", text, metadata)

    def remember_decision(self, text, metadata=None):
        self.long_term.store("decision", text, metadata)

    def recall(self, query, category=None):
        return self.long_term.search(query, category=category)

    def full_context(self, query=""):
        return {
            "working_memory": self.working.state,
            "relevant_memories": self.long_term.search(query) if query else [],
            "recent_episodes": self.long_term.get_past_episodes(limit=5),
        }
