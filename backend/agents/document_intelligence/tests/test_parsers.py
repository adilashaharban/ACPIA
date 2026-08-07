# -*- coding: utf-8 -*-
"""Unit tests for Document Parsers."""

import pytest
from pathlib import Path
from backend.agents.document_intelligence.parsers.txt_parser import TXTParser
from backend.agents.document_intelligence.parsers.csv_parser import CSVParser
from backend.agents.document_intelligence.parsers.json_parser import JSONParser
from backend.agents.document_intelligence.parsers.xml_parser import XMLParser
from backend.agents.document_intelligence.parsers.html_parser import HTMLParser
from backend.agents.document_intelligence.parsers.eml_parser import EMLParser
from backend.agents.document_intelligence.parsers.whatsapp_parser import WhatsAppParser

def test_txt_parser(mock_txt: Path) -> None:
    """Verifies text parsing outputs correct Page and paragraph structures."""
    parser = TXTParser()
    pages, tables, forms, blocks = parser.parse(str(mock_txt.resolve()), "EVID-1")
    assert len(pages) == 1
    assert len(blocks) == 2
    assert blocks[0].text == "Line 1 text content."

def test_csv_parser(mock_csv: Path) -> None:
    """Verifies CSV parsing outputs rows as tables."""
    parser = CSVParser()
    pages, tables, forms, blocks = parser.parse(str(mock_csv.resolve()), "EVID-1")
    assert len(tables) == 1
    assert tables[0].rows_count == 3
    assert tables[0].cols_count == 3

def test_json_parser(mock_json: Path) -> None:
    """Verifies JSON parsing flattens keys to paragraph blocks."""
    parser = JSONParser()
    pages, tables, forms, blocks = parser.parse(str(mock_json.resolve()), "EVID-1")
    assert len(blocks) == 2
    assert "case_id: CASE-9" in [b.text for b in blocks]

def test_xml_parser(mock_xml: Path) -> None:
    """Verifies XML parsing flattens elements recursively."""
    parser = XMLParser()
    pages, tables, forms, blocks = parser.parse(str(mock_xml.resolve()), "EVID-1")
    assert len(blocks) == 2  # attr + text element
    assert "root/entry: Message text log." in [b.text for b in blocks]

def test_html_parser(mock_html: Path) -> None:
    """Verifies HTML parsing extracts headings and text values."""
    parser = HTMLParser()
    pages, tables, forms, blocks = parser.parse(str(mock_html.resolve()), "EVID-1")
    assert len(blocks) == 2
    assert blocks[0].text == "Header Title"

def test_eml_parser(mock_eml: Path) -> None:
    """Verifies EML parser reads headers and body text."""
    parser = EMLParser()
    pages, tables, forms, blocks = parser.parse(str(mock_eml.resolve()), "EVID-1")
    texts = [b.text for b in blocks]
    assert "Subject: Case files" in texts
    assert "Email body text content block." in texts

def test_whatsapp_parser(mock_whatsapp: Path) -> None:
    """Verifies WhatsApp parser segments chat line authors and datetimes."""
    parser = WhatsAppParser()
    pages, tables, forms, blocks = parser.parse(str(mock_whatsapp.resolve()), "EVID-1")
    assert len(blocks) == 2
    assert "Officer: Suspect message." in blocks[0].text
    assert "Suspect: Understood." in blocks[1].text
