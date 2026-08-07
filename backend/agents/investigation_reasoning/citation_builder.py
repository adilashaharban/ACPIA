# -*- coding: utf-8 -*-
"""Citation builder module."""

from typing import List, Dict, Any
from backend.agents.rag.schema import RetrievalPackage
from backend.agents.investigation_reasoning.schema import FindingCitation

class CitationBuilder:
    """Matches raw LLM references to valid RetrievalPackage source references."""
    
    @staticmethod
    def build_citations(
        raw_citations: List[Dict[str, Any]],
        retrieval_pkg: RetrievalPackage
    ) -> List[FindingCitation]:
        """Assembles valid citation items.
        
        Args:
            raw_citations: Citations returned from LLM.
            retrieval_pkg: Base RetrievalPackage context.
            
        Returns:
            FindingCitation list.
        """
        citations = []
        if not raw_citations or not retrieval_pkg:
            return citations
            
        # Map chunks by ID and evidence context
        chunk_map = {rc.chunk.chunk_id: rc for rc in retrieval_pkg.retrieved_chunks}
        
        for rc in raw_citations:
            cid = rc.get("chunk_id")
            ev_id = rc.get("evidence_id")
            
            # Attempt lookup
            ret_chunk = chunk_map.get(cid)
            if ret_chunk:
                citations.append(
                    FindingCitation(
                        evidence_id=ret_chunk.chunk.evidence_id,
                        source_reference=ret_chunk.chunk.source.source_reference,
                        chunk_id=cid,
                        retrieval_rank=ret_chunk.rank
                    )
                )
            elif ev_id:
                # Fallback to evidence citation if chunk reference missing
                # Find first chunk matching evidence_id
                matched = None
                for c in retrieval_pkg.retrieved_chunks:
                    if c.chunk.evidence_id == ev_id:
                        matched = c
                        break
                if matched:
                    citations.append(
                        FindingCitation(
                            evidence_id=ev_id,
                            source_reference=matched.chunk.source.source_reference,
                            chunk_id=matched.chunk.chunk_id,
                            retrieval_rank=matched.rank
                        )
                    )
                    
        return citations
export_citation_builder = CitationBuilder
