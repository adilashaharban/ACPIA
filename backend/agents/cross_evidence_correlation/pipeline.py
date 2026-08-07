# -*- coding: utf-8 -*-
"""Cross-Evidence Correlation pipeline orchestration."""

import time
import uuid
from datetime import datetime, timezone
from typing import Tuple, List, Dict, Any, Optional
from backend.core.logger import get_logger
from backend.agents.base import AgentResultContract
from backend.agents.cross_evidence_correlation.dispatcher import Dispatcher
from backend.agents.cross_evidence_correlation.matcher import Matcher
from backend.agents.cross_evidence_correlation.cluster_builder import ClusterBuilder
from backend.agents.cross_evidence_correlation.conflict_detector import ConflictDetector
from backend.agents.cross_evidence_correlation.validator import Validator
from backend.agents.cross_evidence_correlation.metrics import MetricsCalculator
from backend.agents.cross_evidence_correlation.repositories.memory_repository import MemoryRepository
from backend.agents.cross_evidence_correlation.exceptions import CorrelationError
from backend.agents.cross_evidence_correlation.schema import (
    CorrelationPackage, CorrelationCluster, CorrelationMatch, CorrelationStatistics,
    CorrelationSummary, ProcessorExecution, CorrelationValidation
)

logger = get_logger("agents.cross_evidence_correlation.pipeline")

class CrossEvidenceCorrelationPipeline:
    """Orchestrates candidate observation comparisons, clusters maps, and persistence lookups."""
    
    def __init__(
        self,
        dispatcher: Dispatcher,
        matcher: Matcher,
        cluster_builder: ClusterBuilder,
        conflict_detector: ConflictDetector,
        validator: Validator,
        metrics_calculator: MetricsCalculator,
        repository: Optional[MemoryRepository] = None
    ) -> None:
        self.dispatcher = dispatcher
        self.matcher = matcher
        self.cluster_builder = cluster_builder
        self.conflict_detector = conflict_detector
        self.validator = validator
        self.metrics_calculator = metrics_calculator
        self.repository = repository or MemoryRepository()

    def execute(
        self,
        metadata_result: AgentResultContract,
        document_result: Optional[AgentResultContract] = None,
        vision_result: Optional[AgentResultContract] = None,
        audio_result: Optional[AgentResultContract] = None,
        entity_result: Optional[AgentResultContract] = None,
        graph_result: Optional[AgentResultContract] = None,
        timeline_result: Optional[AgentResultContract] = None
    ) -> Tuple[CorrelationPackage, List[str]]:
        """Runs correlation pipeline.
        
        Args:
            metadata_result: Ingestion Metadata result contract.
            document_result: Optional Document agent result.
            vision_result: Optional Vision agent result.
            audio_result: Optional Audio agent result.
            entity_result: Optional Entity Resolution agent result.
            graph_result: Optional Knowledge Graph result.
            timeline_result: Optional Timeline result.
            
        Returns:
            Tuple containing (CorrelationPackage, warnings list).
        """
        start_time = time.perf_counter()
        warnings: List[str] = []
        executions_log: List[ProcessorExecution] = []
        
        logger.info("Cross-Evidence Correlation pipeline started.")
        
        meta_payload = metadata_result.payload
        if not meta_payload:
            raise CorrelationError("Input metadata payload is empty.")
            
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
                raise CorrelationError(f"Evidence {evidence_id} not registered in database.")
            file_path = db_evidence.file_path
            expected_hash = db_evidence.sha256_hash
            
        # 2. Checksum validation
        self.validator.verify_integrity(file_path, expected_hash)
        
        # 3. Gather Candidates
        t0 = time.perf_counter()
        candidates = self.dispatcher.gather_observations(
            metadata_payload=meta_payload,
            document_payload=document_result.payload if document_result else None,
            vision_payload=vision_result.payload if vision_result else None,
            audio_payload=audio_result.payload if audio_result else None,
            entity_payload=entity_result.payload if entity_result else None,
            graph_payload=graph_result.payload if graph_result else None,
            timeline_payload=timeline_result.payload if timeline_result else None,
            file_path=file_path,
            evidence_id=evidence_id
        )
        extraction_time = (time.perf_counter() - t0) * 1000.0
        
        # 4. Pairwise comparisons and Matchings
        t0 = time.perf_counter()
        matches: List[CorrelationMatch] = []
        for i in range(len(candidates)):
            for j in range(i + 1, len(candidates)):
                match = self.matcher.match_candidates(candidates[i], candidates[j])
                if match:
                    matches.append(match)
        comparison_time = (time.perf_counter() - t0) * 1000.0
        executions_log.append(
            ProcessorExecution(
                processor_name="PairwiseMatcher",
                processor_version="1.0.0",
                execution_time_ms=round(comparison_time, 2),
                status="SUCCESS"
            )
        )
        
        # 5. Connected Component Clustering
        t0 = time.perf_counter()
        clusters = self.cluster_builder.build_clusters(matches)
        clustering_time = (time.perf_counter() - t0) * 1000.0
        executions_log.append(
            ProcessorExecution(
                processor_name="ClusterBuilder",
                processor_version="1.0.0",
                execution_time_ms=round(clustering_time, 2),
                status="SUCCESS"
            )
        )
        
        # Build cluster index map
        cluster_index = {}
        for idx, c in enumerate(clusters):
            cluster_index[c.cluster_id] = idx
            
        # 6. Conflict Detection
        conflicts = self.conflict_detector.detect_conflicts(candidates)
        
        # 7. Save clusters to repository
        self.repository.clear_correlations()
        self.repository.save_clusters(clusters)
        
        # 8. Run validation
        t0 = time.perf_counter()
        validation_status = self.validator.validate_package(clusters, conflicts)
        warnings.extend(validation_status.warnings)
        val_time = (time.perf_counter() - t0) * 1000.0
        
        # Compiling summary counts
        c_dist = {}
        for m in matches:
            t_name = m.correlation_type.name
            c_dist[t_name] = c_dist.get(t_name, 0) + 1
            
        avg_conf = sum(c.confidence for c in clusters) / len(clusters) if clusters else 1.0
        
        statistics = CorrelationStatistics(
            total_candidates=len(candidates),
            total_correlations=len(matches),
            total_clusters=len(clusters),
            total_conflicts=len(conflicts)
        )
        
        summary = CorrelationSummary(
            correlation_distribution=c_dist,
            cluster_distribution={},
            average_confidence=round(avg_conf, 4)
        )
        
        # Compile Timing metrics
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        metrics = self.metrics_calculator.calculate(
            processing_time_ms=elapsed_ms,
            extraction_time_ms=extraction_time,
            comparison_time_ms=comparison_time,
            clustering_time_ms=clustering_time,
            validation_time_ms=val_time,
            executions=executions_log
        )
        
        package = CorrelationPackage(
            schema_version="1.0.0",
            correlation_id=f"CORR-{str(uuid.uuid4())[:8]}",
            case_id=case_id,
            created_at=datetime.now(timezone.utc),
            clusters=clusters,
            cluster_index=cluster_index,
            conflicts=conflicts,
            statistics=statistics,
            validation=validation_status,
            metrics=metrics,
            summary=summary
        )
        
        logger.info("Correlation package built successfully.")
        return package, warnings
export_pipeline = CrossEvidenceCorrelationPipeline
