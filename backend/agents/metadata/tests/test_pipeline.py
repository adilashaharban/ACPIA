# -*- coding: utf-8 -*-
"""Unit tests for MetadataPipeline."""

import pytest
from backend.agents.base import AgentResultContract
from backend.agents.metadata.dispatcher import MetadataDispatcher
from backend.agents.metadata.normalizer import MetadataNormalizer
from backend.agents.metadata.validator import MetadataValidator
from backend.agents.metadata.metrics import MetadataMetricsCalculator
from backend.agents.metadata.pipeline import MetadataPipeline
from backend.agents.metadata.exceptions import ChecksumMismatchError

def test_pipeline_happy_path(intake_result_contract: AgentResultContract) -> None:
    """Verifies a full happy path run of the Metadata pipeline."""
    dispatcher = MetadataDispatcher()
    validator = MetadataValidator()
    normalizer = MetadataNormalizer()
    metrics_calc = MetadataMetricsCalculator()
    
    pipeline = MetadataPipeline(
        dispatcher=dispatcher,
        validator=validator,
        normalizer=normalizer,
        metrics_calculator=metrics_calc
    )
    
    package, warnings = pipeline.execute(intake_result_contract)
    
    # Assert successful extraction schema properties
    assert package.evidence_id == "EVID-100"
    assert package.summary.file_type_category == "image"
    assert package.summary.is_media is True
    assert package.file_specs.file_size_bytes > 0
    assert package.image_details is not None
    assert package.image_details.width == 1
    assert package.image_details.height == 1
    assert len(warnings) == 0

def test_pipeline_checksum_mismatch(intake_result_contract: AgentResultContract) -> None:
    """Verifies that pipeline fails when file is modified/differs from checksum."""
    dispatcher = MetadataDispatcher()
    validator = MetadataValidator()
    normalizer = MetadataNormalizer()
    metrics_calc = MetadataMetricsCalculator()
    
    pipeline = MetadataPipeline(
        dispatcher=dispatcher,
        validator=validator,
        normalizer=normalizer,
        metrics_calculator=metrics_calc
    )
    
    # Modify expected hash inside contract to trigger mismatch
    intake_result_contract.payload["evidence_metadata"]["sha256_hash"] = "mismatchhash"
    
    with pytest.raises(ChecksumMismatchError):
        pipeline.execute(intake_result_contract)
