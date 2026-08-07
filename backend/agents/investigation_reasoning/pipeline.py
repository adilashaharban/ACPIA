# -*- coding: utf-8 -*-
"""Reasoning pipeline orchestration."""

import time
import uuid
from datetime import datetime, timezone
from typing import Tuple, List, Dict, Any, Optional
from backend.core.logger import get_logger
from backend.agents.base import AgentResultContract
from backend.agents.rag.schema import RetrievalPackage
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
from backend.agents.investigation_reasoning.validator import Validator
from backend.agents.investigation_reasoning.metrics import MetricsCalculator
from backend.agents.investigation_reasoning.cache.reasoning_cache import ReasoningCache
from backend.agents.investigation_reasoning.repositories.memory_repository import MemoryRepository
from backend.agents.investigation_reasoning.exceptions import ReasoningError
from backend.agents.investigation_reasoning.schema import (
    ReasoningPackage, InvestigationRequest, Finding, Contradiction, EvidenceGap,
    ReasoningTrace, ReasoningStep, ReasoningStatistics, ReasoningSummary, ProcessorExecution
)

logger = get_logger("agents.investigation_reasoning.pipeline")

class ReasoningPipeline:
    """Orchestrates structured LLM queries and evidence citation validator steps."""
    
    def __init__(
        self,
        prompt_builder: PromptBuilder,
        context_validator: ContextValidator,
        structured_parser: StructuredParser,
        finding_builder: FindingBuilder,
        citation_builder: CitationBuilder,
        citation_validator: CitationValidator,
        confidence_calculator: ConfidenceCalculator,
        contradiction_detector: ContradictionDetector,
        gap_detector: GapDetector,
        reasoning_engine: ReasoningEngine,
        validator: Validator,
        metrics_calculator: MetricsCalculator,
        cache: Optional[ReasoningCache] = None,
        repository: Optional[MemoryRepository] = None
    ) -> None:
        self.prompt_builder = prompt_builder
        self.context_validator = context_validator
        self.structured_parser = structured_parser
        self.finding_builder = finding_builder
        self.citation_builder = citation_builder
        self.citation_validator = citation_validator
        self.confidence_calculator = confidence_calculator
        self.contradiction_detector = contradiction_detector
        self.gap_detector = gap_detector
        self.reasoning_engine = reasoning_engine
        self.validator = validator
        self.metrics_calculator = metrics_calculator
        self.cache = cache or ReasoningCache()
        self.repository = repository or MemoryRepository()

    def execute(
        self,
        request: InvestigationRequest,
        retrieval_pkg: RetrievalPackage,
        correlation_payload: Optional[Dict[str, Any]] = None,
        timeline_payload: Optional[Dict[str, Any]] = None,
        graph_payload: Optional[Dict[str, Any]] = None,
        entity_payload: Optional[Dict[str, Any]] = None,
        provider_type: str = "gemini",
        model_name: str = "gemini-1.5-pro",
        temperature: float = 0.0,
        max_tokens: int = 2048
    ) -> Tuple[ReasoningPackage, List[str]]:
        """Runs the complete reasoning pipeline.
        
        Args:
            request: Action details parameters.
            retrieval_pkg: Base grounding RetrievalPackage context.
            ...
            
        Returns:
            Tuple containing (ReasoningPackage, warnings list).
        """
        start_time = time.perf_counter()
        warnings: List[str] = []
        executions_log: List[ProcessorExecution] = []
        
        logger.info("Investigation Reasoning pipeline started.")
        
        # 1. Cache Check
        cached = self.cache.lookup(request.retrieval_id, request.user_query)
        if cached:
            logger.info("Cache hit for user reasoning query.")
            return cached, warnings
            
        # 2. Context Validation
        self.context_validator.validate(retrieval_pkg)
        
        # 3. Prompt Builder
        t0 = time.perf_counter()
        prompt = self.prompt_builder.build_prompt(
            request=request,
            context_text=retrieval_pkg.context.context_text,
            entities_summary=str(entity_payload or ""),
            timeline_summary=str(timeline_payload or ""),
            graph_summary=str(graph_payload or ""),
            correlation_summary=str(correlation_payload or "")
        )
        prompt_time = (time.perf_counter() - t0) * 1000.0
        
        # 4. Invoke LLM Provider loops
        t0 = time.perf_counter()
        raw_data, provider_meta = self.reasoning_engine.execute_reasoning_loop(
            prompt=prompt,
            provider_type=provider_type,
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens
        )
        parsing_time = (time.perf_counter() - t0) * 1000.0
        executions_log.append(
            ProcessorExecution(
                processor_name="ReasoningEngine",
                processor_version="1.0.0",
                execution_time_ms=round(parsing_time, 2),
                status="SUCCESS"
            )
        )
        
        # 5. structured parser -> findings builder -> citations builder -> citation validator
        t0 = time.perf_counter()
        raw_findings, raw_contras, raw_gaps = self.structured_parser.parse_findings(raw_data)
        
        findings: List[Finding] = []
        execution_steps: List[ReasoningStep] = []
        
        for idx, rf in enumerate(raw_findings):
            f = self.finding_builder.build_finding(rf)
            
            # Map Citations
            raw_cits = rf.get("citations", [])
            citations = self.citation_builder.build_citations(raw_cits, retrieval_pkg)
            
            # Citation Validator Check
            self.citation_validator.validate_citations(citations, retrieval_pkg)
            f.citations = citations
            
            # Calculate explainable confidence metrics
            f.confidence = self.confidence_calculator.calculate_confidence(
                evidence_score=0.90,
                retrieval_score=retrieval_pkg.statistics.average_similarity,
                citation_score=0.95 if citations else 0.0,
                consistency_score=1.0,
                model_score=0.90
            )
            
            # Build execution step trace
            step = ReasoningStep(
                step_id=f"STP-{str(uuid.uuid4())[:8]}",
                step_type="FindingExtraction",
                description=f"Extracted and validated finding: '{f.title}'",
                input_references=f.supporting_evidence_ids,
                output_references=[f.finding_id],
                confidence=f.confidence.final_score
            )
            execution_steps.append(step)
            f.reasoning_steps.append(step)
            findings.append(f)
            
        # 6. Detect Contradictions
        contradictions = self.contradiction_detector.detect_contradictions(findings)
        
        # 7. Detect gaps
        gaps = self.gap_detector.detect_gaps(findings)
        
        # 8. Run final package validations
        validation_status = self.validator.validate_package(findings, contradictions)
        warnings.extend(validation_status.warnings)
        val_time = (time.perf_counter() - t0) * 1000.0
        
        stats = ReasoningStatistics(
            total_findings=len(findings),
            total_contradictions=len(contradictions),
            total_gaps=len(gaps)
        )
        
        avg_conf = sum(f.confidence.final_score for f in findings) / len(findings) if findings else 1.0
        
        summary = ReasoningSummary(
            average_confidence=round(avg_conf, 4),
            finding_types_distribution={}
        )
        
        # Timing Metrics
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        metrics = self.metrics_calculator.calculate(
            processing_time_ms=elapsed_ms,
            prompt_time_ms=prompt_time,
            parsing_time_ms=parsing_time,
            validation_time_ms=val_time,
            provider_metadata=provider_meta,
            executions=executions_log
        )
        
        package = ReasoningPackage(
            schema_version="1.0.0",
            reasoning_id=f"REAS-{str(uuid.uuid4())[:8]}",
            case_id=request.case_id,
            retrieval_id=request.retrieval_id,
            created_at=datetime.now(timezone.utc),
            prompt_version="v1",
            model_name=model_name,
            model_version="1.0.0",
            findings=findings,
            contradictions=contradictions,
            evidence_gaps=gaps,
            reasoning_trace=ReasoningTrace(
                trace_id=f"TRC-{str(uuid.uuid4())[:8]}",
                steps=execution_steps
            ),
            statistics=stats,
            validation=validation_status,
            metrics=metrics,
            summary=summary
        )
        
        # Save to cache and repository databases
        self.cache.save(request.retrieval_id, request.user_query, package)
        self.repository.save_reasoning(package)
        
        return package, warnings
export_pipeline = ReasoningPipeline
