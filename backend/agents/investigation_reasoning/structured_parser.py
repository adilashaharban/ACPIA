# -*- coding: utf-8 -*-
"""Structured response parser module."""

from typing import Dict, Any, List, Tuple
from backend.agents.investigation_reasoning.exceptions import ParsingError
from backend.agents.investigation_reasoning.schema import Finding, Contradiction, EvidenceGap

class StructuredParser:
    """Parses pre-validated dictionaries into structured outputs objects lists."""
    
    @staticmethod
    def parse_findings(data: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Parses output dict parts.
        
        Args:
            data: Validated json dict.
            
        Returns:
            Tuple of (raw_findings, raw_contradictions, raw_gaps).
        """
        try:
            raw_findings = data.get("findings", [])
            raw_contras = data.get("contradictions", [])
            raw_gaps = data.get("evidence_gaps", [])
            return raw_findings, raw_contras, raw_gaps
        except Exception as e:
            raise ParsingError(f"Failed to parse findings structure: {e}")
export_structured_parser = StructuredParser
