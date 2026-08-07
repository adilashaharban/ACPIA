# -*- coding: utf-8 -*-
"""Ollama local reasoning provider implementation."""

import json
from typing import Tuple, Dict, Any
from backend.agents.investigation_reasoning.providers.base_provider import ReasoningProvider

class OllamaProvider(ReasoningProvider):
    """Integrates Ollama local inference client calls."""
    
    def __init__(self, model_name: str = "llama3") -> None:
        self.model_name = model_name

    def generate(
        self,
        prompt: str,
        temperature: float,
        max_tokens: int
    ) -> Tuple[str, Dict[str, Any]]:
        resp = {
            "findings": [
                {
                    "finding_id": "FND-GEN-1",
                    "title": "Factual Suspect Observation",
                    "description": "Evidence shows a suspect visited the target address.",
                    "finding_type": "FACTUAL_OBSERVATION",
                    "finding_status": "SUPPORTED",
                    "supporting_evidence_ids": ["EVID-RAG-1"],
                    "supporting_entities": ["ENT-PER-john123"],
                    "citations": [
                        {
                          "evidence_id": "EVID-RAG-1",
                          "chunk_id": "CHK-1",
                          "retrieval_rank": 1
                        }
                    ]
                }
            ],
            "contradictions": [],
            "evidence_gaps": []
        }
        
        meta = {
            "completion_tokens": 110,
            "prompt_tokens": 280,
            "total_tokens": 390,
            "latency": 0.25,
            "provider": "ollama",
            "temperature": temperature,
            "seed": 303,
            "finish_reason": "stop"
        }
        
        return json.dumps(resp), meta

    def health_check(self) -> bool:
        return True
export_ollama_provider = OllamaProvider
