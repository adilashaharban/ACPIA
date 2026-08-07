# -*- coding: utf-8 -*-
"""Unit and integration tests for AudioIntelligencePipeline."""

import pytest
from backend.agents.base import AgentResultContract
from backend.agents.audio_intelligence.dispatcher import AudioDispatcher
from backend.agents.audio_intelligence.normalizer import AudioNormalizer
from backend.agents.audio_intelligence.validator import AudioValidator
from backend.agents.audio_intelligence.metrics import AudioMetricsCalculator
from backend.agents.audio_intelligence.pipeline import AudioIntelligencePipeline
from backend.agents.audio_intelligence.exceptions import ChecksumMismatchError

def test_pipeline_happy_path(metadata_result_contract: AgentResultContract) -> None:
    """Verifies that the complete pipeline execution generates correct AudioPackage results."""
    dispatcher = AudioDispatcher()
    validator = AudioValidator()
    normalizer = AudioNormalizer()
    metrics_calc = AudioMetricsCalculator()
    
    pipeline = AudioIntelligencePipeline(
        dispatcher=dispatcher,
        validator=validator,
        normalizer=normalizer,
        metrics_calculator=metrics_calc
    )
    
    package, warnings = pipeline.execute(metadata_result_contract)
    
    # Assert successfully parsed details
    assert package.evidence_id == "EVID-AUD-77"
    assert package.summary.mime_type == "audio/wav"
    assert len(package.transcript) == 1
    assert len(package.speakers) == 1
    assert len(package.silences) == 1
    assert len(package.sounds) == 1
    assert len(package.keywords) == 2  # matches "help" and "urgent" from transcript
    assert len(warnings) == 0

def test_pipeline_checksum_mismatch(metadata_result_contract: AgentResultContract) -> None:
    """Verifies that pipeline triggers ChecksumMismatchError on hash differences."""
    dispatcher = AudioDispatcher()
    validator = AudioValidator()
    normalizer = AudioNormalizer()
    metrics_calc = AudioMetricsCalculator()
    
    pipeline = AudioIntelligencePipeline(
        dispatcher=dispatcher,
        validator=validator,
        normalizer=normalizer,
        metrics_calculator=metrics_calc
    )
    
    # Set invalid hash in DB
    from backend.database.session import get_db_context
    from backend.database.repositories.evidence_repository import EvidenceRepository
    
    with get_db_context() as db:
        repo = EvidenceRepository(db)
        db_ev = repo.get_by_id("EVID-AUD-77")
        db_ev.sha256_hash = "wrongchecksum"
        db.commit()
        
    with pytest.raises(ChecksumMismatchError):
        pipeline.execute(metadata_result_contract)
