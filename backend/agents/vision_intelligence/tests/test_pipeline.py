# -*- coding: utf-8 -*-
"""Unit and integration tests for VisionIntelligencePipeline."""

import pytest
from backend.agents.base import AgentResultContract
from backend.agents.vision_intelligence.dispatcher import VisionDispatcher
from backend.agents.vision_intelligence.normalizer import VisionNormalizer
from backend.agents.vision_intelligence.validator import VisionValidator
from backend.agents.vision_intelligence.metrics import VisionMetricsCalculator
from backend.agents.vision_intelligence.pipeline import VisionIntelligencePipeline
from backend.agents.vision_intelligence.exceptions import ChecksumMismatchError

def test_pipeline_happy_path(metadata_result_contract: AgentResultContract) -> None:
    """Verifies that the complete pipeline execution generates correct VisionPackage results."""
    dispatcher = VisionDispatcher()
    validator = VisionValidator()
    normalizer = VisionNormalizer()
    metrics_calc = VisionMetricsCalculator()
    
    pipeline = VisionIntelligencePipeline(
        dispatcher=dispatcher,
        validator=validator,
        normalizer=normalizer,
        metrics_calculator=metrics_calc
    )
    
    package, warnings = pipeline.execute(metadata_result_contract)
    
    # Assert successfully parsed shapes
    assert package.evidence_id == "EVID-VIS-99"
    assert package.summary.mime_type == "image/jpeg"
    assert len(package.objects) == 1
    assert len(package.faces) == 1
    assert len(package.vehicles) == 1
    assert len(package.plates) == 1
    assert len(package.ocr_regions) == 1
    assert len(package.features) == 1
    assert len(warnings) == 0

def test_pipeline_checksum_mismatch(metadata_result_contract: AgentResultContract) -> None:
    """Verifies that pipeline triggers ChecksumMismatchError on hash differences."""
    dispatcher = VisionDispatcher()
    validator = VisionValidator()
    normalizer = VisionNormalizer()
    metrics_calc = VisionMetricsCalculator()
    
    pipeline = VisionIntelligencePipeline(
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
        db_ev = repo.get_by_id("EVID-VIS-99")
        db_ev.sha256_hash = "wrongchecksum"
        db.commit()
        
    with pytest.raises(ChecksumMismatchError):
        pipeline.execute(metadata_result_contract)
