# -*- coding: utf-8 -*-
"""Graph repository base interface."""

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from backend.agents.knowledge_graph.schema import GraphNode, GraphEdge

class GraphRepository(ABC):
    """Abstract interface for storing and loading graph structures."""
    
    @abstractmethod
    def save_nodes(self, nodes: List[GraphNode]) -> None:
        """Stores a list of graph nodes."""
        pass

    @abstractmethod
    def save_edges(self, edges: List[GraphEdge]) -> None:
        """Stores a list of graph edges."""
        pass

    @abstractmethod
    def load_graph(self) -> Tuple[List[GraphNode], List[GraphEdge]]:
        """Loads and returns all saved nodes and edges."""
        pass

    @abstractmethod
    def clear_graph(self) -> None:
        """Purges stored nodes and edges."""
        pass

    @abstractmethod
    def get_node(self, node_id: str) -> Optional[GraphNode]:
        """Loads a single node by ID."""
        pass

    @abstractmethod
    def get_edge(self, edge_id: str) -> Optional[GraphEdge]:
        """Loads a single edge by ID."""
        pass
export_base_repository = GraphRepository
