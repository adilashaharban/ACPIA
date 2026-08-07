# -*- coding: utf-8 -*-
"""Investigation Prompt Builder module."""

import os
from typing import Dict, Any
from backend.agents.investigation_reasoning.schema import InvestigationRequest

class PromptBuilder:
    """Assembles templated texts for LLM reasoning ingestion."""
    
    def __init__(self) -> None:
        self.dir_path = os.path.dirname(os.path.abspath(__file__))
        self.prompts_dir = os.path.join(self.dir_path, "prompts")

    def _read_prompt(self, filename: str) -> str:
        p = os.path.join(self.prompts_dir, filename)
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                return f.read()
        return ""

    def build_prompt(
        self,
        request: InvestigationRequest,
        context_text: str,
        entities_summary: str = "",
        timeline_summary: str = "",
        graph_summary: str = "",
        correlation_summary: str = ""
    ) -> str:
        """Assembles prompt parts.
        
        Returns:
            Formatted final prompt string.
        """
        sys_p = self._read_prompt("system_prompt_v1.txt")
        schema_p = self._read_prompt("output_schema_prompt_v1.txt")
        invest_p = self._read_prompt("investigation_prompt_v1.txt")
        
        formatted_invest = invest_p.format(
            query=request.user_query,
            context=context_text,
            entities=entities_summary,
            timeline=timeline_summary,
            graph=graph_summary,
            correlation=correlation_summary
        )
        
        return f"{sys_p}\n\n{schema_p}\n\n{formatted_invest}"
export_prompt_builder = PromptBuilder
