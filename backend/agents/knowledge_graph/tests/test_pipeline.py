# -*- coding: utf-8 -*-
"""Unit and integration tests for KnowledgeGraphPipeline."""

from backend.agents.base import AgentResultContract
from backend.agents.knowledge_graph.node_builder import NodeBuilder
from backend.agents.knowledge_graph.edge_builder import EdgeBuilder
from backend.agents.knowledge_graph.graph_builder import GraphBuilder
from backend.agents.knowledge_graph.validator import GraphValidator
from backend.agents.knowledge_graph.metrics import GraphMetricsCalculator
from backend.agents.knowledge_graph.pipeline import KnowledgeGraphPipeline
from backend.agents.knowledge_graph.schema import KnowledgeGraphPackage

def test_pipeline_happy_path(
    metadata_result_contract: AgentResultContract,
    entity_resolution_result_contract: AgentResultContract
) -> None:
    """Verifies that the complete pipeline execution generates correct KnowledgeGraphPackage results."""
    pipeline = KnowledgeGraphPipeline(
        node_builder=NodeBuilder(),
        edge_builder=EdgeBuilder(),
        graph_builder=GraphBuilder(),
        validator=GraphValidator(),
        metrics_calculator=GraphMetricsCalculator()
    )
    
    package, warnings = pipeline.execute(
        metadata_result=metadata_result_contract,
        entity_result=entity_resolution_result_contract
    )
    
    assert isinstance(package, KnowledgeGraphPackage)
    # Check nodes built (PERSON + PHONE)
    assert len(package.nodes) == 2
    # Connected by a shared evidence (USES relationship)
    assert len(package.edges) == 1
    assert package.statistics.node_count == 2
    assert package.statistics.edge_count == 1
