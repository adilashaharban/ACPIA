# -*- coding: utf-8 -*-
"""Unit tests for DocumentNormalizer."""

from backend.agents.document_intelligence.normalizer import DocumentNormalizer
from backend.agents.document_intelligence.schema import ExtractedTextBlock, SourceReference, DocumentElementType

def test_normalize_whitespace_collapsing() -> None:
    """Verifies that consecutive tabs, newlines, and spaces collapse to a single space."""
    raw = "  Text \t line \n\n with spacing.  "
    clean = DocumentNormalizer.normalize_whitespace(raw)
    assert clean == "Text line with spacing."

def test_normalize_blocks() -> None:
    """Verifies that normalizer loops and collapses spaces inside block lists."""
    ref = SourceReference(
        evidence_id="EVID-1",
        file_path="mock.txt",
        page_number=1,
        parser="TXTParser",
        parser_version="1.0.0",
        source_element=DocumentElementType.PARAGRAPH
    )
    blocks = [
        ExtractedTextBlock(
            text="  Paragraph  \t text. ",
            reading_order_index=0,
            source_reference=ref
        )
    ]
    
    normalized = DocumentNormalizer.normalize_blocks(blocks)
    assert len(normalized) == 1
    assert normalized[0].text == "Paragraph text."
