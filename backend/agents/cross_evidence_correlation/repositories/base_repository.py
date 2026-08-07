# -*- coding: utf-8 -*-
"""Correlation repository base interface."""

from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from backend.agents.cross_evidence_correlation.schema import CorrelationCluster

class CorrelationRepository(ABC):
    """Abstract interface for storing and loading correlation outputs."""
    
    @abstractmethod
    def save_clusters(self, clusters: List[CorrelationCluster]) -> None:
        """Stores a list of correlation clusters."""
        pass

    @abstractmethod
    def load_clusters(self) -> List[CorrelationCluster]:
        """Loads and returns all saved clusters."""
        pass

    @abstractmethod
    def clear_correlations(self) -> None:
        """Purges stored clusters."""
        pass

    @abstractmethod
    def get_cluster(self, cluster_id: str) -> Optional[CorrelationCluster]:
        """Loads a single cluster by ID."""
        pass

    @abstractmethod
    def list_clusters(self) -> List[CorrelationCluster]:
        """Lists all clusters."""
        pass

    @abstractmethod
    def find_by_entity(self, entity_id: str) -> List[CorrelationCluster]:
        """Filters clusters by associated canonical entity ID."""
        pass

    @abstractmethod
    def find_by_evidence(self, evidence_id: str) -> List[CorrelationCluster]:
        """Filters clusters by associated evidence ID."""
        pass

    @abstractmethod
    def find_by_time(self, start: datetime, end: datetime) -> List[CorrelationCluster]:
        """Filters clusters within time window constraints."""
        pass

    @abstractmethod
    def find_by_graph_node(self, node_id: str) -> List[CorrelationCluster]:
        """Filters clusters associated with a target graph node ID."""
        pass
export_base_repository = CorrelationRepository
