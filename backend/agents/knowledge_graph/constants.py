# -*- coding: utf-8 -*-
"""Constants for the Knowledge Graph Agent."""

from enum import Enum

class GraphState(str, Enum):
    """Lifecycle stages of the Knowledge Graph construction process."""
    STARTED = "STARTED"
    NODES_BUILT = "NODES_BUILT"
    EDGES_BUILT = "EDGES_BUILT"
    MERGED = "MERGED"
    VALIDATED = "VALIDATED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
