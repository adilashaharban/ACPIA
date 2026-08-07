# -*- coding: utf-8 -*-
"""Custom exceptions for the Document Intelligence Agent."""

from typing import Any, Dict, Optional

class DocumentParsingError(Exception):
    """Base exception for all document intelligence processes."""
    
    def __init__(
        self, 
        message: str, 
        error_code: str = "DOCUMENT_PARSING_FAILED", 
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Initializes the exception.
        
        Args:
            message: Error string.
            error_code: Error code.
            details: Context details.
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}


class ChecksumMismatchError(DocumentParsingError):
    """Raised when file integrity checksum differs."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, "CHECKSUM_MISMATCH", details)


class UnsupportedParserError(DocumentParsingError):
    """Raised when MIME type is not associated with any parser."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, "UNSUPPORTED_PARSER", details)


class OcrProcessingError(DocumentParsingError):
    """Raised when OCR execution engine fails."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, "OCR_PROCESSING_FAILED", details)


class ParserFailureError(DocumentParsingError):
    """Raised when parser crashes on corrupted files."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, "PARSER_FAILURE", details)
