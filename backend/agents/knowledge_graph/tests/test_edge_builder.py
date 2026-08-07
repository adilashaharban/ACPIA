# -*- coding: utf-8 -*-
"""Unit tests for EdgeBuilder."""

from backend.agents.knowledge_graph.edge_builder import EdgeBuilder
from backend.agents.knowledge_graph.schema import GraphNode, NodeType, EdgeType
from backend.schemas.common import SourceReference, DocumentElementType

def test_edge_building() -> None:
    """Verifies that shared evidence references generate relationships."""
    ref = SourceReference(
        evidence_id="EVID-1",
        file_path="mock.txt",
        page_number=1,
        parser="test",
        parser_version="1.0.0",
        source_element=DocumentElementType.PARAGRAPH
    )
    
    n1 = GraphNode(
        node_id="ND-PER-1",
        entity_id="ENT-PER-1",
        node_type=NodeType.PERSON,
        label="PERSON: John",
        confidence=0.90,
        source_references=[ref]
    )
    n2 = GraphNode(
        node_id="ND-PHO-2",
        entity_id="ENT-PHO-2",
        node_type=NodeType.PHONE,
        label="PHONE: +1",
        confidence=0.85,
        source_references=[ref]
    )
    
    edges = EdgeBuilder.build_edges([n1, n2])
    assert len(edges) == 1
    assert edges[0].source_node_id == "ND-PER-1"
    assert edges[0].target_node_id == "ND-PHO-2"
    assert edges[0].edge_type == EdgeType.USES
