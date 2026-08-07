# -*- coding: utf-8 -*-
"""Unit and integration tests for EntityResolutionPipeline."""

from backend.agents.base import AgentResultContract
from backend.agents.entity_resolution.normalizer import EntityNormalizer
from backend.agents.entity_resolution.matcher import EntityMatcher
from backend.agents.entity_resolution.merger import EntityMerger
from backend.agents.entity_resolution.confidence import EntityConfidenceCalculator
from backend.agents.entity_resolution.validator import EntityValidator
from backend.agents.entity_resolution.metrics import EntityMetricsCalculator
from backend.agents.entity_resolution.pipeline import EntityResolutionPipeline
from backend.agents.entity_resolution.schema import EntityResolutionPackage

def test_pipeline_happy_path(
    metadata_result_contract: AgentResultContract,
    document_result_contract: AgentResultContract,
    vision_result_contract: AgentResultContract,
    audio_result_contract: AgentResultContract
) -> None:
    """Verifies that the complete pipeline execution generates correct EntityResolutionPackage results."""
    pipeline = EntityResolutionPipeline(
        normalizer=EntityNormalizer(),
        matcher=EntityMatcher(),
        merger=EntityMerger(),
        confidence_calculator=EntityConfidenceCalculator(),
        validator=EntityValidator(),
        metrics_calculator=EntityMetricsCalculator()
    )
    
    package, warnings = pipeline.execute(
        metadata_result=metadata_result_contract,
        document_result=document_result_contract,
        vision_result=vision_result_contract,
        audio_result=audio_result_contract
    )
    
    assert isinstance(package, EntityResolutionPackage)
    # Check resolved candidates (File + Email + Phone + URL + Plate + Color + Keyword)
    assert package.statistics.total_candidates > 0
    assert len(package.entities) > 0
