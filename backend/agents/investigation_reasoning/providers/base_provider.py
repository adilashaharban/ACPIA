# -*- coding: utf-8 -*-
"""Reasoning provider base interface."""

from abc import ABC, abstractmethod
from typing import Tuple, Dict, Any

class ReasoningProvider(ABC):
    """Abstract interface for calling LLMs to extract json findings."""
    
    @abstractmethod
    def generate(
        self,
        prompt: str,
        temperature: float,
        max_tokens: int
    ) -> Tuple[str, Dict[str, Any]]:
        """Invokes active model endpoint.
        
        Args:
            prompt: Assembled context prompt.
            temperature: Randomness control.
            max_tokens: Sizing ceiling.
            
        Returns:
            Tuple of (raw string response, provider metadata dict).
        """
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """Verifies connection health status."""
        pass
export_base_provider = ReasoningProvider
