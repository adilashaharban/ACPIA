# -*- coding: utf-8 -*-
"""Custom exceptions raised within the Evidence Intake agent."""

from typing import Dict, Any, Optional

class EvidenceIntakeError(Exception):
    """Base exception for all Evidence Intake processes."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Initializes the exception with a message and structured details.
        
        Args:
            message: Plain-text explanation.
            details: Serializable key-value data context.
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}


class InvalidFileError(EvidenceIntakeError):
    """Raised when file validation (empty, path traversal, corrupt signatures) fails."""
    pass


class UnsupportedMimeTypeError(EvidenceIntakeError):
    """Raised when the detected file type is not on the allowed list."""
    pass


class OversizedFileError(EvidenceIntakeError):
    """Raised when a file exceeds size limit constraints."""
    pass


class HashingError(EvidenceIntakeError):
    """Raised when SHA-256 generation fails."""
    pass


class StorageFailureError(EvidenceIntakeError):
    """Raised when saving the file to disk or object store fails."""
    pass


class DuplicateEvidenceError(EvidenceIntakeError):
    """Raised when evidence with the same hash already exists."""
    pass


class DatabaseTransactionError(EvidenceIntakeError):
    """Raised when database registry commits fail."""
    pass
