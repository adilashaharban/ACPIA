# -*- coding: utf-8 -*-
"""Constants for the Timeline Intelligence Agent."""

from enum import Enum

class TimelineState(str, Enum):
    """Lifecycle stages of the Timeline compilation process."""
    STARTED = "STARTED"
    EXTRACTED = "EXTRACTED"
    NORMALIZED = "NORMALIZED"
    DEDUPLICATED = "DEDUPLICATED"
    MERGED = "MERGED"
    SORTED = "SORTED"
    VALIDATED = "VALIDATED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


# Proximity merge limit (in seconds)
DUPLICATE_PROXIMITY_SECONDS = 1.0
DEFAULT_TIMEZONE = "UTC"
