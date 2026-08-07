# -*- coding: utf-8 -*-
"""Constants for the Evidence Intake Agent."""

from enum import Enum

# Ingestion Pipeline Lifecycle States
class IntakeState(str, Enum):
    """Execution state within the Evidence Intake pipeline."""
    RECEIVED = "RECEIVED"
    VALIDATED = "VALIDATED"
    HASHED = "HASHED"
    STORED = "STORED"
    REGISTERED = "REGISTERED"
    READY = "READY"
    FAILED = "FAILED"


# MIME Type groups for routing and validation classification
MIME_GROUPS = {
    "image": ["image/jpeg", "image/png", "image/gif", "image/webp"],
    "pdf": ["application/pdf"],
    "text": ["text/plain", "application/json"],
    "audio": ["audio/mpeg", "audio/wav", "audio/ogg", "audio/x-wav"],
    "video": ["video/mp4", "video/mpeg", "video/quicktime", "video/x-msvideo"],
    "archive": ["application/zip", "application/x-zip-compressed"],
}

# Downstream routing prioritization
DEFAULT_PRIORITIES = {
    "metadata": 1,
    "vision": 2,
    "document": 2,
    "audio": 2,
}
