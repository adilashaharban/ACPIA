# -*- coding: utf-8 -*-
"""Context builder module."""

from typing import List, Set
from backend.agents.rag.schema import RetrievedChunk, RetrievalContext

class ContextBuilder:
    """Builds RetrievalContext blocks for downstream reasoning agents."""
    
    @staticmethod
    def build_context(retrieved: List[RetrievedChunk], token_budget: int = 4096) -> RetrievalContext:
        """Consolidates text outputs and deduplicates references.
        
        Args:
            retrieved: Retrieved chunks list.
            token_budget: Upper limit for text sizing.
            
        Returns:
            Structured RetrievalContext object.
        """
        context_parts = []
        accumulated_tokens = 0
        
        ev_ids: Set[str] = set()
        ent_ids: Set[str] = set()
        tl_ids: Set[str] = set()
        nd_ids: Set[str] = set()
        ed_ids: Set[str] = set()
        cl_ids: Set[str] = set()
        
        # Sort by rank ascending
        sorted_chunks = sorted(retrieved, key=lambda x: x.rank)
        
        for item in sorted_chunks:
            c = item.chunk
            # Token budget ceiling check
            if accumulated_tokens + c.token_count > token_budget:
                continue
                
            context_parts.append(f"[{c.chunk_id}] (Evidence: {c.evidence_id}): {c.text}")
            accumulated_tokens += c.token_count
            
            # Aggregate source metrics
            ev_ids.add(c.evidence_id)
            ent_ids.update(c.source.entity_ids)
            tl_ids.update(c.source.timeline_event_ids)
            nd_ids.update(c.source.graph_node_ids)
            ed_ids.update(c.source.graph_edge_ids)
            cl_ids.update(c.source.correlation_cluster_ids)
            
        context_text = "\n\n".join(context_parts)
        
        return RetrievalContext(
            total_tokens=accumulated_tokens,
            context_text=context_text,
            evidence_ids=list(ev_ids),
            entity_ids=list(ent_ids),
            timeline_event_ids=list(tl_ids),
            graph_node_ids=list(nd_ids),
            graph_edge_ids=list(ed_ids),
            correlation_cluster_ids=list(cl_ids)
        )
export_context_builder = ContextBuilder
