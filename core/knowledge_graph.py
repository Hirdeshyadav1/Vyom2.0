"""
Vyom - Knowledge Graph
Simple SQLite-backed graph: nodes aur relationships.
"""

import sqlite3


class KnowledgeGraph:
    def __init__(self, db_path="vyom_knowledge_graph.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS edges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT,
                relation TEXT,
                target TEXT
            )
        """)
        conn.commit()
        conn.close()

    def add_relationship(self, source, relation, target):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("INSERT INTO edges (source, relation, target) VALUES (?, ?, ?)", (source, relation, target))
        conn.commit()
        conn.close()

    def get_related(self, node):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT source, relation, target FROM edges WHERE source = ? OR target = ?", (node, node))
        rows = c.fetchall()
        conn.close()
        return rows

    def traverse(self, start, depth=2):
        visited = set()
        frontier = [start]
        result = {}
        for _ in range(depth):
            next_frontier = []
            for node in frontier:
                if node in visited:
                    continue
                visited.add(node)
                edges = self.get_related(node)
                result[node] = edges
                for s, r, t in edges:
                    neighbor = t if s == node else s
                    if neighbor not in visited:
                        next_frontier.append(neighbor)
            frontier = next_frontier
        return result
