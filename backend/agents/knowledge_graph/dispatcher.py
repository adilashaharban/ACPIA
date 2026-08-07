# -*- coding: utf-8 -*-
"""Knowledge Graph dispatcher."""

class GraphDispatcher:
    """Manages custom builder routing dispatch mappings."""
    def __init__(self) -> None:
        self.builders = ["node_builder", "edge_builder"]
