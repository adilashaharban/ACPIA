# -*- coding: utf-8 -*-
"""Unit tests for DocumentIntelligencePipeline."""

import pytest
from backend.agents.base import AgentResultContract
from backend.agents.document_intelligence.dispatcher import DocumentDispatcher
from backend.agents.document_intelligence.normalizer import DocumentNormalizer
from backend.agents.document_intelligence.validator import DocumentValidator
from backend.agents.document_intelligence.metrics import DocumentMetricsCalculator
from backend.agents.document_intelligence.pipeline import DocumentIntelligencePipeline
from backend.agents.document_intelligence.exceptions import ChecksumMismatchError

def test_pipeline_happy_path(metadata_result_contract: AgentResultContract) -> None:
    """Verifies standard pipeline executions on text file."""
    dispatcher = DocumentDispatcher()
    validator = DocumentValidator()
    normalizer = DocumentNormalizer()
    metrics_calc = DocumentMetricsCalculator()
    
    pipeline = DocumentIntelligencePipeline(
        dispatcher=dispatcher,
        validator=validator,
        normalizer=normalizer,
        metrics_calculator=metrics_calc
    )
    
    package, warnings = pipeline.execute(metadata_result_contract)
    
    # Assert successfully parsed details
    assert package.evidence_id == "EVID-DOC-100"
    assert package.summary.mime_type == "text/plain"
    assert package.summary.is_scanned is False
    assert package.statistics.page_count == 1
    assert len(package.raw_blocks) == 2
    assert "Line 1 text content." in [b.text for b in package.raw_blocks]
    assert len(warnings) == 0

def test_pipeline_checksum_mismatch(metadata_result_contract: AgentResultContract) -> None:
    """Verifies that pipeline fails when database hashes mismatch expected checksums."""
    dispatcher = DocumentDispatcher()
    validator = DocumentValidator()
    normalizer = DocumentNormalizer()
    metrics_calc = DocumentMetricsCalculator()
    
    pipeline = DocumentIntelligencePipeline(
        dispatcher=dispatcher,
        validator=validator,
        normalizer=normalizer,
        metrics_calculator=metrics_calc
    )
    
    # Pre-register modified hash to trigger integrity validation error
    from backend.database.session import get_db_context
    from backend.database.repositories.evidence_repository import EvidenceRepository
    
    with get_db_context() as db:
        repo = EvidenceRepository(db)
        db_ev = repo.get_by_id("EVID-DOC-100")
        db_ev.sha256_hash = "wrongchecksum"
        db.commit()
        
    with pytest.raises(ChecksumMismatchError):
        pipeline.execute(metadata_result_contract)
