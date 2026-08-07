# -*- coding: utf-8 -*-
"""Timeline Intelligence Agent."""

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
from backend.agents.timeline_intelligence.dispatcher import TimelineDispatcher
from backend.agents.timeline_intelligence.timestamp_normalizer import TimestampNormalizer
from backend.agents.timeline_intelligence.event_builder import EventBuilder
from backend.agents.timeline_intelligence.duplicate_detector import DuplicateDetector
from backend.agents.timeline_intelligence.merger import EventMerger
from backend.agents.timeline_intelligence.sorter import ChronologicalSorter
from backend.agents.timeline_intelligence.validator import TimelineValidator
from backend.agents.timeline_intelligence.metrics import TimelineMetricsCalculator
from backend.agents.timeline_intelligence.pipeline import TimelineIntelligencePipeline
from backend.agents.timeline_intelligence.exceptions import TimelineException

logger = get_logger("agents.timeline_intelligence.agent")

class TimelineIntelligenceAgent(BaseAgent):
    """Stateless timeline agent compiling chronological sequences."""
    
    _MANIFEST = AgentManifest(
        metadata=AgentMetadata(
            name="timeline_intelligence_agent",
            version="1.0.0",
            description="Extracts, normalizes, deduplicates, and sorts timeline events from ingestion files and Knowledge Graphs.",
            supported_input_types=["AgentResultContracts"],
            supported_output_types=["TimelinePackage"],
            dependencies=["python-dateutil"]
        ),
        capabilities=[
            "timestamp_normalization_utc",
            "timezone_offset_handling",
            "duplicate_event_merging",
            "chronological_stable_sorting"
        ],
        custom_configuration_schema={}
    )

    def __init__(
        self,
        dispatcher: Optional[TimelineDispatcher] = None,
        normalizer: Optional[TimestampNormalizer] = None,
        event_builder: Optional[EventBuilder] = None,
        duplicate_detector: Optional[DuplicateDetector] = None,
        merger: Optional[EventMerger] = None,
        sorter: Optional[ChronologicalSorter] = None,
        validator: Optional[TimelineValidator] = None,
        metrics_calculator: Optional[TimelineMetricsCalculator] = None,
        pipeline: Optional[TimelineIntelligencePipeline] = None
    ) -> None:
        self.dispatcher = dispatcher or TimelineDispatcher()
        self.normalizer = normalizer or TimestampNormalizer()
        self.event_builder = event_builder or EventBuilder()
        self.duplicate_detector = duplicate_detector or DuplicateDetector()
        self.merger = merger or EventMerger()
        self.sorter = sorter or ChronologicalSorter()
        self.validator = validator or TimelineValidator()
        self.metrics_calculator = metrics_calculator or TimelineMetricsCalculator()
        
        self.pipeline = pipeline or TimelineIntelligencePipeline(
            dispatcher=self.dispatcher,
            normalizer=self.normalizer,
            event_builder=self.event_builder,
            duplicate_detector=self.duplicate_detector,
            merger=self.merger,
            sorter=self.sorter,
            validator=self.validator,
            metrics_calculator=self.metrics_calculator
        )

    def run(self, context: ProcessingContextContract, **kwargs) -> AgentResultContract:
        """Runs timeline chronology assembly.
        
        Args:
            context: Active tracing context.
            **kwargs: Must contain:
                - metadata_result (AgentResultContract): Metadata Agent output.
                - document_result (AgentResultContract): Optional Document Agent output.
                - vision_result (AgentResultContract): Optional Vision Agent output.
                - audio_result (AgentResultContract): Optional Audio Agent output.
                - graph_result (AgentResultContract): Optional Knowledge Graph output.
                
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
        document_result = kwargs.get("document_result")
        vision_result = kwargs.get("vision_result")
        audio_result = kwargs.get("audio_result")
        graph_result = kwargs.get("graph_result")
        
        try:
            if not isinstance(metadata_result, AgentResultContract):
                raise ValueError("Parameter 'metadata_result' must be an AgentResultContract.")
                
            # Execute pipeline
            package, pipeline_warnings = self.pipeline.execute(
                metadata_result=metadata_result,
                document_result=document_result,
                vision_result=vision_result,
                audio_result=audio_result,
                graph_result=graph_result
            )
            payload = package.model_dump()
            warnings.extend(pipeline_warnings)
            
        except TimelineException as e:
            status = "FAILURE"
            errors.append(e.message)
            logger.error(f"Domain timeline execution failure [Code: {e.error_code}]: {e.message}", exc_info=True)
            
        except Exception as e:
            status = "FAILURE"
            errors.append(str(e))
            logger.critical(f"System panic inside TimelineIntelligenceAgent: {e}", exc_info=True)
            
        finished_at = datetime.now(timezone.utc)
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        
        context.pipeline_stage = "timeline_intelligence"
        
        return AgentResultContract(
            agent="timeline_intelligence_agent",
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
            "agent": "Timeline Intelligence Agent",
            "status": "healthy",
            "version": __version__
        }

    def manifest(self) -> AgentManifest:
        """Exposes discovery manifest capability profile."""
        return self._MANIFEST
export_agent = TimelineIntelligenceAgent
