# -*- coding: utf-8 -*-
"""Metadata Agent."""

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
from backend.agents.metadata.dispatcher import MetadataDispatcher
from backend.agents.metadata.normalizer import MetadataNormalizer
from backend.agents.metadata.validator import MetadataValidator
from backend.agents.metadata.metrics import MetadataMetricsCalculator
from backend.agents.metadata.pipeline import MetadataPipeline
from backend.agents.metadata.exceptions import MetadataExtractionError

logger = get_logger("agents.metadata.agent")

class MetadataAgent(BaseAgent):
    """Stateless metadata extraction agent executing forensic headers validations."""
    
    # Declarative Manifest
    _MANIFEST = AgentManifest(
        metadata=AgentMetadata(
            name="metadata_agent",
            version="1.0.0",
            description="Extracts and normalizes forensic headers and technical characteristics from evidence.",
            supported_input_types=["AgentResultContract (from evidence_intake)"],
            supported_output_types=["MetadataPackage"],
            dependencies=["mutagen", "piexif", "hachoir", "PyPDF2"]
        ),
        capabilities=[
            "exif_decoding",
            "gps_degrees_conversion",
            "media_stream_probing",
            "document_properties_extraction",
            "completeness_scoring"
        ],
        custom_configuration_schema={}
    )

    def __init__(
        self,
        dispatcher: Optional[MetadataDispatcher] = None,
        validator: Optional[MetadataValidator] = None,
        normalizer: Optional[MetadataNormalizer] = None,
        metrics_calculator: Optional[MetadataMetricsCalculator] = None,
        pipeline: Optional[MetadataPipeline] = None
    ) -> None:
        """Initializes the MetadataAgent with injected dependencies.
        
        Args:
            dispatcher: Injected MIME dispatcher.
            validator: Checksum and coordinates boundary validator.
            normalizer: Data formatter.
            metrics_calculator: Completeness metric calculator.
            pipeline: Orchestrated pipeline executor.
        """
        self.dispatcher = dispatcher or MetadataDispatcher()
        self.validator = validator or MetadataValidator()
        self.normalizer = normalizer or MetadataNormalizer()
        self.metrics_calculator = metrics_calculator or MetadataMetricsCalculator()
        
        # Instantiate pipeline using dependencies
        self.pipeline = pipeline or MetadataPipeline(
            dispatcher=self.dispatcher,
            validator=self.validator,
            normalizer=self.normalizer,
            metrics_calculator=self.metrics_calculator
        )

    def run(self, context: ProcessingContextContract, **kwargs) -> AgentResultContract:
        """Executes the metadata extraction pipeline.
        
        Args:
            context: Active tracing context.
            **kwargs: Must contain:
                - intake_result (AgentResultContract): Result output from Evidence Intake Agent.
                
        Returns:
            Standardized AgentResultContract output.
        """
        started_at = datetime.now(timezone.utc)
        start_time = time.perf_counter()
        
        status = "SUCCESS"
        payload: Dict[str, Any] = {}
        warnings: List[str] = []
        errors: List[str] = []
        
        intake_result = kwargs.get("intake_result")
        
        try:
            if not isinstance(intake_result, AgentResultContract):
                raise ValueError("Parameter 'intake_result' must be an AgentResultContract.")
                
            # Execute pipeline
            package, pipeline_warnings = self.pipeline.execute(intake_result)
            payload = package.model_dump()
            warnings.extend(pipeline_warnings)
            
        except MetadataExtractionError as e:
            status = "FAILURE"
            errors.append(e.message)
            logger.error(f"Domain extraction failure [Code: {e.error_code}]: {e.message}", exc_info=True)
            
        except Exception as e:
            status = "FAILURE"
            errors.append(str(e))
            logger.critical(f"System panic inside MetadataAgent: {e}", exc_info=True)
            
        finished_at = datetime.now(timezone.utc)
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        
        # Update context stage
        context.pipeline_stage = "metadata"
        
        return AgentResultContract(
            agent="metadata_agent",
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
        """Exposes health metrics and versions."""
        return {
            "agent": "Metadata Agent",
            "status": "healthy",
            "version": __version__
        }

    def manifest(self) -> AgentManifest:
        """Exposes capability registration details."""
        return self._MANIFEST
