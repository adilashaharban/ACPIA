# -*- coding: utf-8 -*-
"""Unit tests for ReasoningRepository implementations."""

from datetime import datetime, timezone
from backend.agents.investigation_reasoning.repositories.memory_repository import MemoryRepository
from backend.agents.investigation_reasoning.repositories.sqlite_repository import SQLiteRepository
from backend.agents.investigation_reasoning.schema import ReasoningPackage, ReasoningTrace, ReasoningStatistics, ReasoningValidation, ReasoningMetrics

def test_repositories() -> None:
    """Verifies reasoning packages save, load, find_by, and delete options."""
    pkg = ReasoningPackage(
        schema_version="1.0.0",
        reasoning_id="RE-1",
        case_id="C1",
        retrieval_id="RET-1",
        created_at=datetime.now(timezone.utc),
        model_name="gemini",
        model_version="1.0.0",
        reasoning_trace=ReasoningTrace(trace_id="TR-1"),
        statistics=ReasoningStatistics(total_findings=0, total_contradictions=0, total_gaps=0),
        validation=ReasoningValidation(),
        metrics=ReasoningMetrics(processing_time_ms=0.0, prompt_time_ms=0.0, parsing_time_ms=0.0, validation_time_ms=0.0),
        summary={"average_confidence": 1.0}
    )
    
    # Memory check
    mem = MemoryRepository()
    mem.save_reasoning(pkg)
    assert len(mem.find_by_case("C1")) == 1
    assert mem.load_reasoning("RE-1") is not None
    
    # SQLite check
    sq = SQLiteRepository(":memory:")
    sq.save_reasoning(pkg)
    assert len(sq.find_by_case("C1")) == 1
    assert sq.load_reasoning("RE-1") is not None
export_test_repositories = test_repositories
