# -*- coding: utf-8 -*-
"""Custom exceptions for the Vision Intelligence Agent."""

from typing import Any, Dict, Optional

class VisionParsingError(Exception):
    """Base exception for all visual scanning steps."""
    def __init__(
        self,
        message: str,
        error_code: str = "VISION_PARSING_FAILED",
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}


class ChecksumMismatchError(VisionParsingError):
    """Raised when file integrity validation fails."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, "CHECKSUM_MISMATCH", details)


class UnsupportedFormatError(VisionParsingError):
    """Raised when visual file MIME is unsupported."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, "UNSUPPORTED_FORMAT", details)


class DetectorLoadError(VisionParsingError):
    """Raised when object detection model files fail to load."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, "DETECTOR_LOAD_FAILED", details)
