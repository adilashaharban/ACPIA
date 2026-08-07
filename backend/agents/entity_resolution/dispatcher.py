# -*- coding: utf-8 -*-
"""Entity Resolution dispatcher."""

class EntityDispatcher:
    """Manages custom matching logic dispatch mappings."""
    def __init__(self) -> None:
        self.registered_extractors = ["metadata", "document", "vision", "audio"]
