# -*- coding: utf-8 -*-
"""Constants for the Document Intelligence Agent."""

from enum import Enum

class DocumentState(str, Enum):
    """Lifecycle stages during document parsing and structural analysis."""
    STARTED = "STARTED"
    INTEGRITY_VERIFIED = "INTEGRITY_VERIFIED"
    PARSING = "PARSING"
    OCR_RUNNING = "OCR_RUNNING"
    NORMALIZING = "NORMALIZING"
    VALIDATING = "VALIDATING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


# MIME Type categorizations mapping to document parsers
DOCUMENT_MIME_GROUPS = {
    "pdf": ["application/pdf"],
    "docx": ["application/vnd.openxmlformats-officedocument.wordprocessingml.document"],
    "txt": ["text/plain"],
    "csv": ["text/csv"],
    "html": ["text/html"],
    "xml": ["text/xml", "application/xml"],
    "json": ["application/json"],
    "eml": ["message/rfc822", "application/octet-stream"], # fallback EML
}

# OCR trigger: if the embedded text extracted has less than this number of words per page
OCR_WORD_THRESHOLD_PER_PAGE = 5

DEFAULT_PRIORITIES = {
    "entity_resolution": 1,
    "timeline": 2,
    "knowledge_graph": 2,
}
