# -*- coding: utf-8 -*-
"""Unit tests for GraphBuilder."""

from backend.agents.knowledge_graph.graph_builder import GraphBuilder
from backend.agents.knowledge_graph.schema import GraphNode, GraphEdge, NodeType, EdgeType, EdgeDirection, GraphValidation, GraphMetrics
from backend.schemas.common import SourceReference, DocumentElementType

def test_graph_builder_deduplication() -> None:
    """Verifies duplicate nodes merge property collections."""
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
        label="John",
        confidence=0.90,
        source_references=[ref]
    )
    n2 = GraphNode(
        node_id="ND-PER-1",
        entity_id="ENT-PER-1",
        node_type=NodeType.PERSON,
        label="John",
        confidence=0.80,
        source_references=[ref]
    )
    
    merged = GraphBuilder.deduplicate_nodes([n1, n2])
    assert len(merged) == 1
    assert merged[0].confidence == 0.90
    
def test_assemble_package() -> None:
    """Verifies that stats computes correct graph metrics."""
    ref = SourceReference(
        evidence_id="EVID-1",
        file_path="mock.txt",
        page_number=1,
        parser="test",
        parser_version="1.0.0",
        source_element=DocumentElementType.PARAGRAPH
    )
    
    n = GraphNode(
        node_id="ND-PER-1",
        entity_id="ENT-PER-1",
        node_type=NodeType.PERSON,
        label="John",
        confidence=0.90,
        source_references=[ref]
    )
    
    val = GraphValidation(integrity_status="PASS")
    met = GraphMetrics(
        processing_time_ms=10.0,
        node_build_time_ms=5.0,
        edge_build_time_ms=2.0,
        validation_time_ms=1.0,
        repository_time_ms=2.0,
        executions=[]
    )
    
    package = GraphBuilder.assemble_package("CASE-1", [n], [], val, met)
    assert package.statistics.node_count == 1
    assert package.statistics.edge_count == 0
    assert package.statistics.density == 0.0
