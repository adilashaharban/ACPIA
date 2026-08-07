# -*- coding: utf-8 -*-
"""NetworkX-backed graph repository implementation."""

from typing import List, Optional, Tuple
import networkx as nx
from backend.agents.knowledge_graph.repositories.base_repository import GraphRepository
from backend.agents.knowledge_graph.schema import GraphNode, GraphEdge

class NetworkXRepository(GraphRepository):
    """Uses a NetworkX MultiDiGraph structure to support topological lookups."""
    
    def __init__(self) -> None:
        self.g = nx.MultiDiGraph()

    def save_nodes(self, nodes: List[GraphNode]) -> None:
        for node in nodes:
            self.g.add_node(node.node_id, payload=node)

    def save_edges(self, edges: List[GraphEdge]) -> None:
        for edge in edges:
            self.g.add_edge(edge.source_node_id, edge.target_node_id, key=edge.edge_id, payload=edge)

    def load_graph(self) -> Tuple[List[GraphNode], List[GraphEdge]]:
        nodes = [data["payload"] for node_id, data in self.g.nodes(data=True) if "payload" in data]
        edges = [data["payload"] for u, v, k, data in self.g.edges(keys=True, data=True) if "payload" in data]
        return nodes, edges

    def clear_graph(self) -> None:
        self.g.clear()

    def get_node(self, node_id: str) -> Optional[GraphNode]:
        if self.g.has_node(node_id):
            return self.g.nodes[node_id].get("payload")
        return None

    def get_edge(self, edge_id: str) -> Optional[GraphEdge]:
        for u, v, k, data in self.g.edges(keys=True, data=True):
            if k == edge_id:
                return data.get("payload")
        return None
export_networkx_repository = NetworkXRepository
