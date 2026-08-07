# -*- coding: utf-8 -*-
"""GraphNode builder module."""

from typing import List
from backend.agents.knowledge_graph.schema import GraphNode, NodeType, GraphProperty, GraphObservation
from backend.agents.entity_resolution.schema import CanonicalEntity

class NodeBuilder:
    """Transforms CanonicalEntity entities into GraphNode models."""
    
    @staticmethod
    def build_node(entity: CanonicalEntity) -> GraphNode:
        """Converts Entity to Node.
        
        Args:
            entity: CanonicalEntity resolved object.
            
        Returns:
            GraphNode object.
        """
        node_id = f"ND-{entity.entity_type.name[:3]}-{entity.entity_id[-8:]}"
        
        # Build properties list
        properties: List[GraphProperty] = []
        for attr in entity.attributes:
            properties.append(
                GraphProperty(
                    key=attr.key,
                    value=attr.value,
                    confidence=attr.confidence,
                    source_reference=attr.source_reference
                )
            )
            
        # Build supporting observations list
        observations: List[GraphObservation] = []
        for obs in entity.supporting_observations:
            observations.append(
                GraphObservation(
                    observation_id=obs.observation_id,
                    evidence_id=obs.evidence_id,
                    raw_value=obs.raw_value,
                    confidence=obs.confidence,
                    source_reference=obs.source_reference
                )
            )
            
        # Standard node mapping
        # Map EntityType to NodeType name if they align
        try:
            n_type = NodeType[entity.entity_type.name]
        except KeyError:
            n_type = NodeType.UNKNOWN
            
        return GraphNode(
            node_id=node_id,
            entity_id=entity.entity_id,
            node_type=n_type,
            label=f"{n_type.name}: {entity.canonical_name}",
            properties=properties,
            confidence=entity.confidence_breakdown.final_confidence,
            source_references=entity.source_references,
            supporting_observations=observations
        )
export_node_builder = NodeBuilder
