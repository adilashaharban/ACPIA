# -*- coding: utf-8 -*-
"""Custom exceptions for the Entity Resolution Agent."""

from typing import Any, Dict, Optional

class ResolutionParsingError(Exception):
    """Base exception for all identity resolution steps."""
    def __init__(
        self,
        message: str,
        error_code: str = "RESOLUTION_FAILED",
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}


class ChecksumMismatchError(ResolutionParsingError):
    """Raised when file integrity validation fails."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, "CHECKSUM_MISMATCH", details)


class MatchingEngineError(ResolutionParsingError):
    """Raised when alignment engines fail to blocking check."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, "MATCHING_ENGINE_FAILED", details)
