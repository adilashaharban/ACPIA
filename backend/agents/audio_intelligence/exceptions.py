# -*- coding: utf-8 -*-
"""Custom exceptions for the Audio Intelligence Agent."""

from typing import Any, Dict, Optional

class AudioParsingError(Exception):
    """Base exception for all acoustic scanning steps."""
    def __init__(
        self,
        message: str,
        error_code: str = "AUDIO_PARSING_FAILED",
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}


class ChecksumMismatchError(AudioParsingError):
    """Raised when file integrity validation fails."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, "CHECKSUM_MISMATCH", details)


class UnsupportedCodecError(AudioParsingError):
    """Raised when audio MIME codec is unsupported."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, "UNSUPPORTED_CODEC", details)


class ProcessorLoadError(AudioParsingError):
    """Raised when signal processing models fail to load."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, "PROCESSOR_LOAD_FAILED", details)
