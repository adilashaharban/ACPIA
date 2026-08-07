# -*- coding: utf-8 -*-
"""Knowledge Graph Agent."""

import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from backend.core.logger import get_logger
from backend.version import __version__
from backend.agents.base.base_agent import BaseAgent
from backend.agents.base.processing_context import ProcessingContextContract
from backend.agents.base.agent_result import AgentResultContract
from backend.agents.base.metadata import AgentMetadata
from backend.agents.base.manifest import AgentManifest
from backend.agents.knowledge_graph.node_builder import NodeBuilder
from backend.agents.knowledge_graph.edge_builder import EdgeBuilder
from backend.agents.knowledge_graph.graph_builder import GraphBuilder
from backend.agents.knowledge_graph.validator import GraphValidator
from backend.agents.knowledge_graph.metrics import GraphMetricsCalculator
from backend.agents.knowledge_graph.pipeline import KnowledgeGraphPipeline
from backend.agents.knowledge_graph.exceptions import GraphParsingError

logger = get_logger("agents.knowledge_graph.agent")

class KnowledgeGraphAgent(BaseAgent):
    """Stateless Knowledge Graph agent assembling the investigation graph."""
    
    _MANIFEST = AgentManifest(
        metadata=AgentMetadata(
            name="knowledge_graph_agent",
            version="1.0.0",
            description="Extracts graph nodes and edges from resolved entities and properties.",
            supported_input_types=["AgentResultContract (from entity_resolution_agent)"],
            supported_output_types=["KnowledgeGraphPackage"],
            dependencies=["networkx"]
        ),
        capabilities=[
            "node_builder_mapping",
            "edge_builder_connections",
            "isolated_nodes_counting",
            "graph_density_calculation"
        ],
        custom_configuration_schema={}
    )

    def __init__(
        self,
        node_builder: Optional[NodeBuilder] = None,
        edge_builder: Optional[EdgeBuilder] = None,
        graph_builder: Optional[GraphBuilder] = None,
        validator: Optional[GraphValidator] = None,
        metrics_calculator: Optional[GraphMetricsCalculator] = None,
        pipeline: Optional[KnowledgeGraphPipeline] = None
    ) -> None:
        self.node_builder = node_builder or NodeBuilder()
        self.edge_builder = edge_builder or EdgeBuilder()
        self.graph_builder = graph_builder or GraphBuilder()
        self.validator = validator or GraphValidator()
        self.metrics_calculator = metrics_calculator or GraphMetricsCalculator()
        
        self.pipeline = pipeline or KnowledgeGraphPipeline(
            node_builder=self.node_builder,
            edge_builder=self.edge_builder,
            graph_builder=self.graph_builder,
            validator=self.validator,
            metrics_calculator=self.metrics_calculator
        )

    def run(self, context: ProcessingContextContract, **kwargs) -> AgentResultContract:
        """Runs graph extraction.
        
        Args:
            context: Active tracing context.
            **kwargs: Must contain:
                - metadata_result (AgentResultContract): Metadata Agent output.
                - entity_result (AgentResultContract): Entity Resolution Agent output.
                
        Returns:
            Standardized AgentResultContract output.
        """
        started_at = datetime.now(timezone.utc)
        start_time = time.perf_counter()
        
        status = "SUCCESS"
        payload: Dict[str, Any] = {}
        warnings: List[str] = []
        errors: List[str] = []
        
        metadata_result = kwargs.get("metadata_result")
        entity_result = kwargs.get("entity_result")
        
        try:
            if not isinstance(metadata_result, AgentResultContract):
                raise ValueError("Parameter 'metadata_result' must be an AgentResultContract.")
            if not isinstance(entity_result, AgentResultContract):
                raise ValueError("Parameter 'entity_result' must be an AgentResultContract.")
                
            # Execute pipeline
            package, pipeline_warnings = self.pipeline.execute(
                metadata_result=metadata_result,
                entity_result=entity_result
            )
            payload = package.model_dump()
            warnings.extend(pipeline_warnings)
            
        except GraphParsingError as e:
            status = "FAILURE"
            errors.append(e.message)
            logger.error(f"Domain graph execution failure [Code: {e.error_code}]: {e.message}", exc_info=True)
            
        except Exception as e:
            status = "FAILURE"
            errors.append(str(e))
            logger.critical(f"System panic inside KnowledgeGraphAgent: {e}", exc_info=True)
            
        finished_at = datetime.now(timezone.utc)
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        
        context.pipeline_stage = "knowledge_graph"
        
        return AgentResultContract(
            agent="knowledge_graph_agent",
            status=status,
            processing_context=context,
            payload=payload,
            metrics={
                "started_at": started_at.isoformat(),
                "finished_at": finished_at.isoformat(),
                "processing_time_ms": round(elapsed_ms, 2)
            },
            warnings=warnings,
            errors=errors
        )

    def health(self) -> dict:
        """Exposes health metrics and version status."""
        return {
            "agent": "Knowledge Graph Agent",
            "status": "healthy",
            "version": __version__
        }

    def manifest(self) -> AgentManifest:
        """Exposes discovery manifest capability profile."""
        return self._MANIFEST
export_agent = KnowledgeGraphAgent
