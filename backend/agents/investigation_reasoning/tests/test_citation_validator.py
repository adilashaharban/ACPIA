# -*- coding: utf-8 -*-
"""Unit tests for CitationValidator."""

import pytest
from backend.agents.investigation_reasoning.citation_validator import CitationValidator
from backend.agents.investigation_reasoning.exceptions import CitationError
from backend.agents.investigation_reasoning.schema import FindingCitation
from backend.agents.rag.schema import RetrievalPackage
from backend.schemas.common import SourceReference, DocumentElementType

def test_citation_validator_mismatch(mock_retrieval_package: RetrievalPackage) -> None:
    """Verifies that invalid/hallucinated chunk IDs raise CitationError."""
    ref = SourceReference(
        evidence_id="EVID-1",
        file_path="mock.txt",
        page_number=1,
        parser="test",
        parser_version="1.0.0",
        source_element=DocumentElementType.PARAGRAPH
    )
    
    cit = FindingCitation(
        evidence_id="EVID-REAS-1",
        source_reference=ref,
        chunk_id="CHK-BAD",
        retrieval_rank=1
    )
    
    with pytest.raises(CitationError):
        CitationValidator.validate_citations([cit], mock_retrieval_package)
export_test_citation_validator = test_citation_validator_mismatch
