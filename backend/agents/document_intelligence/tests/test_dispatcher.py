# -*- coding: utf-8 -*-
"""Unit tests for the DocumentDispatcher."""

import pytest
from backend.agents.document_intelligence.dispatcher import DocumentDispatcher
from backend.agents.document_intelligence.parsers.pdf_parser import PDFParser
from backend.agents.document_intelligence.parsers.txt_parser import TXTParser
from backend.agents.document_intelligence.parsers.whatsapp_parser import WhatsAppParser
from backend.agents.document_intelligence.exceptions import UnsupportedParserError

def test_dispatcher_select_pdf() -> None:
    """Verifies application/pdf maps to PDFParser."""
    dispatcher = DocumentDispatcher()
    parser_cls = dispatcher.select_parser("application/pdf")
    assert parser_cls is PDFParser

def test_dispatcher_select_txt() -> None:
    """Verifies text/plain maps to TXTParser."""
    dispatcher = DocumentDispatcher()
    parser_cls = dispatcher.select_parser("text/plain")
    assert parser_cls is TXTParser

def test_dispatcher_whatsapp_export() -> None:
    """Verifies text/plain logs with whatsapp filename override maps to WhatsAppParser."""
    dispatcher = DocumentDispatcher()
    parser_cls = dispatcher.select_parser("text/plain", filename="whatsapp_chat.txt")
    assert parser_cls is WhatsAppParser

def test_dispatcher_unsupported_mime() -> None:
    """Verifies that unmappable formats raise UnsupportedParserError."""
    dispatcher = DocumentDispatcher()
    with pytest.raises(UnsupportedParserError):
        dispatcher.select_parser("image/png")
