# -*- coding: utf-8 -*-
"""Constants for the Entity Resolution Agent."""

from enum import Enum

class ResolutionState(str, Enum):
    """Lifecycle stages of the entity resolution process."""
    STARTED = "STARTED"
    EXTRACTED = "EXTRACTED"
    NORMALIZED = "NORMALIZED"
    MATCHED = "MATCHED"
    MERGED = "MERGED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


# Fuzzy logic thresholds
FUZZY_JARO_WINKLER_THRESHOLD = 0.88
FUZZY_LEVENSHTEIN_MAX_DISTANCE = 2
FUZZY_TOKEN_SET_RATIO_THRESHOLD = 85

# Confidence parameters
BASE_CONFIDENCE_WEIGHT = 0.70
MULTIPLE_EVIDENCE_BOOST = 0.05
MAX_BOOST_VALUE = 0.99
