# -*- coding: utf-8 -*-
"""Custom exceptions for the Investigation Reasoning Agent."""

from typing import Any, Dict, Optional

class ReasoningError(Exception):
    """Base exception for all investigation reasoning steps."""
    def __init__(
        self,
        message: str,
        error_code: str = "REASONING_FAILED",
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}


class PromptBuildError(ReasoningError):
    """Raised when context compilation fails."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, "PROMPT_BUILD_FAILED", details)


class ProviderError(ReasoningError):
    """Raised when the LLM provider API client fails."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, "PROVIDER_FAILED", details)


class ParsingError(ReasoningError):
    """Raised when JSON parsing fails."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, "PARSING_FAILED", details)


class CitationError(ReasoningError):
    """Raised when citation mappings do not exist in RAG context."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, "CITATION_FAILED", details)


class ValidationError(ReasoningError):
    """Raised when reasoning validation checks fail."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, "VALIDATION_FAILED", details)


class RepositoryError(ReasoningError):
    """Raised when database persistent storage operations fail."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, "REPOSITORY_FAILED", details)


class ChecksumMismatchError(ReasoningError):
    """Raised when file integrity validation fails."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, "CHECKSUM_MISMATCH", details)
