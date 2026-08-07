# -*- coding: utf-8 -*-
"""Document parsers package namespace."""

from backend.agents.document_intelligence.parsers.base_parser import BaseParser
from backend.agents.document_intelligence.parsers.pdf_parser import PDFParser
from backend.agents.document_intelligence.parsers.docx_parser import DOCXParser
from backend.agents.document_intelligence.parsers.txt_parser import TXTParser
from backend.agents.document_intelligence.parsers.csv_parser import CSVParser
from backend.agents.document_intelligence.parsers.html_parser import HTMLParser
from backend.agents.document_intelligence.parsers.json_parser import JSONParser
from backend.agents.document_intelligence.parsers.xml_parser import XMLParser
from backend.agents.document_intelligence.parsers.eml_parser import EMLParser
from backend.agents.document_intelligence.parsers.whatsapp_parser import WhatsAppParser

__all__ = [
    "BaseParser",
    "PDFParser",
    "DOCXParser",
    "TXTParser",
    "CSVParser",
    "HTMLParser",
    "JSONParser",
    "XMLParser",
    "EMLParser",
    "WhatsAppParser",
]
