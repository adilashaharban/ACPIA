# -*- coding: utf-8 -*-
"""Unit tests for NodeBuilder."""

from backend.agents.knowledge_graph.node_builder import NodeBuilder
from backend.agents.entity_resolution.schema import CanonicalEntity, EntityAttribute, ConfidenceBreakdown
from backend.agents.knowledge_graph.schema import NodeType
from backend.schemas.common import SourceReference, DocumentElementType

def test_node_building() -> None:
    """Verifies that NodeBuilder converts entities to GraphNodes."""
    ref = SourceReference(
        evidence_id="EVID-1",
        file_path="mock.txt",
        page_number=1,
        parser="test",
        parser_version="1.0.0",
        source_element=DocumentElementType.PARAGRAPH
    )
    
    breakdown = ConfidenceBreakdown(
        exact_match_score=1.0,
        fuzzy_match_score=0.0,
        cross_modal_score=0.0,
        evidence_count_score=0.5,
        final_confidence=0.95
    )
    
    entity = CanonicalEntity(
        entity_id="ENT-PER-1234",
        entity_type="PERSON",
        canonical_name="John Doe",
        aliases=[],
        attributes=[
            EntityAttribute(
                key="name",
                value="John Doe",
                confidence=0.95,
                source_reference=ref
            )
        ],
        confidence_breakdown=breakdown,
        source_references=[ref],
        supporting_observations=[],
        linked_evidence=["EVID-1"],
        creation_method="EXACT_MATCH"
    )
    
    node = NodeBuilder.build_node(entity)
    assert node.node_id == "ND-PER-PER-1234"
    assert node.node_type == NodeType.PERSON
    assert len(node.properties) == 1
    assert node.properties[0].value == "John Doe"
