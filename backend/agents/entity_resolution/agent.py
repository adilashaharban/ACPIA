# -*- coding: utf-8 -*-
"""Entity Resolution Agent."""

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
from backend.agents.entity_resolution.normalizer import EntityNormalizer
from backend.agents.entity_resolution.matcher import EntityMatcher
from backend.agents.entity_resolution.merger import EntityMerger
from backend.agents.entity_resolution.confidence import EntityConfidenceCalculator
from backend.agents.entity_resolution.validator import EntityValidator
from backend.agents.entity_resolution.metrics import EntityMetricsCalculator
from backend.agents.entity_resolution.pipeline import EntityResolutionPipeline
from backend.agents.entity_resolution.exceptions import ResolutionParsingError

logger = get_logger("agents.entity_resolution.agent")

class EntityResolutionAgent(BaseAgent):
    """Stateless entity resolution agent deduplicating candidate observations."""
    
    _MANIFEST = AgentManifest(
        metadata=AgentMetadata(
            name="entity_resolution_agent",
            version="1.0.0",
            description="Extracts, standardizes, blocks, and merges candidate entities from document, vision, and audio.",
            supported_input_types=["AgentResultContracts"],
            supported_output_types=["EntityResolutionPackage"],
            dependencies=["rapidfuzz", "phonenumbers", "email-validator"]
        ),
        capabilities=[
            "entity_extraction_regex",
            "entity_normalization_e164",
            "exact_blocking_matches",
            "fuzzy_jaro_winkler_clustering",
            "confidence_aggregation_booster"
        ],
        custom_configuration_schema={}
    )

    def __init__(
        self,
        normalizer: Optional[EntityNormalizer] = None,
        matcher: Optional[EntityMatcher] = None,
        merger: Optional[EntityMerger] = None,
        confidence_calculator: Optional[EntityConfidenceCalculator] = None,
        validator: Optional[EntityValidator] = None,
        metrics_calculator: Optional[EntityMetricsCalculator] = None,
        pipeline: Optional[EntityResolutionPipeline] = None
    ) -> None:
        self.normalizer = normalizer or EntityNormalizer()
        self.matcher = matcher or EntityMatcher()
        self.merger = merger or EntityMerger()
        self.confidence_calculator = confidence_calculator or EntityConfidenceCalculator()
        self.validator = validator or EntityValidator()
        self.metrics_calculator = metrics_calculator or EntityMetricsCalculator()
        
        self.pipeline = pipeline or EntityResolutionPipeline(
            normalizer=self.normalizer,
            matcher=self.matcher,
            merger=self.merger,
            confidence_calculator=self.confidence_calculator,
            validator=self.validator,
            metrics_calculator=self.metrics_calculator
        )

    def run(self, context: ProcessingContextContract, **kwargs) -> AgentResultContract:
        """Runs candidate entity resolution.
        
        Args:
            context: Active tracing context.
            **kwargs: Must contain:
                - metadata_result (AgentResultContract): Metadata Agent output.
                - document_result (AgentResultContract): Optional Document Agent output.
                - vision_result (AgentResultContract): Optional Vision Agent output.
                - audio_result (AgentResultContract): Optional Audio Agent output.
                
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
        
        try:
            if not isinstance(metadata_result, AgentResultContract):
                raise ValueError("Parameter 'metadata_result' must be an AgentResultContract.")
                
            # Execute pipeline
            package, pipeline_warnings = self.pipeline.execute(
                metadata_result=metadata_result,
                document_result=document_result,
                vision_result=vision_result,
                audio_result=audio_result
            )
            payload = package.model_dump()
            warnings.extend(pipeline_warnings)
            
        except ResolutionParsingError as e:
            status = "FAILURE"
            errors.append(e.message)
            logger.error(f"Domain entity resolution execution failure [Code: {e.error_code}]: {e.message}", exc_info=True)
            
        except Exception as e:
            status = "FAILURE"
            errors.append(str(e))
            logger.critical(f"System panic inside EntityResolutionAgent: {e}", exc_info=True)
            
        finished_at = datetime.now(timezone.utc)
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        
        context.pipeline_stage = "entity_resolution"
        
        return AgentResultContract(
            agent="entity_resolution_agent",
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
            "agent": "Entity Resolution Agent",
            "status": "healthy",
            "version": __version__
        }

    def manifest(self) -> AgentManifest:
        """Exposes discovery manifest capability profile."""
        return self._MANIFEST
export_agent = EntityResolutionAgent
