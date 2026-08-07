# -*- coding: utf-8 -*-
"""Unit and integration tests for ReasoningPipeline."""

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
from backend.agents.investigation_reasoning.dispatcher import Dispatcher
from backend.agents.investigation_reasoning.validator import Validator
from backend.agents.investigation_reasoning.metrics import MetricsCalculator
from backend.agents.investigation_reasoning.repositories.sqlite_repository import SQLiteRepository
from backend.agents.investigation_reasoning.pipeline import ReasoningPipeline
from backend.agents.investigation_reasoning.schema import InvestigationRequest, ReasoningPackage

def test_pipeline_happy_path(
    metadata_result_contract: AgentResultContract,
    mock_retrieval_package: RetrievalPackage,
    mock_investigation_request: InvestigationRequest
) -> None:
    """Verifies that the complete reasoning pipeline executes and saves packages successfully."""
    pipeline = ReasoningPipeline(
        prompt_builder=PromptBuilder(),
        context_validator=ContextValidator(),
        structured_parser=StructuredParser(),
        finding_builder=FindingBuilder(),
        citation_builder=CitationBuilder(),
        citation_validator=CitationValidator(),
        confidence_calculator=ConfidenceCalculator(),
        contradiction_detector=ContradictionDetector(),
        gap_detector=GapDetector(),
        reasoning_engine=ReasoningEngine(Dispatcher()),
        validator=Validator(),
        metrics_calculator=MetricsCalculator(),
        repository=SQLiteRepository(":memory:")
    )
    
    package, warnings = pipeline.execute(
        request=mock_investigation_request,
        retrieval_pkg=mock_retrieval_package,
        metadata_result=metadata_result_contract
    )
    
    assert isinstance(package, ReasoningPackage)
    assert len(package.findings) > 0
    assert len(package.reasoning_trace.steps) > 0
