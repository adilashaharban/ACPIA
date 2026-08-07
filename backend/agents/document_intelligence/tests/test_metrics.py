# -*- coding: utf-8 -*-
"""Unit tests for DocumentMetricsCalculator."""

from backend.agents.document_intelligence.metrics import DocumentMetricsCalculator
from backend.agents.document_intelligence.schema import Page

def test_metrics_calculator() -> None:
    """Verifies that stats computes correct word, character, and page counts."""
    # Text content has 4 words, 23 characters
    page = Page(
        page_number=1,
        text_content="The quick brown fox jumps over the lazy dog. This is a standard English document text string representing investigation evidence file.",
        paragraphs=[],
        tables=[],
        forms=[]
    )
    
    stats, metrics, lang, summary = DocumentMetricsCalculator.calculate(
        mime_type="text/plain",
        parser_name="TXTParser",
        pages=[page],
        tables=[],
        forms=[],
        ocr_triggered=False,
        ocr_page_count=0,
        processing_time_ms=5.0
    )
    
    assert stats.page_count == 1
    assert stats.word_count == 21
    assert stats.char_count == 134
    assert lang.primary_language == "en"
    assert summary.parser_name == "TXTParser"
