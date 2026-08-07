# -*- coding: utf-8 -*-
"""Unit and integration tests for CrossEvidenceCorrelationPipeline."""

from backend.agents.base import AgentResultContract
from backend.agents.cross_evidence_correlation.dispatcher import Dispatcher
from backend.agents.cross_evidence_correlation.comparator import Comparator
from backend.agents.cross_evidence_correlation.matcher import Matcher
from backend.agents.cross_evidence_correlation.cluster_builder import ClusterBuilder
from backend.agents.cross_evidence_correlation.conflict_detector import ConflictDetector
from backend.agents.cross_evidence_correlation.validator import Validator
from backend.agents.cross_evidence_correlation.metrics import MetricsCalculator
from backend.agents.cross_evidence_correlation.pipeline import CrossEvidenceCorrelationPipeline
from backend.agents.cross_evidence_correlation.schema import CorrelationPackage

def test_pipeline_happy_path(
    metadata_result_contract: AgentResultContract,
    document_result_contract: AgentResultContract,
    vision_result_contract: AgentResultContract,
    audio_result_contract: AgentResultContract,
    entity_result_contract: AgentResultContract,
    graph_result_contract: AgentResultContract,
    timeline_result_contract: AgentResultContract
) -> None:
    """Verifies that the complete pipeline execution generates correct CorrelationPackage results."""
    pipeline = CrossEvidenceCorrelationPipeline(
        dispatcher=Dispatcher(),
        matcher=Matcher(Comparator()),
        cluster_builder=ClusterBuilder(),
        conflict_detector=ConflictDetector(),
        validator=Validator(),
        metrics_calculator=MetricsCalculator()
    )
    
    package, warnings = pipeline.execute(
        metadata_result=metadata_result_contract,
        document_result=document_result_contract,
        vision_result=vision_result_contract,
        audio_result=audio_result_contract,
        entity_result=entity_result_contract,
        graph_result=graph_result_contract,
        timeline_result=timeline_result_contract
    )
    
    assert isinstance(package, CorrelationPackage)
    # Check we harvested candidates
    assert package.statistics.total_candidates > 0
    # Checks package properties
    assert len(package.cluster_index) == len(package.clusters)
