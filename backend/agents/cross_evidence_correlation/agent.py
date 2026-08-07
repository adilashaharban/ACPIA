# -*- coding: utf-8 -*-
"""Cross-Evidence Correlation Agent."""

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
from backend.agents.cross_evidence_correlation.dispatcher import Dispatcher
from backend.agents.cross_evidence_correlation.comparator import Comparator
from backend.agents.cross_evidence_correlation.matcher import Matcher
from backend.agents.cross_evidence_correlation.cluster_builder import ClusterBuilder
from backend.agents.cross_evidence_correlation.conflict_detector import ConflictDetector
from backend.agents.cross_evidence_correlation.validator import Validator
from backend.agents.cross_evidence_correlation.metrics import MetricsCalculator
from backend.agents.cross_evidence_correlation.pipeline import CrossEvidenceCorrelationPipeline
from backend.agents.cross_evidence_correlation.exceptions import CorrelationError

logger = get_logger("agents.cross_evidence_correlation.agent")

class CrossEvidenceCorrelationAgent(BaseAgent):
    """Stateless correlation agent compiling cross-modal link packages."""
    
    _MANIFEST = AgentManifest(
        metadata=AgentMetadata(
            name="cross_evidence_correlation_agent",
            version="1.0.0",
            description="Identifies deterministic links across entities, timelines, metadata, visual, and graph structures.",
            supported_input_types=["AgentResultContracts"],
            supported_output_types=["CorrelationPackage"],
            dependencies=["networkx", "rapidfuzz"]
        ),
        capabilities=[
            "entity_levenshtein_similarity",
            "gps_haversine_distance",
            "temporal_window_overlaps",
            "connected_components_clustering"
        ],
        custom_configuration_schema={}
    )

    def __init__(
        self,
        dispatcher: Optional[Dispatcher] = None,
        comparator: Optional[Comparator] = None,
        matcher: Optional[Matcher] = None,
        cluster_builder: Optional[ClusterBuilder] = None,
        conflict_detector: Optional[ConflictDetector] = None,
        validator: Optional[Validator] = None,
        metrics_calculator: Optional[MetricsCalculator] = None,
        pipeline: Optional[CrossEvidenceCorrelationPipeline] = None
    ) -> None:
        self.dispatcher = dispatcher or Dispatcher()
        self.comparator = comparator or Comparator()
        self.matcher = matcher or Matcher(comparator=self.comparator)
        self.cluster_builder = cluster_builder or ClusterBuilder()
        self.conflict_detector = conflict_detector or ConflictDetector()
        self.validator = validator or Validator()
        self.metrics_calculator = metrics_calculator or MetricsCalculator()
        
        self.pipeline = pipeline or CrossEvidenceCorrelationPipeline(
            dispatcher=self.dispatcher,
            matcher=self.matcher,
            cluster_builder=self.cluster_builder,
            conflict_detector=self.conflict_detector,
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
                - entity_result (AgentResultContract): Optional Entity Resolution output.
                - graph_result (AgentResultContract): Optional Knowledge Graph output.
                - timeline_result (AgentResultContract): Optional Timeline output.
                
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
        entity_result = kwargs.get("entity_result")
        graph_result = kwargs.get("graph_result")
        timeline_result = kwargs.get("timeline_result")
        
        try:
            if not isinstance(metadata_result, AgentResultContract):
                raise ValueError("Parameter 'metadata_result' must be an AgentResultContract.")
                
            # Execute pipeline
            package, pipeline_warnings = self.pipeline.execute(
                metadata_result=metadata_result,
                document_result=document_result,
                vision_result=vision_result,
                audio_result=audio_result,
                entity_result=entity_result,
                graph_result=graph_result,
                timeline_result=timeline_result
            )
            payload = package.model_dump()
            warnings.extend(pipeline_warnings)
            
        except CorrelationError as e:
            status = "FAILURE"
            errors.append(e.message)
            logger.error(f"Domain correlation execution failure [Code: {e.error_code}]: {e.message}", exc_info=True)
            
        except Exception as e:
            status = "FAILURE"
            errors.append(str(e))
            logger.critical(f"System panic inside CrossEvidenceCorrelationAgent: {e}", exc_info=True)
            
        finished_at = datetime.now(timezone.utc)
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        
        context.pipeline_stage = "cross_evidence_correlation"
        
        return AgentResultContract(
            agent="cross_evidence_correlation_agent",
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
            "agent": "Cross-Evidence Correlation Agent",
            "status": "healthy",
            "version": __version__
        }

    def manifest(self) -> AgentManifest:
        """Exposes discovery manifest capability profile."""
        return self._MANIFEST
export_agent = CrossEvidenceCorrelationAgent
