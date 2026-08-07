# -*- coding: utf-8 -*-
"""Custom exceptions for the Timeline Intelligence Agent."""

from typing import Any, Dict, Optional

class TimelineException(Exception):
    """Base exception for all timeline intelligence steps."""
    def __init__(
        self,
        message: str,
        error_code: str = "TIMELINE_FAILED",
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}


class TimestampNormalizationError(TimelineException):
    """Raised when datetime values fail to parse/shift to UTC."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, "TIMESTAMP_NORMALIZATION_FAILED", details)


class DuplicateMergeError(TimelineException):
    """Raised when event merge logic crashes."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, "DUPLICATE_MERGE_FAILED", details)


class EventBuilderError(TimelineException):
    """Raised when candidate conversions fail."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, "EVENT_BUILDER_FAILED", details)


class TimelineValidationError(TimelineException):
    """Raised when validation constraints fail."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, "TIMELINE_VALIDATION_FAILED", details)


class RepositoryError(TimelineException):
    """Raised when repository storage fails."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, "REPOSITORY_FAILED", details)


class ChecksumMismatchError(TimelineException):
    """Raised when file integrity validation fails."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, "CHECKSUM_MISMATCH", details)

