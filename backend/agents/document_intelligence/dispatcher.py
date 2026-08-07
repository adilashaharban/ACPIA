# -*- coding: utf-8 -*-
"""Document parser dispatcher."""

from typing import Dict, Type, Any, Optional
from backend.agents.document_intelligence.exceptions import UnsupportedParserError
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
from backend.agents.document_intelligence.constants import DOCUMENT_MIME_GROUPS

class DocumentDispatcher:
    """Dispatches document MIME types to specific parser implementation engines."""
    
    def __init__(self, custom_parsers: Optional[Dict[str, Type[BaseParser]]] = None) -> None:
        """Initializes mapping entries."""
        self._parser_map: Dict[str, Type[BaseParser]] = {
            "pdf": PDFParser,
            "docx": DOCXParser,
            "txt": TXTParser,
            "csv": CSVParser,
            "html": HTMLParser,
            "json": JSONParser,
            "xml": XMLParser,
            "eml": EMLParser,
        }
        if custom_parsers:
            self._parser_map.update(custom_parsers)

    def select_parser(self, mime_type: str, filename: Optional[str] = None) -> Type[BaseParser]:
        """Resolves the correct parser class.
        
        Args:
            mime_type: File signature MIME category.
            filename: String name of file.
            
        Returns:
            The resolved parser class type inheriting BaseParser.
            
        Raises:
            UnsupportedParserError: For unmappable formats.
        """
        if not mime_type:
            raise UnsupportedParserError("MIME type string is empty.")
            
        normalized_mime = mime_type.lower().strip()
        
        # Check WhatsApp override (chat exports are typically text/plain, but named like chat log)
        if filename and ("whatsapp" in filename.lower() or "chat" in filename.lower()):
            if normalized_mime in DOCUMENT_MIME_GROUPS["txt"]:
                return WhatsAppParser
                
        # Resolve standard MIME groups
        for category, mimes in DOCUMENT_MIME_GROUPS.items():
            if normalized_mime in mimes:
                parser_cls = self._parser_map.get(category)
                if parser_cls:
                    return parser_cls
                    
        # Check fallbacks for plain/text variations
        if normalized_mime.startswith("text/"):
            return TXTParser
            
        raise UnsupportedParserError(f"No document parser registered for MIME type: {mime_type}")
