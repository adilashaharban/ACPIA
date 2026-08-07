# -*- coding: utf-8 -*-
"""Vision Intelligence Agent."""

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
from backend.agents.vision_intelligence.dispatcher import VisionDispatcher
from backend.agents.vision_intelligence.normalizer import VisionNormalizer
from backend.agents.vision_intelligence.validator import VisionValidator
from backend.agents.vision_intelligence.metrics import VisionMetricsCalculator
from backend.agents.vision_intelligence.pipeline import VisionIntelligencePipeline
from backend.agents.vision_intelligence.exceptions import VisionParsingError

logger = get_logger("agents.vision_intelligence.agent")

class VisionIntelligenceAgent(BaseAgent):
    """Stateless vision intelligence agent running object detection and quality sweeps."""
    
    _MANIFEST = AgentManifest(
        metadata=AgentMetadata(
            name="vision_intelligence_agent",
            version="1.0.0",
            description="Performs object detection, quality scans, and perceptual duplicate checking.",
            supported_input_types=["AgentResultContract (from metadata_agent)"],
            supported_output_types=["VisionPackage"],
            dependencies=["opencv-python", "imagehash", "pillow", "numpy"]
        ),
        capabilities=[
            "object_detection_cv",
            "face_localization_cv",
            "perceptual_duplicate_checking",
            "image_quality_scoring",
            "dominant_color_extraction"
        ],
        custom_configuration_schema={}
    )

    def __init__(
        self,
        dispatcher: Optional[VisionDispatcher] = None,
        validator: Optional[VisionValidator] = None,
        normalizer: Optional[VisionNormalizer] = None,
        metrics_calculator: Optional[VisionMetricsCalculator] = None,
        pipeline: Optional[VisionIntelligencePipeline] = None
    ) -> None:
        self.dispatcher = dispatcher or VisionDispatcher()
        self.validator = validator or VisionValidator()
        self.normalizer = normalizer or VisionNormalizer()
        self.metrics_calculator = metrics_calculator or VisionMetricsCalculator()
        
        self.pipeline = pipeline or VisionIntelligencePipeline(
            dispatcher=self.dispatcher,
            validator=self.validator,
            normalizer=self.normalizer,
            metrics_calculator=self.metrics_calculator
        )

    def run(self, context: ProcessingContextContract, **kwargs) -> AgentResultContract:
        """Runs visual scan analysis.
        
        Args:
            context: Active tracing context.
            **kwargs: Must contain:
                - metadata_result (AgentResultContract): Metadata Agent output contract.
                
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
        
        try:
            if not isinstance(metadata_result, AgentResultContract):
                raise ValueError("Parameter 'metadata_result' must be an AgentResultContract.")
                
            # Execute pipeline
            package, pipeline_warnings = self.pipeline.execute(metadata_result)
            payload = package.model_dump()
            warnings.extend(pipeline_warnings)
            
        except VisionParsingError as e:
            status = "FAILURE"
            errors.append(e.message)
            logger.error(f"Domain vision execution failure [Code: {e.error_code}]: {e.message}", exc_info=True)
            
        except Exception as e:
            status = "FAILURE"
            errors.append(str(e))
            logger.critical(f"System panic inside VisionIntelligenceAgent: {e}", exc_info=True)
            
        finished_at = datetime.now(timezone.utc)
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        
        context.pipeline_stage = "vision_intelligence"
        
        return AgentResultContract(
            agent="vision_intelligence_agent",
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
            "agent": "Vision Intelligence Agent",
            "status": "healthy",
            "version": __version__
        }

    def manifest(self) -> AgentManifest:
        """Exposes discovery manifest capability profile."""
        return self._MANIFEST
export_agent = VisionIntelligenceAgent
