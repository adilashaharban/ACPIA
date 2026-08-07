# -*- coding: utf-8 -*-
"""Query expander module."""

class QueryExpander:
    """Optional expander that rewrites target lexical search terms."""
    
    def __init__(self, enabled: bool = False) -> None:
        self.enabled = enabled

    def expand(self, query: str) -> str:
        """Rewrites queries.
        
        Args:
            query: Original search string.
            
        Returns:
            Rewritten or original query.
        """
        if not self.enabled:
            return query
            
        # Simple deterministic expansion
        return f"{query} OR synonym"
export_query_expander = QueryExpander
