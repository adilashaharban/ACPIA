# -*- coding: utf-8 -*-
"""Validation engine for uploaded evidence files."""

import mimetypes
import re
from pathlib import Path
from typing import Tuple
from backend.core.config import settings
from backend.agents.evidence_intake.exceptions import (
    InvalidFileError,
    OversizedFileError,
    UnsupportedMimeTypeError,
)

# Optional magic import fallback
try:
    import magic
except ImportError:
    magic = None  # type: ignore


class EvidenceValidator:
    """Validates file properties including size, filename safety, and signature MIME type."""
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitizes filename to prevent directory traversal and clean special characters.
        
        Args:
            filename: Original raw string.
            
        Returns:
            Sanitized name string.
            
        Raises:
            InvalidFileError: If path traversal attempt is detected.
        """
        if not filename:
            raise InvalidFileError("Filename is empty.")
            
        # Check for path traversal elements
        if ".." in filename or "/" in filename or "\\" in filename:
            raise InvalidFileError(f"Directory traversal detected in filename: {filename}")
            
        # Extract name and extension
        path = Path(filename)
        stem = path.stem
        suffix = path.suffix.lower()
        
        # Keep alphanumeric, dashes, and underscores
        clean_stem = re.sub(r"[^a-zA-Z0-9_\-]", "_", stem)
        if not clean_stem:
            clean_stem = "evidence_file"
            
        return f"{clean_stem}{suffix}"

    @classmethod
    def validate(cls, file_bytes: bytes, filename: str) -> Tuple[str, str]:
        """Validates the uploaded file.
        
        Args:
            file_bytes: Raw binary content.
            filename: Original user filename.
            
        Returns:
            Tuple containing (sanitized_filename, detected_mime_type).
            
        Raises:
            InvalidFileError: For empty files.
            OversizedFileError: If exceeding size limit.
            UnsupportedMimeTypeError: If MIME type isn't allowed.
        """
        # 1. Empty check
        if not file_bytes or len(file_bytes) == 0:
            raise InvalidFileError("Uploaded file is empty.")
            
        # 2. Size validation
        size_bytes = len(file_bytes)
        if size_bytes > settings.MAX_FILE_SIZE_BYTES:
            raise OversizedFileError(
                f"File size {size_bytes} exceeds limit of {settings.MAX_FILE_SIZE_BYTES} bytes."
            )
            
        # 3. Filename sanitation
        sanitized_name = cls.sanitize_filename(filename)
        
        # 4. MIME type signature check
        detected_mime = None
        if magic is not None:
            try:
                # Read signature from buffer
                detected_mime = magic.from_buffer(file_bytes, mime=True)
            except Exception:
                pass
                
        # Fallback to extension check if magic fails or is unavailable
        if not detected_mime:
            detected_mime, _ = mimetypes.guess_type(sanitized_name)
            
        if not detected_mime:
            detected_mime = "application/octet-stream"
            
        # Normalize common zip variant MIME types
        if detected_mime == "application/x-zip":
            detected_mime = "application/zip"
            
        # Verify against allowed configuration list
        if detected_mime not in settings.ALLOWED_MIME_TYPES:
            raise UnsupportedMimeTypeError(
                f"MIME type '{detected_mime}' is not supported. Allowed: {settings.ALLOWED_MIME_TYPES}"
            )
            
        return sanitized_name, detected_mime
