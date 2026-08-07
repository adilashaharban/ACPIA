# -*- coding: utf-8 -*-
"""Unit tests for ClusterBuilder."""

from backend.agents.cross_evidence_correlation.cluster_builder import ClusterBuilder
from backend.agents.cross_evidence_correlation.schema import (
    CorrelationMatch, CorrelationType, CorrelationStrength, CorrelationObservation
)
from backend.schemas.common import SourceReference, DocumentElementType

def test_cluster_builder() -> None:
    """Verifies that connected matches form groups."""
    ref = SourceReference(
        evidence_id="EVID-1",
        file_path="mock.txt",
        page_number=1,
        parser="test",
        parser_version="1.0.0",
        source_element=DocumentElementType.PARAGRAPH
    )
    
    o1 = CorrelationObservation(
        observation_id="OBS-1",
        evidence_id="EVID-1",
        originating_agent="test",
        raw_value="John",
        normalized_value="john",
        confidence=1.0,
        source_reference=ref
    )
    o2 = CorrelationObservation(
        observation_id="OBS-2",
        evidence_id="EVID-1",
        originating_agent="test",
        raw_value="John",
        normalized_value="john",
        confidence=1.0,
        source_reference=ref
    )
    
    m1 = CorrelationMatch(
        match_id="MTH-1",
        correlation_type=CorrelationType.ENTITY_MATCH,
        correlation_strength=CorrelationStrength.EXACT,
        confidence=1.0,
        matching_algorithm="EXACT",
        supporting_observations=[o1, o2]
    )
    
    clusters = ClusterBuilder.build_clusters([m1])
    assert len(clusters) == 1
    assert "EVID-1" in clusters[0].matched_evidence
