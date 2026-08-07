# -*- coding: utf-8 -*-
"""Base document parser interface."""

from abc import ABC, abstractmethod
from typing import Tuple, List, Dict, Any
from backend.agents.document_intelligence.schema import Page, Table, FormField, ExtractedTextBlock

class BaseParser(ABC):
    """Abstract Base Class specifying common file parsing method interfaces."""
    
    @abstractmethod
    def parse(
        self, 
        file_path: str, 
        evidence_id: str
    ) -> Tuple[List[Page], List[Table], List[FormField], List[ExtractedTextBlock]]:
        """Parses the document at file_path.
        
        Args:
            file_path: Absolute string path.
            evidence_id: Evidentiary parent tracking ID.
            
        Returns:
            Tuple containing:
            - List of Page objects
            - List of Table objects
            - List of FormField objects
            - List of ExtractedTextBlock objects
            
        Raises:
            ParserFailureError: For format processing errors.
        """
        pass
