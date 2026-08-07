# -*- coding: utf-8 -*-
"""Custom exceptions for the Metadata Agent."""

from typing import Any, Dict, Optional

class MetadataExtractionError(Exception):
    """Base exception for all metadata extraction errors."""
    
    def __init__(
        self, 
        message: str, 
        error_code: str = "METADATA_EXTRACTION_FAILED", 
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Initializes the exception with error code, message, and details.
        
        Args:
            message: Explanation message.
            error_code: Code for machine processing.
            details: Serializable data context.
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}


class ChecksumMismatchError(MetadataExtractionError):
    """Raised when file integrity validation fails against ingestion hash."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, "CHECKSUM_MISMATCH", details)


class UnsupportedMetadataError(MetadataExtractionError):
    """Raised when parsing is requested on unsupported file signatures."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, "UNSUPPORTED_METADATA", details)


class MetadataValidationError(MetadataExtractionError):
    """Raised when coordinates or structural properties violate boundaries."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, "METADATA_VALIDATION_FAILED", details)


class ParserFailureError(MetadataExtractionError):
    """Raised when a specific extractor parser fails."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, "PARSER_FAILURE", details)
