# -*- coding: utf-8 -*-
"""Unit tests for CorrelationRepository implementations."""

from datetime import datetime, timezone
from backend.agents.cross_evidence_correlation.repositories.memory_repository import MemoryRepository
from backend.agents.cross_evidence_correlation.repositories.sqlite_repository import SQLiteRepository
from backend.agents.cross_evidence_correlation.schema import CorrelationCluster, CorrelatedEntity

def test_repositories() -> None:
    """Verifies that clusters save, load, and filter correctly inside Memory and SQLite backends."""
    c = CorrelationCluster(
        cluster_id="CL-1",
        cluster_name="Cluster 1",
        matched_entities=[CorrelatedEntity(entity_id="ENT-1", canonical_name="John", entity_type="PERSON", confidence=1.0)],
        matched_evidence=["EVID-1"],
        timeline_events=[],
        graph_nodes=["ND-1"],
        graph_edges=[],
        cluster_primary_timestamp=datetime(2026, 8, 1, 10, 0, 0, tzinfo=timezone.utc),
        confidence=1.0
    )
    
    # Test MemoryRepository
    mem_repo = MemoryRepository()
    mem_repo.save_clusters([c])
    assert len(mem_repo.list_clusters()) == 1
    assert len(mem_repo.find_by_entity("ENT-1")) == 1
    assert len(mem_repo.find_by_evidence("EVID-1")) == 1
    assert len(mem_repo.find_by_graph_node("ND-1")) == 1
    
    # Test SQLiteRepository
    sqlite_repo = SQLiteRepository(":memory:")
    sqlite_repo.save_clusters([c])
    assert len(sqlite_repo.list_clusters()) == 1
    assert sqlite_repo.get_cluster("CL-1") is not None
    assert len(sqlite_repo.find_by_entity("ENT-1")) == 1
