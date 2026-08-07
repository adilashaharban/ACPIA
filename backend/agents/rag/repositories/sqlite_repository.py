# -*- coding: utf-8 -*-
"""SQLite RAG repository implementation."""

import json
import sqlite3
from typing import List, Optional, Tuple
from backend.agents.rag.repositories.base_repository import RAGRepository
from backend.agents.rag.schema import RetrievalChunk
from backend.agents.rag.exceptions import RepositoryError

class SQLiteRepository(RAGRepository):
    """Stores text chunks and metadata schemas inside a local SQLite table."""
    
    def __init__(self, db_path: str = ":memory:") -> None:
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self._init_db()

    def _init_db(self) -> None:
        try:
            self.conn.execute(
                """CREATE TABLE IF NOT EXISTS retrieval_chunks (
                    chunk_id TEXT PRIMARY KEY,
                    evidence_id TEXT,
                    chunk_data TEXT
                )"""
            )
            self.conn.commit()
        except Exception as e:
            raise RepositoryError(f"Failed to initialize SQLite RAG database: {e}")

    def build_index(self) -> None:
        pass

    def add_chunks(self, chunks: List[RetrievalChunk]) -> None:
        try:
            for c in chunks:
                self.conn.execute(
                    "INSERT OR REPLACE INTO retrieval_chunks (chunk_id, evidence_id, chunk_data) VALUES (?, ?, ?)",
                    (c.chunk_id, c.evidence_id, c.model_dump_json())
                )
            self.conn.commit()
        except Exception as e:
            raise RepositoryError(f"Failed to save chunks to SQLite: {e}")

    def delete_chunks(self, chunk_ids: List[str]) -> None:
        try:
            for cid in chunk_ids:
                self.conn.execute("DELETE FROM retrieval_chunks WHERE chunk_id = ?", (cid,))
            self.conn.commit()
        except Exception as e:
            raise RepositoryError(f"Failed to delete chunks from SQLite: {e}")

    def search(self, query_vector: List[float], top_k: int) -> List[Tuple[RetrievalChunk, float]]:
        res = []
        for c in self.load_chunks()[:top_k]:
            res.append((c, 0.90))
        return res

    def rebuild(self) -> None:
        pass

    def optimize(self) -> None:
        pass

    def save_chunks(self, chunks: List[RetrievalChunk]) -> None:
        self.add_chunks(chunks)

    def load_chunks(self) -> List[RetrievalChunk]:
        try:
            chunks = []
            cursor = self.conn.execute("SELECT chunk_data FROM retrieval_chunks")
            for row in cursor.fetchall():
                chunks.append(RetrievalChunk.model_validate_json(row[0]))
            return chunks
        except Exception as e:
            raise RepositoryError(f"Failed to load chunks from SQLite: {e}")

    def clear_index(self) -> None:
        try:
            self.conn.execute("DELETE FROM retrieval_chunks")
            self.conn.commit()
        except Exception as e:
            raise RepositoryError(f"Failed to clear SQLite RAG: {e}")

    def get_chunk(self, chunk_id: str) -> Optional[RetrievalChunk]:
        try:
            cursor = self.conn.execute("SELECT chunk_data FROM retrieval_chunks WHERE chunk_id = ?", (chunk_id,))
            row = cursor.fetchone()
            if row:
                return RetrievalChunk.model_validate_json(row[0])
            return None
        except Exception as e:
            raise RepositoryError(f"Failed to fetch chunk {chunk_id} from SQLite: {e}")

    def exists(self, chunk_id: str) -> bool:
        return self.get_chunk(chunk_id) is not None

    def count(self) -> int:
        try:
            cursor = self.conn.execute("SELECT count(*) FROM retrieval_chunks")
            return cursor.fetchone()[0]
        except Exception as e:
            raise RepositoryError(f"Failed to count SQLite chunks: {e}")
export_sqlite_repository = SQLiteRepository
