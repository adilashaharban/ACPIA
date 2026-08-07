# -*- coding: utf-8 -*-
"""Unit tests for repository implementations."""

from backend.agents.knowledge_graph.repositories.memory_repository import MemoryRepository
from backend.agents.knowledge_graph.repositories.networkx_repository import NetworkXRepository
from backend.agents.knowledge_graph.repositories.neo4j_repository import Neo4jRepository
from backend.agents.knowledge_graph.schema import GraphNode, NodeType
from backend.schemas.common import SourceReference, DocumentElementType

def test_repositories() -> None:
    """Verifies that nodes save and load correctly in different backend repositories."""
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
    
    # Test MemoryRepository
    mem_repo = MemoryRepository()
    mem_repo.save_nodes([n])
    nodes, edges = mem_repo.load_graph()
    assert len(nodes) == 1
    assert mem_repo.get_node("ND-PER-1") is not None
    
    # Test NetworkXRepository
    nx_repo = NetworkXRepository()
    nx_repo.save_nodes([n])
    nodes, edges = nx_repo.load_graph()
    assert len(nodes) == 1
    assert nx_repo.get_node("ND-PER-1") is not None
    
    # Test Neo4jRepository
    neo_repo = Neo4jRepository()
    neo_repo.save_nodes([n])
    nodes, edges = neo_repo.load_graph()
    assert len(nodes) == 1
    assert neo_repo.get_node("ND-PER-1") is not None
