# -*- coding: utf-8 -*-
"""Unit tests for GraphValidator."""

import pytest
from pathlib import Path
from backend.agents.knowledge_graph.validator import GraphValidator
from backend.agents.knowledge_graph.exceptions import ChecksumMismatchError
from backend.agents.knowledge_graph.schema import GraphNode, GraphEdge, NodeType, EdgeType, EdgeDirection
from backend.schemas.common import SourceReference, DocumentElementType

def test_verify_integrity_success(mock_evidence_file: Path) -> None:
    """Verifies that matching SHA hashes complete validation successfully."""
    import hashlib
    content = mock_evidence_file.read_bytes()
    sha256 = hashlib.sha256(content).hexdigest()
    # Should not raise exception
    GraphValidator.verify_integrity(str(mock_evidence_file.resolve()), sha256)

def test_verify_integrity_mismatch(mock_evidence_file: Path) -> None:
    """Verifies that mismatching hashes raise ChecksumMismatchError."""
    bad_hash = "wrongsha"
    with pytest.raises(ChecksumMismatchError):
        GraphValidator.verify_integrity(str(mock_evidence_file.resolve()), bad_hash)

def test_validate_graph_dangling_edge() -> None:
    """Verifies that dangling edges raise errors."""
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
    
    # Edge points to target ND-PHO-2 which is missing from nodes list
    edge = GraphEdge(
        edge_id="ED-1",
        source_node_id="ND-PER-1",
        target_node_id="ND-PHO-2",
        edge_type=EdgeType.USES,
        direction=EdgeDirection.DIRECTED,
        confidence=0.80
    )
    
    validation = GraphValidator.validate_graph([n], [edge])
    assert validation.integrity_status == "FAIL"
    assert len(validation.errors) == 1
    assert "dangling target_node_id" in validation.errors[0]
