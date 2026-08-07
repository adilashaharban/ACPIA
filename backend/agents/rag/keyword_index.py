# -*- coding: utf-8 -*-
"""BM25 Lexical Keyword search index."""

import math
from typing import List, Dict, Tuple
from backend.agents.rag.schema import RetrievalChunk

class KeywordIndex:
    """Computes deterministic BM25 scores for chunks mapping."""
    
    def __init__(self, k1: float = 1.5, b: float = 0.75) -> None:
        self.k1 = k1
        self.b = b
        self._chunks: Dict[str, RetrievalChunk] = {}
        # Document frequencies for words
        self._df: Dict[str, int] = {}
        # Average document word length
        self._avg_dl = 0.0

    def add_chunks(self, chunks: List[RetrievalChunk]) -> None:
        for c in chunks:
            self._chunks[c.chunk_id] = c
        self._rebuild_stats()

    def delete_chunks(self, chunk_ids: List[str]) -> None:
        for cid in chunk_ids:
            self._chunks.pop(cid, None)
        self._rebuild_stats()

    def clear(self) -> None:
        self._chunks.clear()
        self._df.clear()
        self._avg_dl = 0.0

    def _rebuild_stats(self) -> None:
        self._df.clear()
        if not self._chunks:
            self._avg_dl = 0.0
            return
            
        total_len = 0
        for c in self._chunks.values():
            words = set(c.text.lower().split())
            for w in words:
                self._df[w] = self._df.get(w, 0) + 1
            total_len += len(c.text.split())
            
        self._avg_dl = total_len / len(self._chunks)

    def search(self, query: str, top_k: int) -> List[Tuple[RetrievalChunk, float]]:
        """Calculates standard BM25 ranking.
        
        Args:
            query: User search string.
            top_k: Return limits.
            
        Returns:
            List of (RetrievalChunk, score).
        """
        results = []
        q_tokens = query.lower().split()
        if not self._chunks or not q_tokens:
            return []
            
        n = len(self._chunks)
        
        for c in self._chunks.values():
            c_words = c.text.lower().split()
            dl = len(c_words)
            c_tf: Dict[str, int] = {}
            for w in c_words:
                c_tf[w] = c_tf.get(w, 0) + 1
                
            score = 0.0
            for t in q_tokens:
                tf = c_tf.get(t, 0)
                df = self._df.get(t, 0)
                
                # Inverse Document Frequency (IDF) with smoothing
                idf = math.log((n - df + 0.5) / (df + 0.5) + 1.0)
                
                numerator = tf * (self.k1 + 1.0)
                denominator = tf + self.k1 * (1.0 - self.b + self.b * (dl / (self._avg_dl or 1.0)))
                score += idf * (numerator / denominator)
                
            results.append((c, score))
            
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
export_keyword_index = KeywordIndex
