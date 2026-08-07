# -*- coding: utf-8 -*-
"""Hybrid retriever module."""

from typing import List, Dict, Tuple, Optional
from backend.agents.rag.schema import RetrievedChunk, RetrievalScore, RetrievalChunk, RetrievalMode, RetrievalFilter
from backend.agents.rag.constants import SEMANTIC_WEIGHT, KEYWORD_WEIGHT
from backend.agents.rag.keyword_index import KeywordIndex
from backend.agents.rag.vector_index import VectorIndex

class HybridRetriever:
    """Orchestrates multi-modal sparse/dense query searches."""
    
    def __init__(self, vector_index: VectorIndex, keyword_index: KeywordIndex) -> None:
        self.vector_index = vector_index
        self.keyword_index = keyword_index

    def retrieve(
        self,
        query: str,
        query_vector: List[float],
        retrieval_mode: RetrievalMode,
        top_k: int,
        filters: Optional[RetrievalFilter] = None
    ) -> List[RetrievedChunk]:
        """Retrieves and scores chunks using sparse/dense fusion.
        
        Args:
            query: Lexical query.
            query_vector: Semantic vector.
            retrieval_mode: Mode selection.
            top_k: Output count limit.
            filters: Optional metadata filter parameters.
            
        Returns:
            List of RetrievedChunk results.
        """
        # Fetch candidates
        vec_results = self.vector_index.search(query_vector, top_k * 2) if retrieval_mode in [RetrievalMode.SEMANTIC, RetrievalMode.HYBRID] else []
        kw_results = self.keyword_index.search(query, top_k * 2) if retrieval_mode in [RetrievalMode.KEYWORD, RetrievalMode.HYBRID] else []
        
        # Apply filters
        if filters:
            vec_results = [(c, s) for c, s in vec_results if self._matches_filter(c, filters)]
            kw_results = [(c, s) for c, s in kw_results if self._matches_filter(c, filters)]
            
        # Map scoring
        chunk_map: Dict[str, RetrievalChunk] = {}
        semantic_scores: Dict[str, float] = {}
        keyword_scores: Dict[str, float] = {}
        
        for c, s in vec_results:
            chunk_map[c.chunk_id] = c
            semantic_scores[c.chunk_id] = s
            
        for c, s in kw_results:
            chunk_map[c.chunk_id] = c
            keyword_scores[c.chunk_id] = s
            
        all_ids = set(semantic_scores.keys()) | set(keyword_scores.keys())
        
        retrieved_list = []
        for cid in all_ids:
            chunk = chunk_map[cid]
            s_score = semantic_scores.get(cid, 0.0)
            k_score = keyword_scores.get(cid, 0.0)
            
            # Compute fusion
            if retrieval_mode == RetrievalMode.SEMANTIC:
                fused = s_score
            elif retrieval_mode == RetrievalMode.KEYWORD:
                fused = k_score
            else:
                fused = (s_score * SEMANTIC_WEIGHT) + (k_score * KEYWORD_WEIGHT)
                
            retrieved_list.append(
                RetrievedChunk(
                    chunk=chunk,
                    score=RetrievalScore(
                        semantic_score=round(s_score, 4),
                        keyword_score=round(k_score, 4),
                        fused_score=round(fused, 4)
                    ),
                    rank=1
                )
            )
            
        # Sort and rank
        retrieved_list.sort(key=lambda x: x.score.fused_score, reverse=True)
        for rank, item in enumerate(retrieved_list):
            item.rank = rank + 1
            
        return retrieved_list[:top_k]

    def _matches_filter(self, chunk: RetrievalChunk, f: RetrievalFilter) -> bool:
        if f.case_id and chunk.source.case_id != f.case_id:
            return False
        if f.evidence_ids and chunk.evidence_id not in f.evidence_ids:
            return False
        if f.entity_ids and not any(eid in chunk.source.entity_ids for eid in f.entity_ids):
            return False
        if f.modalities and chunk.chunk_type not in f.modalities:
            return False
        return True
export_hybrid_retriever = HybridRetriever
