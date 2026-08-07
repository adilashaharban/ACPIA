# -*- coding: utf-8 -*-
"""Timeline Intelligence pipeline orchestration."""

import time
from datetime import datetime, timezone
import uuid
from typing import Tuple, List, Dict, Any, Optional
from backend.core.logger import get_logger
from backend.agents.base import AgentResultContract
from backend.agents.timeline_intelligence.dispatcher import TimelineDispatcher
from backend.agents.timeline_intelligence.timestamp_normalizer import TimestampNormalizer
from backend.agents.timeline_intelligence.event_builder import EventBuilder
from backend.agents.timeline_intelligence.duplicate_detector import DuplicateDetector
from backend.agents.timeline_intelligence.merger import EventMerger
from backend.agents.timeline_intelligence.sorter import ChronologicalSorter
from backend.agents.timeline_intelligence.validator import TimelineValidator
from backend.agents.timeline_intelligence.metrics import TimelineMetricsCalculator
from backend.agents.timeline_intelligence.repositories.memory_repository import MemoryRepository
from backend.agents.timeline_intelligence.exceptions import TimelineException
from backend.agents.timeline_intelligence.schema import (
    TimelinePackage, TimelineEvent, TimelineStatistics, TimelineSummary,
    ProcessorExecution, TimelineValidation
)

logger = get_logger("agents.timeline_intelligence.pipeline")

class TimelineIntelligencePipeline:
    """Orchestrates candidate timeline observations parsing, sorting, and database storage."""
    
    def __init__(
        self,
        dispatcher: TimelineDispatcher,
        normalizer: TimestampNormalizer,
        event_builder: EventBuilder,
        duplicate_detector: DuplicateDetector,
        merger: EventMerger,
        sorter: ChronologicalSorter,
        validator: TimelineValidator,
        metrics_calculator: TimelineMetricsCalculator,
        repository: Optional[MemoryRepository] = None
    ) -> None:
        self.dispatcher = dispatcher
        self.normalizer = normalizer
        self.event_builder = event_builder
        self.duplicate_detector = duplicate_detector
        self.merger = merger
        self.sorter = sorter
        self.validator = validator
        self.metrics_calculator = metrics_calculator
        self.repository = repository or MemoryRepository()

    def execute(
        self,
        metadata_result: AgentResultContract,
        document_result: Optional[AgentResultContract] = None,
        vision_result: Optional[AgentResultContract] = None,
        audio_result: Optional[AgentResultContract] = None,
        graph_result: Optional[AgentResultContract] = None
    ) -> Tuple[TimelinePackage, List[str]]:
        """Runs timeline construction.
        
        Args:
            metadata_result: Ingestion metadata result.
            document_result: Optional Document agent result.
            vision_result: Optional Vision agent result.
            audio_result: Optional Audio agent result.
            graph_result: Optional Knowledge Graph result.
            
        Returns:
            Tuple containing (TimelinePackage, warnings list).
        """
        start_time = time.perf_counter()
        warnings: List[str] = []
        executions_log: List[ProcessorExecution] = []
        
        logger.info("Timeline Intelligence pipeline started.")
        
        meta_payload = metadata_result.payload
        if not meta_payload:
            raise TimelineException("Input metadata payload is empty.")
            
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
                raise TimelineException(f"Evidence {evidence_id} not registered in database.")
            file_path = db_evidence.file_path
            expected_hash = db_evidence.sha256_hash
            
        # 2. Checksum validation
        self.validator.verify_integrity(file_path, expected_hash)
        
        # Extract graph_id if graph_result is provided
        graph_id = None
        graph_payload = None
        if graph_result and graph_result.payload:
            graph_payload = graph_result.payload
            graph_id = graph_payload.get("graph_id")
            
        # 3. Harvest candidates
        t0 = time.perf_counter()
        candidates = self.dispatcher.gather_candidates(
            metadata_payload=meta_payload,
            document_payload=document_result.payload if document_result else None,
            vision_payload=vision_result.payload if vision_result else None,
            audio_payload=audio_result.payload if audio_result else None,
            graph_payload=graph_payload,
            file_path=file_path,
            evidence_id=evidence_id
        )
        extraction_time = (time.perf_counter() - t0) * 1000.0
        
        # 4. Normalize timestamps and Build TimelineEvents
        t0 = time.perf_counter()
        events: List[TimelineEvent] = []
        for cand in candidates:
            try:
                norm_time = self.normalizer.normalize(cand["raw_timestamp"])
                precision = self.normalizer.infer_precision(cand["raw_timestamp"])
                event = self.event_builder.build_event(
                    cand=cand,
                    processing_id=metadata_result.processing_context.evidence_id,
                    normalized_time=norm_time,
                    precision=precision
                )
                events.append(event)
            except Exception as e:
                warnings.append(f"Skipped candidate event creation due to normalization error: {e}")
        normalization_time = (time.perf_counter() - t0) * 1000.0
        executions_log.append(
            ProcessorExecution(
                processor_name="TimestampNormalizer",
                processor_version="1.0.0",
                execution_time_ms=round(normalization_time, 2),
                status="SUCCESS"
            )
        )
        
        # 5. Duplicate Detection & Merge
        t0 = time.perf_counter()
        groups = self.duplicate_detector.detect_groups(events)
        merged_events: List[TimelineEvent] = []
        for gp in groups:
            if len(gp) > 1:
                merged_events.append(self.merger.merge_events(gp))
            else:
                merged_events.append(gp[0])
        merge_time = (time.perf_counter() - t0) * 1000.0
        executions_log.append(
            ProcessorExecution(
                processor_name="DuplicateDetector",
                processor_version="1.0.0",
                execution_time_ms=round(merge_time, 2),
                status="SUCCESS"
            )
        )
        
        # 6. Sort and assign sequence number indices
        t0 = time.perf_counter()
        sorted_events, event_index = self.sorter.sort_and_index(merged_events)
        sort_time = (time.perf_counter() - t0) * 1000.0
        executions_log.append(
            ProcessorExecution(
                processor_name="ChronologicalSorter",
                processor_version="1.0.0",
                execution_time_ms=round(sort_time, 2),
                status="SUCCESS"
            )
        )
        
        # 7. Save events to repository
        t0 = time.perf_counter()
        self.repository.clear_timeline()
        self.repository.save_events(sorted_events)
        repo_time = (time.perf_counter() - t0) * 1000.0
        
        # 8. Validate timeline
        t0 = time.perf_counter()
        validation_status = self.validator.validate_timeline(sorted_events)
        warnings.extend(validation_status.warnings)
        val_time = (time.perf_counter() - t0) * 1000.0
        
        # Calculate stats
        duration_days = 0.0
        if len(sorted_events) > 1:
            diff = sorted_events[-1].normalized_timestamp_utc - sorted_events[0].normalized_timestamp_utc
            duration_days = diff.total_seconds() / 86400.0
            
        precision_dist = {}
        for ev in sorted_events:
            p_name = ev.timestamp_precision.name
            precision_dist[p_name] = precision_dist.get(p_name, 0) + 1
            
        statistics = TimelineStatistics(
            total_events=len(sorted_events),
            precision_distribution=precision_dist,
            duration_days=round(duration_days, 4)
        )
        
        # Summary details
        event_dist = {}
        for ev in sorted_events:
            e_name = ev.event_type.name
            event_dist[e_name] = event_dist.get(e_name, 0) + 1
            
        summary = TimelineSummary(
            event_type_distribution=event_dist,
            earliest_timestamp=sorted_events[0].normalized_timestamp_utc if sorted_events else None,
            latest_timestamp=sorted_events[-1].normalized_timestamp_utc if sorted_events else None
        )
        
        # 9. Compile metrics
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        metrics = self.metrics_calculator.calculate(
            processing_time_ms=elapsed_ms,
            timestamp_normalization_time_ms=normalization_time,
            merge_time_ms=merge_time,
            sorting_time_ms=sort_time,
            validation_time_ms=val_time,
            builder_time_ms=extraction_time,
            executions=executions_log
        )
        
        package = TimelinePackage(
            schema_version="1.0.0",
            timeline_id=f"TMLN-{str(uuid.uuid4())[:8]}",
            case_id=case_id,
            graph_id=graph_id,
            timeline_version="1.0.0",
            created_at=datetime.now(timezone.utc),
            events=sorted_events,
            event_index=event_index,
            statistics=statistics,
            validation=validation_status,
            metrics=metrics,
            summary=summary
        )
        
        logger.info("Timeline package built successfully.")
        return package, warnings
export_pipeline = TimelineIntelligencePipeline
