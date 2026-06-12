"""
knowledge_base.py — SQLite + busca vetorial simples via cosine similarity.

Implementação minimalista sem dependências externas de embeddings:
usa TF simples (frequência de termos) para calcular similaridade entre
a query e os documentos armazenados.
"""

import sqlite3
import math
import os
from typing import List, Dict, Any


def _tokenize(text: str) -> List[str]:
    """Tokeniza texto em palavras minúsculas, removendo pontuação básica."""
    import re
    text = text.lower()
    tokens = re.findall(r"[a-záàâãéèêíïóôõöúüçñ0-9]+", text)
    return tokens


def _tf_vector(tokens: List[str]) -> Dict[str, float]:
    """Calcula frequência normalizada de termos (TF)."""
    counts: Dict[str, float] = {}
    for t in tokens:
        counts[t] = counts.get(t, 0) + 1
    total = len(tokens) or 1
    return {t: c / total for t, c in counts.items()}


def _cosine_similarity(vec_a: Dict[str, float], vec_b: Dict[str, float]) -> float:
    """Cosine similarity entre dois vetores TF representados como dicts."""
    common = set(vec_a.keys()) & set(vec_b.keys())
    if not common:
        return 0.0
    dot = sum(vec_a[t] * vec_b[t] for t in common)
    norm_a = math.sqrt(sum(v ** 2 for v in vec_a.values()))
    norm_b = math.sqrt(sum(v ** 2 for v in vec_b.values()))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


class KnowledgeBase:
    """Base de conhecimento local com SQLite e busca por similaridade TF."""

    def __init__(self, db_path: str = "./data/knowledge_base.db"):
        self.db_path = db_path
        self._mem_conn: sqlite3.Connection | None = None
        if db_path == ":memory:":
            self._mem_conn = sqlite3.connect(":memory:")
        else:
            os.makedirs(os.path.dirname(db_path) if os.path.dirname(db_path) else ".", exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        if self._mem_conn is not None:
            return self._mem_conn
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    category TEXT DEFAULT 'geral',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def insert(self, title: str, content: str, category: str = "geral") -> int:
        """Insere documento na base. Retorna o ID gerado."""
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO documents (title, content, category) VALUES (?, ?, ?)",
                (title, content, category),
            )
            conn.commit()
            return cur.lastrowid

    def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Busca documentos relevantes usando cosine similarity TF.
        Retorna lista de dicts com id, title, content, category, score.
        """
        query_vec = _tf_vector(_tokenize(query))

        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, title, content, category FROM documents"
            ).fetchall()

        scored = []
        for row_id, title, content, category in rows:
            doc_text = f"{title} {content}"
            doc_vec = _tf_vector(_tokenize(doc_text))
            score = _cosine_similarity(query_vec, doc_vec)
            scored.append({
                "id": row_id,
                "title": title,
                "content": content,
                "category": category,
                "score": round(score, 4),
            })

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:max_results]

    def count(self) -> int:
        """Retorna total de documentos na base."""
        with self._connect() as conn:
            return conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]

    def delete(self, doc_id: int) -> bool:
        """Remove documento por ID. Retorna True se removeu."""
        with self._connect() as conn:
            cur = conn.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
            conn.commit()
            return cur.rowcount > 0
