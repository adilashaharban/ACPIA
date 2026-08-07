# -*- coding: utf-8 -*-
"""Custom exceptions for the Knowledge Graph Agent."""

from typing import Any, Dict, Optional

class GraphParsingError(Exception):
    """Base exception for all graph conversion steps."""
    def __init__(
        self,
        message: str,
        error_code: str = "GRAPH_FAILED",
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}


class ChecksumMismatchError(GraphParsingError):
    """Raised when file integrity validation fails."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, "CHECKSUM_MISMATCH", details)


class GraphBuilderError(GraphParsingError):
    """Raised when nodes or edges builder crashes."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, "GRAPH_BUILDER_FAILED", details)
