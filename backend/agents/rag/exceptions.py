# -*- coding: utf-8 -*-
"""Custom exceptions for the RAG Agent."""

from typing import Any, Dict, Optional

class RAGError(Exception):
    """Base exception for all RAG intelligence steps."""
    def __init__(
        self,
        message: str,
        error_code: str = "RAG_FAILED",
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}


class RepositoryError(RAGError):
    """Raised when repository storage or index builder fails."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, "REPOSITORY_FAILED", details)


class ExtractorError(RAGError):
    """Raised when parsing or candidate gathering crashes."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, "EXTRACTOR_FAILED", details)


class ValidationError(RAGError):
    """Raised when validation constraints fail."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, "VALIDATION_FAILED", details)


class PipelineError(RAGError):
    """Raised when the orchestrator pipeline crashes."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, "PIPELINE_FAILED", details)


class ProviderError(RAGError):
    """Raised when embedding model provider fails."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, "PROVIDER_FAILED", details)


class ChecksumMismatchError(RAGError):
    """Raised when file integrity validation fails."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, "CHECKSUM_MISMATCH", details)
