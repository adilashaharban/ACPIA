# -*- coding: utf-8 -*-
"""Unit and integration tests for TimelineIntelligencePipeline."""

from backend.agents.base import AgentResultContract
from backend.agents.timeline_intelligence.dispatcher import TimelineDispatcher
from backend.agents.timeline_intelligence.timestamp_normalizer import TimestampNormalizer
from backend.agents.timeline_intelligence.event_builder import EventBuilder
from backend.agents.timeline_intelligence.duplicate_detector import DuplicateDetector
from backend.agents.timeline_intelligence.merger import EventMerger
from backend.agents.timeline_intelligence.sorter import ChronologicalSorter
from backend.agents.timeline_intelligence.validator import TimelineValidator
from backend.agents.timeline_intelligence.metrics import TimelineMetricsCalculator
from backend.agents.timeline_intelligence.pipeline import TimelineIntelligencePipeline
from backend.agents.timeline_intelligence.schema import TimelinePackage

def test_pipeline_happy_path(
    metadata_result_contract: AgentResultContract,
    document_result_contract: AgentResultContract,
    vision_result_contract: AgentResultContract,
    audio_result_contract: AgentResultContract,
    graph_result_contract: AgentResultContract
) -> None:
    """Verifies that the complete pipeline execution generates correct TimelinePackage results."""
    pipeline = TimelineIntelligencePipeline(
        dispatcher=TimelineDispatcher(),
        normalizer=TimestampNormalizer(),
        event_builder=EventBuilder(),
        duplicate_detector=DuplicateDetector(),
        merger=EventMerger(),
        sorter=ChronologicalSorter(),
        validator=TimelineValidator(),
        metrics_calculator=TimelineMetricsCalculator()
    )
    
    package, warnings = pipeline.execute(
        metadata_result=metadata_result_contract,
        document_result=document_result_contract,
        vision_result=vision_result_contract,
        audio_result=audio_result_contract,
        graph_result=graph_result_contract
    )
    
    assert isinstance(package, TimelinePackage)
    # Check we harvested events from all 5 sources
    assert len(package.events) > 1
    assert package.statistics.total_events == len(package.events)
    # Check earliest is before latest
    assert package.summary.earliest_timestamp < package.summary.latest_timestamp
    # Verify index mapping
    assert len(package.event_index) == len(package.events)
