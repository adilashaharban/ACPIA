# -*- coding: utf-8 -*-
"""Graph validator module."""

import hashlib
from pathlib import Path
from typing import List
from backend.agents.knowledge_graph.exceptions import ChecksumMismatchError, GraphParsingError
from backend.agents.knowledge_graph.schema import GraphValidation, GraphNode, GraphEdge

class GraphValidator:
    """Checks duplicate node/edge IDs, dangling connections, and invalid confidence bounds."""
    
    @staticmethod
    def verify_integrity(file_path: str, expected_sha256: str) -> None:
        """Verifies integrity checksums.
        
        Args:
            file_path: Evidence file path.
            expected_sha256: Expected SHA hash.
        """
        path = Path(file_path)
        if not path.exists():
            raise GraphParsingError(f"Evidence file missing during graph verification: {file_path}")
            
        try:
            hasher = hashlib.sha256()
            with open(path, "rb") as f:
                while chunk := f.read(65536):
                    hasher.update(chunk)
            calculated = hasher.hexdigest()
            if calculated != expected_sha256:
                raise ChecksumMismatchError(
                    f"Integrity check failed. Expected: {expected_sha256}, Got: {calculated}"
                )
        except ChecksumMismatchError:
            raise
        except Exception as e:
            raise GraphParsingError(f"Integrity check processing crash: {e}")

    @staticmethod
    def validate_graph(nodes: List[GraphNode], edges: List[GraphEdge]) -> GraphValidation:
        """Sanity checks graph nodes and edge targets integrity.
        
        Args:
            nodes: List of nodes.
            edges: List of edges.
            
        Returns:
            GraphValidation status containing warning/error listings.
        """
        warnings = []
        errors = []
        
        # 1. Check duplicate node IDs
        node_ids = {n.node_id for n in nodes}
        if len(node_ids) != len(nodes):
            errors.append("Duplicate node IDs detected in GraphNodes list.")
            
        # 2. Check duplicate edge IDs
        edge_ids = {e.edge_id for e in edges}
        if len(edge_ids) != len(edges):
            errors.append("Duplicate edge IDs detected in GraphEdges list.")
            
        # 3. Check invalid confidences
        for n in nodes:
            if not (0.0 <= n.confidence <= 1.0):
                errors.append(f"Node '{n.node_id}' confidence is outside bounds: {n.confidence}")
                
        # 4. Check dangling source/target edges
        for e in edges:
            if e.source_node_id not in node_ids:
                errors.append(f"Edge '{e.edge_id}' has dangling source_node_id: {e.source_node_id}")
            if e.target_node_id not in node_ids:
                errors.append(f"Edge '{e.edge_id}' has dangling target_node_id: {e.target_node_id}")
            if not (0.0 <= e.confidence <= 1.0):
                errors.append(f"Edge '{e.edge_id}' confidence is outside bounds: {e.confidence}")
                
        return GraphValidation(
            integrity_status="PASS" if len(errors) == 0 else "FAIL",
            warnings=warnings,
            errors=errors
        )
export_validator = GraphValidator
