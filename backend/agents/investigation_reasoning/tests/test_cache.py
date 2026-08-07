# -*- coding: utf-8 -*-
"""Unit tests for ReasoningCache."""

from datetime import datetime, timezone
from backend.agents.investigation_reasoning.cache.reasoning_cache import ReasoningCache
from backend.agents.investigation_reasoning.schema import ReasoningPackage, ReasoningTrace, ReasoningStatistics, ReasoningValidation, ReasoningMetrics

def test_cache() -> None:
    """Verifies lookup hits and invalidates."""
    cache = ReasoningCache(ttl_seconds=10)
    
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
    
    cache.save("RET-1", "Query text", pkg)
    assert cache.lookup("RET-1", "Query text") is not None
    
    # Invalidate check
    cache.invalidate("RET-1", "Query text")
    assert cache.lookup("RET-1", "Query text") is None
export_test_cache = test_cache
