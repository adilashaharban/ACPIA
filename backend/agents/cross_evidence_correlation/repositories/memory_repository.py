# -*- coding: utf-8 -*-
"""In-memory correlation repository implementation."""

from typing import List, Optional, Dict
from datetime import datetime
from backend.agents.cross_evidence_correlation.repositories.base_repository import CorrelationRepository
from backend.agents.cross_evidence_correlation.schema import CorrelationCluster

class MemoryRepository(CorrelationRepository):
    """Stores correlation clusters inside thread-safe local dictionaries."""
    
    def __init__(self) -> None:
        self._clusters: Dict[str, CorrelationCluster] = {}

    def save_clusters(self, clusters: List[CorrelationCluster]) -> None:
        for c in clusters:
            self._clusters[c.cluster_id] = c

    def load_clusters(self) -> List[CorrelationCluster]:
        return list(self._clusters.values())

    def clear_correlations(self) -> None:
        self._clusters.clear()

    def get_cluster(self, cluster_id: str) -> Optional[CorrelationCluster]:
        return self._clusters.get(cluster_id)

    def list_clusters(self) -> List[CorrelationCluster]:
        return self.load_clusters()

    def find_by_entity(self, entity_id: str) -> List[CorrelationCluster]:
        return [c for c in self.load_clusters() if any(ent.entity_id == entity_id for ent in c.matched_entities)]

    def find_by_evidence(self, evidence_id: str) -> List[CorrelationCluster]:
        return [c for c in self.load_clusters() if evidence_id in c.matched_evidence]

    def find_by_time(self, start: datetime, end: datetime) -> List[CorrelationCluster]:
        res = []
        for c in self.load_clusters():
            if c.cluster_primary_timestamp and start <= c.cluster_primary_timestamp <= end:
                res.append(c)
        return res

    def find_by_graph_node(self, node_id: str) -> List[CorrelationCluster]:
        return [c for c in self.load_clusters() if node_id in c.graph_nodes]
export_memory_repository = MemoryRepository
