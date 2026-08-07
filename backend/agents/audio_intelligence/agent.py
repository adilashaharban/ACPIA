# -*- coding: utf-8 -*-
"""Audio Intelligence Agent."""

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
from backend.agents.audio_intelligence.dispatcher import AudioDispatcher
from backend.agents.audio_intelligence.normalizer import AudioNormalizer
from backend.agents.audio_intelligence.validator import AudioValidator
from backend.agents.audio_intelligence.metrics import AudioMetricsCalculator
from backend.agents.audio_intelligence.pipeline import AudioIntelligencePipeline
from backend.agents.audio_intelligence.exceptions import AudioParsingError

logger = get_logger("agents.audio_intelligence.agent")

class AudioIntelligenceAgent(BaseAgent):
    """Stateless audio intelligence agent transcribing conversation timelines."""
    
    _MANIFEST = AgentManifest(
        metadata=AgentMetadata(
            name="audio_intelligence_agent",
            version="1.0.0",
            description="Performs voice activity segmentation, speaker diarization, and speech literal transcribing.",
            supported_input_types=["AgentResultContract (from metadata_agent)"],
            supported_output_types=["AudioPackage"],
            dependencies=["librosa", "numpy", "soundfile"]
        ),
        capabilities=[
            "speech_to_text_transcription",
            "speaker_diarization_labeling",
            "voice_activity_detection",
            "decibel_quality_scoring",
            "silence_segmentation"
        ],
        custom_configuration_schema={}
    )

    def __init__(
        self,
        dispatcher: Optional[AudioDispatcher] = None,
        validator: Optional[AudioValidator] = None,
        normalizer: Optional[AudioNormalizer] = None,
        metrics_calculator: Optional[AudioMetricsCalculator] = None,
        pipeline: Optional[AudioIntelligencePipeline] = None
    ) -> None:
        self.dispatcher = dispatcher or AudioDispatcher()
        self.validator = validator or AudioValidator()
        self.normalizer = normalizer or AudioNormalizer()
        self.metrics_calculator = metrics_calculator or AudioMetricsCalculator()
        
        self.pipeline = pipeline or AudioIntelligencePipeline(
            dispatcher=self.dispatcher,
            validator=self.validator,
            normalizer=self.normalizer,
            metrics_calculator=self.metrics_calculator
        )

    def run(self, context: ProcessingContextContract, **kwargs) -> AgentResultContract:
        """Runs acoustic scan analysis.
        
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
            
        except AudioParsingError as e:
            status = "FAILURE"
            errors.append(e.message)
            logger.error(f"Domain audio execution failure [Code: {e.error_code}]: {e.message}", exc_info=True)
            
        except Exception as e:
            status = "FAILURE"
            errors.append(str(e))
            logger.critical(f"System panic inside AudioIntelligenceAgent: {e}", exc_info=True)
            
        finished_at = datetime.now(timezone.utc)
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        
        context.pipeline_stage = "audio_intelligence"
        
        return AgentResultContract(
            agent="audio_intelligence_agent",
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
            "agent": "Audio Intelligence Agent",
            "status": "healthy",
            "version": __version__
        }

    def manifest(self) -> AgentManifest:
        """Exposes discovery manifest capability profile."""
        return self._MANIFEST
export_agent = AudioIntelligenceAgent
