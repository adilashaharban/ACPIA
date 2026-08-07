# -*- coding: utf-8 -*-
"""Reasoning engine module."""

import time
from typing import Tuple, Dict, Any, List
from backend.agents.investigation_reasoning.dispatcher import Dispatcher
from backend.agents.investigation_reasoning.output_validator import OutputValidator
from backend.agents.investigation_reasoning.structured_parser import StructuredParser
from backend.agents.investigation_reasoning.exceptions import ReasoningError
from backend.agents.investigation_reasoning.schema import ProviderResponseMetadata

class ReasoningEngine:
    """Manages prompt calls and structured decoding retries."""
    
    def __init__(self, dispatcher: Dispatcher) -> None:
        self.dispatcher = dispatcher

    def execute_reasoning_loop(
        self,
        prompt: str,
        provider_type: str,
        model_name: str,
        temperature: float,
        max_tokens: int,
        retry_limit: int = 2
    ) -> Tuple[Dict[str, Any], ProviderResponseMetadata]:
        """Calls dispatcher and retries parsing failures.
        
        Args:
            prompt: Text prompt string.
            provider_type: Provider selection ID.
            model_name: Specific model tag.
            temperature: Randomness.
            max_tokens: Size limit.
            retry_limit: Retries budget count.
            
        Returns:
            Tuple of (parsed dictionary, ProviderResponseMetadata).
        """
        attempts = 0
        last_error = None
        
        while attempts < retry_limit:
            attempts += 1
            try:
                raw_txt, raw_meta = self.dispatcher.call_provider(
                    provider_type=provider_type,
                    model_name=model_name,
                    prompt=prompt,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                
                # output validator checks
                data = OutputValidator.validate_raw_json(raw_txt)
                
                # Decode metadata
                meta = ProviderResponseMetadata(
                    completion_tokens=raw_meta.get("completion_tokens", 0),
                    prompt_tokens=raw_meta.get("prompt_tokens", 0),
                    total_tokens=raw_meta.get("total_tokens", 0),
                    latency=raw_meta.get("latency", 0.0),
                    provider=raw_meta.get("provider", provider_type),
                    temperature=raw_meta.get("temperature", temperature),
                    seed=raw_meta.get("seed", 0),
                    finish_reason=raw_meta.get("finish_reason", "stop")
                )
                return data, meta
                
            except Exception as e:
                last_error = e
                # Pause brief delay before retry
                time.sleep(0.1)
                
        raise ReasoningError(f"Reasoning loop failed after {retry_limit} attempts. Last error: {last_error}")
export_reasoning_engine = ReasoningEngine
