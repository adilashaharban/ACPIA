# -*- coding: utf-8 -*-
"""GraphEdge builder module."""

import uuid
from typing import List
from backend.agents.knowledge_graph.schema import (
    GraphEdge, GraphNode, EdgeType, EdgeDirection, GraphEvidenceReference, GraphObservation, NodeType
)

class EdgeBuilder:
    """Creates relationship edges from supporting observation and source reference intersects."""
    
    @staticmethod
    def build_edges(nodes: List[GraphNode]) -> List[GraphEdge]:
        """Infers deterministic edges connecting nodes that share evidence or observations.
        
        Args:
            nodes: List of GraphNode.
            
        Returns:
            List of GraphEdge objects.
        """
        edges: List[GraphEdge] = []
        
        # Simple quadratic comparison to link nodes sharing evidence/observables
        for i in range(len(nodes)):
            n1 = nodes[i]
            for j in range(i + 1, len(nodes)):
                n2 = nodes[j]
                
                # Check for shared evidence IDs
                ev1 = {ref.evidence_id for ref in n1.source_references}
                ev2 = {ref.evidence_id for ref in n2.source_references}
                shared_ev = ev1.intersection(ev2)
                
                if shared_ev:
                    # Construct evidence references list
                    supporting_ev = []
                    for ev_id in shared_ev:
                        # Find matching source ref
                        ref = next((r for r in n1.source_references if r.evidence_id == ev_id), None)
                        if ref:
                            supporting_ev.append(
                                GraphEvidenceReference(
                                    evidence_id=ev_id,
                                    source_reference=ref
                                )
                            )
                            
                    # Construct observations list
                    supporting_obs = []
                    for obs in n1.supporting_observations:
                        if obs.evidence_id in shared_ev:
                            supporting_obs.append(obs)
                            
                    # Determine relationship type based on NodeTypes
                    edge_type = EdgeType.LINKED_TO
                    direction = EdgeDirection.UNDIRECTED
                    
                    if n1.node_type == NodeType.PERSON and n2.node_type == NodeType.PHONE:
                        edge_type = EdgeType.USES
                        direction = EdgeDirection.DIRECTED
                    elif n1.node_type == NodeType.PERSON and n2.node_type == NodeType.PLATE:
                        edge_type = EdgeType.OWNS
                        direction = EdgeDirection.DIRECTED
                    elif n1.node_type == NodeType.PHONE and n2.node_type == NodeType.PHONE:
                        edge_type = EdgeType.COMMUNICATED_WITH
                        direction = EdgeDirection.UNDIRECTED
                        
                    edges.append(
                        GraphEdge(
                            edge_id=f"ED-{edge_type.name[:3]}-{str(uuid.uuid4())[:8]}",
                            source_node_id=n1.node_id,
                            target_node_id=n2.node_id,
                            edge_type=edge_type,
                            direction=direction,
                            confidence=min(n1.confidence, n2.confidence),
                            supporting_evidence=supporting_ev,
                            supporting_observations=supporting_obs,
                            creation_method="SHARED_EVIDENCE_OBSERVATION"
                        )
                    )
                    
        return edges
export_edge_builder = EdgeBuilder
