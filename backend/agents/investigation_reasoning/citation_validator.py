# -*- coding: utf-8 -*-
"""Citation validator module."""

from typing import List
from backend.agents.investigation_reasoning.exceptions import CitationError
from backend.agents.investigation_reasoning.schema import FindingCitation
from backend.agents.rag.schema import RetrievalPackage

class CitationValidator:
    """Verifies that all citation entries exist in the underlying retrieval context."""
    
    @staticmethod
    def validate_citations(
        citations: List[FindingCitation],
        retrieval_pkg: RetrievalPackage
    ) -> None:
        """Checks citation mappings.
        
        Args:
            citations: Citations list.
            retrieval_pkg: Original retrieval context.
        """
        valid_chunks_ids = {rc.chunk.chunk_id for rc in retrieval_pkg.retrieved_chunks}
        valid_evidence_ids = {rc.chunk.evidence_id for rc in retrieval_pkg.retrieved_chunks}
        
        for cit in citations:
            if cit.chunk_id not in valid_chunks_ids:
                raise CitationError(f"Citation validation failed: chunk_id {cit.chunk_id} does not exist in retrieval context.")
            if cit.evidence_id not in valid_evidence_ids:
                raise CitationError(f"Citation validation failed: evidence_id {cit.evidence_id} does not exist in retrieval context.")
export_citation_validator = CitationValidator
