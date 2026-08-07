# -*- coding: utf-8 -*-
"""Document Intelligence Agent."""

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
from backend.agents.document_intelligence.dispatcher import DocumentDispatcher
from backend.agents.document_intelligence.normalizer import DocumentNormalizer
from backend.agents.document_intelligence.validator import DocumentValidator
from backend.agents.document_intelligence.metrics import DocumentMetricsCalculator
from backend.agents.document_intelligence.pipeline import DocumentIntelligencePipeline
from backend.agents.document_intelligence.exceptions import DocumentParsingError

logger = get_logger("agents.document_intelligence.agent")

class DocumentIntelligenceAgent(BaseAgent):
    """Stateless document intelligence agent extracting columns, tables, and paragraphs."""
    
    # Declarative Manifest
    _MANIFEST = AgentManifest(
        metadata=AgentMetadata(
            name="document_intelligence_agent",
            version="1.0.0",
            description="Parses structured documents and runs character recognition layouts.",
            supported_input_types=["AgentResultContract (from metadata_agent)"],
            supported_output_types=["DocumentPackage"],
            dependencies=["pdfplumber", "python-docx", "BeautifulSoup4", "pandas", "langdetect"]
        ),
        capabilities=[
            "pdf_structural_parsing",
            "table_extraction",
            "form_key_value_extraction",
            "ocr_fallback_pipeline",
            "multilingual_detection"
        ],
        custom_configuration_schema={}
    )

    def __init__(
        self,
        dispatcher: Optional[DocumentDispatcher] = None,
        validator: Optional[DocumentValidator] = None,
        normalizer: Optional[DocumentNormalizer] = None,
        metrics_calculator: Optional[DocumentMetricsCalculator] = None,
        pipeline: Optional[DocumentIntelligencePipeline] = None
    ) -> None:
        """Initializes dependencies."""
        self.dispatcher = dispatcher or DocumentDispatcher()
        self.validator = validator or DocumentValidator()
        self.normalizer = normalizer or DocumentNormalizer()
        self.metrics_calculator = metrics_calculator or DocumentMetricsCalculator()
        
        # Instantiate pipeline using dependencies
        self.pipeline = pipeline or DocumentIntelligencePipeline(
            dispatcher=self.dispatcher,
            validator=self.validator,
            normalizer=self.normalizer,
            metrics_calculator=self.metrics_calculator
        )

    def run(self, context: ProcessingContextContract, **kwargs) -> AgentResultContract:
        """Runs document parsing.
        
        Args:
            context: Active tracing context.
            **kwargs: Must contain:
                - metadata_result (AgentResultContract): Output from Metadata Agent.
                
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
            
        except DocumentParsingError as e:
            status = "FAILURE"
            errors.append(e.message)
            logger.error(f"Domain document parsing failure [Code: {e.error_code}]: {e.message}", exc_info=True)
            
        except Exception as e:
            status = "FAILURE"
            errors.append(str(e))
            logger.critical(f"System panic inside DocumentIntelligenceAgent: {e}", exc_info=True)
            
        finished_at = datetime.now(timezone.utc)
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        
        # Update context stage
        context.pipeline_stage = "document_intelligence"
        
        return AgentResultContract(
            agent="document_intelligence_agent",
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
            "agent": "Document Intelligence Agent",
            "status": "healthy",
            "version": __version__
        }

    def manifest(self) -> AgentManifest:
        """Exposes discovery manifest."""
        return self._MANIFEST
