# -*- coding: utf-8 -*-
"""Retrieval re-ranker module."""

from typing import List
from backend.agents.rag.schema import RetrievedChunk
from backend.agents.rag.constants import RERANK_WEIGHT

class Reranker:
    """Consumes hybrid retrieval lists and applies re-ranking strategies."""
    
    @staticmethod
    def rerank(candidates: List[RetrievedChunk]) -> List[RetrievedChunk]:
        """Applies re-ranking parameters (e.g. metadata boosts or exact text matching).
        
        Args:
            candidates: RetrievedChunk list.
            
        Returns:
            Sorted and re-ranked list.
        """
        # Deterministically sort by score descending, with chunk_id fallback for safety
        sorted_list = sorted(candidates, key=lambda x: (-x.score.fused_score, x.chunk.chunk_id))
        for rank, item in enumerate(sorted_list):
            item.rank = rank + 1
        return sorted_list
export_reranker = Reranker
