# -*- coding: utf-8 -*-
"""Knowledge Graph pipeline orchestration."""

import time
from typing import Tuple, List, Dict, Any, Optional
from backend.core.logger import get_logger
from backend.agents.base import AgentResultContract
from backend.agents.knowledge_graph.node_builder import NodeBuilder
from backend.agents.knowledge_graph.edge_builder import EdgeBuilder
from backend.agents.knowledge_graph.graph_builder import GraphBuilder
from backend.agents.knowledge_graph.validator import GraphValidator
from backend.agents.knowledge_graph.metrics import GraphMetricsCalculator
from backend.agents.knowledge_graph.repositories.memory_repository import MemoryRepository
from backend.agents.knowledge_graph.exceptions import GraphParsingError
from backend.agents.entity_resolution.schema import EntityResolutionPackage
from backend.agents.knowledge_graph.schema import KnowledgeGraphPackage, ProcessorExecution

logger = get_logger("agents.knowledge_graph.pipeline")

class KnowledgeGraphPipeline:
    """Orchestrates multi-modal graph extraction, integrity validator checks, and topological metric logs."""
    
    def __init__(
        self,
        node_builder: NodeBuilder,
        edge_builder: EdgeBuilder,
        graph_builder: GraphBuilder,
        validator: GraphValidator,
        metrics_calculator: GraphMetricsCalculator,
        repository: Optional[MemoryRepository] = None
    ) -> None:
        self.node_builder = node_builder
        self.edge_builder = edge_builder
        self.graph_builder = graph_builder
        self.validator = validator
        self.metrics_calculator = metrics_calculator
        self.repository = repository or MemoryRepository()

    def execute(
        self,
        metadata_result: AgentResultContract,
        entity_result: AgentResultContract
    ) -> Tuple[KnowledgeGraphPackage, List[str]]:
        """Runs graph construction.
        
        Args:
            metadata_result: Ingestion metadata result.
            entity_result: Output package from Entity Resolution Agent.
            
        Returns:
            Tuple containing (KnowledgeGraphPackage, warnings list).
        """
        start_time = time.perf_counter()
        warnings: List[str] = []
        executions_log: List[ProcessorExecution] = []
        
        logger.info("Knowledge Graph pipeline started.")
        
        meta_payload = metadata_result.payload
        if not meta_payload:
            raise GraphParsingError("Input metadata payload is empty.")
            
        evidence_id = meta_payload.get("evidence_id")
        case_id = metadata_result.processing_context.case_id
        
        # 1. Fetch paths from database context
        from backend.database.session import get_db_context
        from backend.database.repositories.evidence_repository import EvidenceRepository
        
        file_path = None
        expected_hash = None
        
        with get_db_context() as db:
            repo = EvidenceRepository(db)
            db_evidence = repo.get_by_id(evidence_id)
            if not db_evidence:
                raise GraphParsingError(f"Evidence {evidence_id} not registered in database.")
            file_path = db_evidence.file_path
            expected_hash = db_evidence.sha256_hash
            
        # 2. Checksum validation
        self.validator.verify_integrity(file_path, expected_hash)
        
        # Parse entity resolution package from payload dict
        entity_payload = entity_result.payload
        if not entity_payload:
            raise GraphParsingError("Input entity payload is empty.")
            
        ent_package = EntityResolutionPackage.model_validate(entity_payload)
        
        # 3. Build nodes
        t0 = time.perf_counter()
        nodes = []
        for ent in ent_package.entities:
            nodes.append(self.node_builder.build_node(ent))
        node_build_time = (time.perf_counter() - t0) * 1000.0
        executions_log.append(
            ProcessorExecution(
                processor_name="NodeBuilder",
                processor_version="1.0.0",
                execution_time_ms=round(node_build_time, 2),
                status="SUCCESS"
            )
        )
        
        # 4. Build edges
        t0 = time.perf_counter()
        edges = self.edge_builder.build_edges(nodes)
        edge_build_time = (time.perf_counter() - t0) * 1000.0
        executions_log.append(
            ProcessorExecution(
                processor_name="EdgeBuilder",
                processor_version="1.0.0",
                execution_time_ms=round(edge_build_time, 2),
                status="SUCCESS"
            )
        )
        
        # 5. Save elements to repository
        t0 = time.perf_counter()
        self.repository.clear_graph()
        self.repository.save_nodes(nodes)
        self.repository.save_edges(edges)
        repo_time = (time.perf_counter() - t0) * 1000.0
        
        # 6. Validate Graph
        t0 = time.perf_counter()
        validation_status = self.validator.validate_graph(nodes, edges)
        warnings.extend(validation_status.warnings)
        val_time = (time.perf_counter() - t0) * 1000.0
        
        # 7. Compile Metrics
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        metrics = self.metrics_calculator.calculate(
            processing_time_ms=elapsed_ms,
            node_build_time_ms=node_build_time,
            edge_build_time_ms=edge_build_time,
            validation_time_ms=val_time,
            repository_time_ms=repo_time,
            executions=executions_log
        )
        
        # 8. Assemble Package
        package = self.graph_builder.assemble_package(
            case_id=case_id,
            nodes=nodes,
            edges=edges,
            validation=validation_status,
            metrics=metrics
        )
        
        logger.info("Knowledge Graph package built successfully.")
        return package, warnings
export_pipeline = KnowledgeGraphPipeline
