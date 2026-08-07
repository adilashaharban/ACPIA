# -*- coding: utf-8 -*-
"""In-memory graph repository implementation."""

from typing import List, Optional, Tuple, Dict
from backend.agents.knowledge_graph.repositories.base_repository import GraphRepository
from backend.agents.knowledge_graph.schema import GraphNode, GraphEdge

class MemoryRepository(GraphRepository):
    """Stores graph elements inside thread-safe local dictionaries."""
    
    def __init__(self) -> None:
        self._nodes: Dict[str, GraphNode] = {}
        self._edges: Dict[str, GraphEdge] = {}

    def save_nodes(self, nodes: List[GraphNode]) -> None:
        for node in nodes:
            self._nodes[node.node_id] = node

    def save_edges(self, edges: List[GraphEdge]) -> None:
        for edge in edges:
            self._edges[edge.edge_id] = edge

    def load_graph(self) -> Tuple[List[GraphNode], List[GraphEdge]]:
        return list(self._nodes.values()), list(self._edges.values())

    def clear_graph(self) -> None:
        self._nodes.clear()
        self._edges.clear()

    def get_node(self, node_id: str) -> Optional[GraphNode]:
        return self._nodes.get(node_id)

    def get_edge(self, edge_id: str) -> Optional[GraphEdge]:
        return self._edges.get(edge_id)
export_memory_repository = MemoryRepository
