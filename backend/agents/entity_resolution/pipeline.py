# -*- coding: utf-8 -*-
"""Entity Resolution pipeline orchestration."""

import time
from typing import Tuple, List, Dict, Any, Optional
from backend.core.logger import get_logger
from backend.agents.base import AgentResultContract
from backend.agents.entity_resolution.dispatcher import EntityDispatcher
from backend.agents.entity_resolution.normalizer import EntityNormalizer
from backend.agents.entity_resolution.matcher import EntityMatcher
from backend.agents.entity_resolution.merger import EntityMerger
from backend.agents.entity_resolution.confidence import EntityConfidenceCalculator
from backend.agents.entity_resolution.validator import EntityValidator
from backend.agents.entity_resolution.metrics import EntityMetricsCalculator
from backend.agents.entity_resolution.exceptions import ResolutionParsingError
from backend.agents.entity_resolution.extractors.metadata_extractor import MetadataExtractor
from backend.agents.entity_resolution.extractors.document_extractor import DocumentExtractor
from backend.agents.entity_resolution.extractors.vision_extractor import VisionExtractor
from backend.agents.entity_resolution.extractors.audio_extractor import AudioExtractor
from backend.agents.entity_resolution.schema import (
    EntityResolutionPackage, CanonicalEntity, ResolvedEntity, EntityStatistics,
    EntitySummary, ProcessorExecution, CandidateEntity, MatchingEvidence
)

logger = get_logger("agents.entity_resolution.pipeline")

class EntityResolutionPipeline:
    """Orchestrates multi-modal candidate entities normalization, blocking matches, and merges."""
    
    def __init__(
        self,
        normalizer: EntityNormalizer,
        matcher: EntityMatcher,
        merger: EntityMerger,
        confidence_calculator: EntityConfidenceCalculator,
        validator: EntityValidator,
        metrics_calculator: EntityMetricsCalculator
    ) -> None:
        self.normalizer = normalizer
        self.matcher = matcher
        self.merger = merger
        self.confidence_calculator = confidence_calculator
        self.validator = validator
        self.metrics_calculator = metrics_calculator

    def execute(
        self,
        metadata_result: AgentResultContract,
        document_result: Optional[AgentResultContract] = None,
        vision_result: Optional[AgentResultContract] = None,
        audio_result: Optional[AgentResultContract] = None
    ) -> Tuple[EntityResolutionPackage, List[str]]:
        """Executes entity resolution.
        
        Args:
            metadata_result: Metadata agent output.
            document_result: Document agent output.
            vision_result: Vision agent output.
            audio_result: Audio agent output.
            
        Returns:
            Tuple containing (EntityResolutionPackage, warnings list).
        """
        start_time = time.perf_counter()
        warnings: List[str] = []
        executions_log: List[ProcessorExecution] = []
        
        logger.info("Entity Resolution pipeline started.")
        
        meta_payload = metadata_result.payload
        if not meta_payload:
            raise ResolutionParsingError("Input metadata payload is empty.")
            
        evidence_id = meta_payload.get("evidence_id")
        
        # 1. Fetch paths from database context
        from backend.database.session import get_db_context
        from backend.database.repositories.evidence_repository import EvidenceRepository
        
        file_path = None
        expected_hash = None
        
        with get_db_context() as db:
            repo = EvidenceRepository(db)
            db_evidence = repo.get_by_id(evidence_id)
            if not db_evidence:
                raise ResolutionParsingError(f"Evidence {evidence_id} not registered in database.")
            file_path = db_evidence.file_path
            expected_hash = db_evidence.sha256_hash
            
        # 2. Checksum validation
        self.validator.verify_integrity(file_path, expected_hash)
        
        # 3. Harvest candidates pool from extractors
        candidates: List[CandidateEntity] = []
        
        # Metadata extraction
        t0 = time.perf_counter()
        candidates.extend(MetadataExtractor.extract(meta_payload, file_path, evidence_id))
        executions_log.append(ProcessorExecution(processor_name="MetadataExtractor", processor_version="1.0.0", execution_time_ms=round((time.perf_counter() - t0)*1000, 2), status="SUCCESS"))
        
        # Document extraction
        if document_result and document_result.payload:
            t0 = time.perf_counter()
            candidates.extend(DocumentExtractor.extract(document_result.payload, file_path, evidence_id))
            executions_log.append(ProcessorExecution(processor_name="DocumentExtractor", processor_version="1.0.0", execution_time_ms=round((time.perf_counter() - t0)*1000, 2), status="SUCCESS"))
            
        # Vision extraction
        if vision_result and vision_result.payload:
            t0 = time.perf_counter()
            candidates.extend(VisionExtractor.extract(vision_result.payload, file_path, evidence_id))
            executions_log.append(ProcessorExecution(processor_name="VisionExtractor", processor_version="1.0.0", execution_time_ms=round((time.perf_counter() - t0)*1000, 2), status="SUCCESS"))
            
        # Audio extraction
        if audio_result and audio_result.payload:
            t0 = time.perf_counter()
            candidates.extend(AudioExtractor.extract(audio_result.payload, file_path, evidence_id))
            executions_log.append(ProcessorExecution(processor_name="AudioExtractor", processor_version="1.0.0", execution_time_ms=round((time.perf_counter() - t0)*1000, 2), status="SUCCESS"))
            
        candidate_count = len(candidates)
        
        # 4. Normalization Engine
        normalized_candidates: List[CandidateEntity] = []
        for c in candidates:
            normalized_candidates.append(self.normalizer.normalize_candidate(c))
        norm_count = len(normalized_candidates)
        
        # 5. Blocking matches partitions
        blocked_buckets = self.matcher.block_candidates(normalized_candidates)
        
        # Output resolved entities list
        resolved_entities: List[CanonicalEntity] = []
        match_count = 0
        merge_count = 0
        
        # 6. Matching & Merge Engine per block
        for entity_type_name, bucket in blocked_buckets.items():
            # Quick cluster assignment using a simplified grouping loop
            visited_indices = set()
            
            for i in range(len(bucket)):
                if i in visited_indices:
                    continue
                    
                cluster = [bucket[i]]
                matches_ev: List[MatchingEvidence] = []
                visited_indices.add(i)
                
                for j in range(i + 1, len(bucket)):
                    if j in visited_indices:
                        continue
                        
                    is_match, evidence = self.matcher.match_pair(bucket[i], bucket[j])
                    if is_match:
                        cluster.append(bucket[j])
                        visited_indices.add(j)
                        match_count += 1
                        if evidence:
                            matches_ev.append(evidence)
                            
                # 7. Confidence aggregations
                conf_breakdown = self.confidence_calculator.calculate(cluster, matches_ev)
                
                # 8. Merge clusters
                canonical = self.merger.merge_cluster(cluster, matches_ev, conf_breakdown)
                resolved_entities.append(canonical)
                merge_count += len(cluster) - 1
                
        # 9. Validation
        validation_meta = self.validator.validate_entities(resolved_entities)
        warnings.extend(validation_meta.warnings)
        
        # 10. Statistics
        statistics = EntityStatistics(
            total_candidates=candidate_count,
            resolved_count=len(resolved_entities),
            merged_count=merge_count,
            cluster_count=len(resolved_entities)
        )
        
        # 11. Summary
        resolved_types: Dict[str, int] = {}
        for ent in resolved_entities:
            t_name = ent.entity_type.name
            resolved_types[t_name] = resolved_types.get(t_name, 0) + 1
            
        avg_conf = sum([e.confidence_breakdown.final_confidence for e in resolved_entities]) / len(resolved_entities) if resolved_entities else 1.0
        
        summary = EntitySummary(
            resolved_types=resolved_types,
            average_resolution_confidence=round(float(avg_conf), 4)
        )
        
        # 12. Compile metrics
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        metrics = self.metrics_calculator.calculate(
            processing_time_ms=elapsed_ms,
            candidate_count=candidate_count,
            normalization_count=norm_count,
            match_count=match_count,
            merge_count=merge_count,
            executions=executions_log
        )
        
        package = EntityResolutionPackage(
            schema_version="1.0.0",
            entities=resolved_entities,
            statistics=statistics,
            validation=validation_meta,
            metrics=metrics,
            summary=summary
        )
        
        logger.info("Entity resolution package built successfully.")
        return package, warnings
export_pipeline = EntityResolutionPipeline
