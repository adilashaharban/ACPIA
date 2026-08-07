# -*- coding: utf-8 -*-
"""Unit tests for CitationBuilder."""

from backend.agents.investigation_reasoning.citation_builder import CitationBuilder
from backend.agents.rag.schema import RetrievalPackage

def test_citation_builder(mock_retrieval_package: RetrievalPackage) -> None:
    """Verifies citations resolve to valid chunks and retrieval ranks."""
    raw_citations = [
        {"chunk_id": "CHK-1"}
    ]
    
    citations = CitationBuilder.build_citations(raw_citations, mock_retrieval_package)
    assert len(citations) == 1
    assert citations[0].chunk_id == "CHK-1"
    assert citations[0].retrieval_rank == 1
