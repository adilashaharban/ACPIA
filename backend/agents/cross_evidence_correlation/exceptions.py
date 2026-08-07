# -*- coding: utf-8 -*-
"""Custom exceptions for the Cross-Evidence Correlation Agent."""

from typing import Any, Dict, Optional

class CorrelationError(Exception):
    """Base exception for all cross-evidence correlation steps."""
    def __init__(
        self,
        message: str,
        error_code: str = "CORRELATION_FAILED",
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}


class RepositoryError(CorrelationError):
    """Raised when repository storage fails."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, "REPOSITORY_FAILED", details)


class ExtractorError(CorrelationError):
    """Raised when parsing or candidate gathering crashes."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, "EXTRACTOR_FAILED", details)


class MatchingError(CorrelationError):
    """Raised when similarity or comparison processes fail."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, "MATCHING_FAILED", details)


class ValidationError(CorrelationError):
    """Raised when validation constraints fail."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, "VALIDATION_FAILED", details)


class PipelineError(CorrelationError):
    """Raised when the orchestrator pipeline crashes."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, "PIPELINE_FAILED", details)


class ChecksumMismatchError(CorrelationError):
    """Raised when file integrity validation fails."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, "CHECKSUM_MISMATCH", details)
