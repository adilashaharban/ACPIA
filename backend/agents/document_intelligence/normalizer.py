# -*- coding: utf-8 -*-
"""Document text normalizer."""

import re
from typing import List
from backend.agents.document_intelligence.schema import ExtractedTextBlock

class DocumentNormalizer:
    """Standardizes string characters and normalizes paragraph alignments."""
    
    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """Standardizes character spacings and strips surrounding empty elements.
        
        Args:
            text: Raw string.
            
        Returns:
            Normalized string.
        """
        if not text:
            return ""
        # Collapse multiple spaces and line endings
        text_clean = re.sub(r"\s+", " ", text)
        return text_clean.strip()

    @classmethod
    def normalize_blocks(cls, blocks: List[ExtractedTextBlock]) -> List[ExtractedTextBlock]:
        """Normalizes spacing and updates paragraph alignments in a list of text blocks.
        
        Args:
            blocks: List of text blocks.
            
        Returns:
            A list of new normalized ExtractedTextBlock objects.
        """
        normalized_list = []
        for block in blocks:
            clean_text = cls.normalize_whitespace(block.text)
            
            # Copy with normalized values
            normalized_list.append(
                ExtractedTextBlock(
                    text=clean_text,
                    reading_order_index=block.reading_order_index,
                    text_confidence=block.text_confidence,
                    layout_confidence=block.layout_confidence,
                    source_reference=block.source_reference
                )
            )
        return normalized_list
