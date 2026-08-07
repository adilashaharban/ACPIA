# -*- coding: utf-8 -*-
"""Investigation Reasoning Agent."""

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
from backend.agents.investigation_reasoning.prompt_builder import PromptBuilder
from backend.agents.investigation_reasoning.context_validator import ContextValidator
from backend.agents.investigation_reasoning.structured_parser import StructuredParser
from backend.agents.investigation_reasoning.finding_builder import FindingBuilder
from backend.agents.investigation_reasoning.citation_builder import CitationBuilder
from backend.agents.investigation_reasoning.citation_validator import CitationValidator
from backend.agents.investigation_reasoning.confidence_calculator import ConfidenceCalculator
from backend.agents.investigation_reasoning.contradiction_detector import ContradictionDetector
from backend.agents.investigation_reasoning.gap_detector import GapDetector
from backend.agents.investigation_reasoning.reasoning_engine import ReasoningEngine
from backend.agents.investigation_reasoning.dispatcher import Dispatcher
from backend.agents.investigation_reasoning.validator import Validator
from backend.agents.investigation_reasoning.metrics import MetricsCalculator
from backend.agents.investigation_reasoning.cache.reasoning_cache import ReasoningCache
from backend.agents.investigation_reasoning.repositories.sqlite_repository import SQLiteRepository
from backend.agents.investigation_reasoning.pipeline import ReasoningPipeline
from backend.agents.investigation_reasoning.exceptions import ReasoningError
from backend.agents.investigation_reasoning.schema import InvestigationRequest, InvestigationMode

logger = get_logger("agents.investigation_reasoning.agent")

class InvestigationReasoningAgent(BaseAgent):
    """Stateless reasoning agent compiling structured factual observations from LLMs."""
    
    _MANIFEST = AgentManifest(
        metadata=AgentMetadata(
            name="investigation_reasoning_agent",
            version="1.0.0",
            description="Performs evidence-grounded reasoning over retrieved context to produce structured findings.",
            supported_input_types=["InvestigationRequest", "RetrievalPackage"],
            supported_output_types=["ReasoningPackage"],
            dependencies=["instructor", "langchain"]
        ),
        capabilities=[
            "structured_findings",
            "citation_validations",
            "confidence_aggregation",
            "contradiction_detector"
        ],
        custom_configuration_schema={}
    )

    def __init__(
        self,
        prompt_builder: Optional[PromptBuilder] = None,
        context_validator: Optional[ContextValidator] = None,
        structured_parser: Optional[StructuredParser] = None,
        finding_builder: Optional[FindingBuilder] = None,
        citation_builder: Optional[CitationBuilder] = None,
        citation_validator: Optional[CitationValidator] = None,
        confidence_calculator: Optional[ConfidenceCalculator] = None,
        contradiction_detector: Optional[ContradictionDetector] = None,
        gap_detector: Optional[GapDetector] = None,
        reasoning_engine: Optional[ReasoningEngine] = None,
        validator: Optional[Validator] = None,
        metrics_calculator: Optional[MetricsCalculator] = None,
        cache: Optional[ReasoningCache] = None,
        repository: Optional[SQLiteRepository] = None,
        pipeline: Optional[ReasoningPipeline] = None
    ) -> None:
        self.prompt_builder = prompt_builder or PromptBuilder()
        self.context_validator = context_validator or ContextValidator()
        self.structured_parser = structured_parser or StructuredParser()
        self.finding_builder = finding_builder or FindingBuilder()
        self.citation_builder = citation_builder or CitationBuilder()
        self.citation_validator = citation_validator or CitationValidator()
        self.confidence_calculator = confidence_calculator or ConfidenceCalculator()
        self.contradiction_detector = contradiction_detector or ContradictionDetector()
        self.gap_detector = gap_detector or GapDetector()
        self.dispatcher = Dispatcher()
        self.reasoning_engine = reasoning_engine or ReasoningEngine(dispatcher=self.dispatcher)
        self.validator = validator or Validator()
        self.metrics_calculator = metrics_calculator or MetricsCalculator()
        
        self.cache = cache or ReasoningCache()
        self.repository = repository or SQLiteRepository()
        
        self.pipeline = pipeline or ReasoningPipeline(
            prompt_builder=self.prompt_builder,
            context_validator=self.context_validator,
            structured_parser=self.structured_parser,
            finding_builder=self.finding_builder,
            citation_builder=self.citation_builder,
            citation_validator=self.citation_validator,
            confidence_calculator=self.confidence_calculator,
            contradiction_detector=self.contradiction_detector,
            gap_detector=self.gap_detector,
            reasoning_engine=self.reasoning_engine,
            validator=self.validator,
            metrics_calculator=self.metrics_calculator,
            cache=self.cache,
            repository=self.repository
        )

    def run(self, context: ProcessingContextContract, **kwargs) -> AgentResultContract:
        """Executes indexing or query retrieval pipeline.
        
        Args:
            context: Active tracing context.
            **kwargs: Must contain:
                - request (InvestigationRequest): Action query details.
                - retrieval_pkg (RetrievalPackage): Base grounding search context.
                - correlation_payload (Dict): Optional Correlation output.
                - timeline_payload (Dict): Optional Timeline output.
                - graph_payload (Dict): Optional Graph output.
                - entity_payload (Dict): Optional Entity Resolution output.
                
        Returns:
            Standardized AgentResultContract output.
        """
        started_at = datetime.now(timezone.utc)
        start_time = time.perf_counter()
        
        status = "SUCCESS"
        payload: Dict[str, Any] = {}
        warnings: List[str] = []
        errors: List[str] = []
        
        request = kwargs.get("request")
        retrieval_pkg = kwargs.get("retrieval_pkg")
        correlation_payload = kwargs.get("correlation_payload")
        timeline_payload = kwargs.get("timeline_payload")
        graph_payload = kwargs.get("graph_payload")
        entity_payload = kwargs.get("entity_payload")
        
        try:
            if not isinstance(request, InvestigationRequest):
                # Fallback default request
                request = InvestigationRequest(
                    request_id="REQ-DEF-1",
                    case_id="CASE-DEF-1",
                    user_query="Who is the suspect?",
                    retrieval_id="RET-DEF-1",
                    mode=InvestigationMode.QUESTION_ANSWERING
                )
                
            if not retrieval_pkg:
                raise ValueError("Parameter 'retrieval_pkg' must be provided.")
                
            # Execute pipeline
            package, pipeline_warnings = self.pipeline.execute(
                request=request,
                retrieval_pkg=retrieval_pkg,
                correlation_payload=correlation_payload,
                timeline_payload=timeline_payload,
                graph_payload=graph_payload,
                entity_payload=entity_payload
            )
            payload = package.model_dump()
            warnings.extend(pipeline_warnings)
            
        except ReasoningError as e:
            status = "FAILURE"
            errors.append(e.message)
            logger.error(f"Domain reasoning execution failure [Code: {e.error_code}]: {e.message}", exc_info=True)
            
        except Exception as e:
            status = "FAILURE"
            errors.append(str(e))
            logger.critical(f"System panic inside InvestigationReasoningAgent: {e}", exc_info=True)
            
        finished_at = datetime.now(timezone.utc)
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        
        context.pipeline_stage = "investigation_reasoning"
        
        return AgentResultContract(
            agent="investigation_reasoning_agent",
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
            "agent": "Investigation Reasoning Agent",
            "status": "healthy",
            "version": __version__
        }

    def manifest(self) -> AgentManifest:
        """Exposes discovery manifest capability profile."""
        return self._MANIFEST
export_agent = InvestigationReasoningAgent
