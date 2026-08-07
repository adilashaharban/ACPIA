# -*- coding: utf-8 -*-
"""Keyword processor module."""

from typing import List, Any
import numpy as np
from backend.schemas.common import SourceReference
from backend.agents.audio_intelligence.processors.base_processor import BaseProcessor
from backend.agents.audio_intelligence.schema import DetectedKeyword, KeywordMatchType, TranscriptSegment

class KeywordProcessor(BaseProcessor):
    """Spots specific high-priority keywords inside transcript sequences."""
    
    def __init__(self, target_keywords: List[str] = None) -> None:
        self.processor_name = "TextRegex_KeywordProcessor"
        self.version = "1.0.0"
        from backend.agents.audio_intelligence.constants import DEFAULT_KEYWORDS_LIST
        self.target_keywords = target_keywords or DEFAULT_KEYWORDS_LIST

    def process(self, audio_data: np.ndarray, context: SourceReference) -> List[Any]:
        # Returns empty when raw audio is fed without transcript text
        return []

    def detect_keywords(self, segments: List[TranscriptSegment]) -> List[DetectedKeyword]:
        """Matches targets against parsed transcript segments.
        
        Args:
            segments: Output segments from transcription.
            
        Returns:
            A list of DetectedKeyword schemas.
        """
        detections: List[DetectedKeyword] = []
        
        for segment in segments:
            text_lower = segment.text.lower()
            for kw in self.target_keywords:
                kw_lower = kw.lower()
                if kw_lower in text_lower:
                    # Find approximate timing from matched word if present
                    start_time = segment.start_time
                    end_time = segment.end_time
                    for word in segment.words:
                        if word.word.lower() == kw_lower:
                            start_time = word.start_time
                            end_time = word.end_time
                            break
                            
                    detections.append(
                        DetectedKeyword(
                            keyword=kw,
                            matched_text=kw,
                            match_type=KeywordMatchType.CASE_INSENSITIVE,
                            start_time=start_time,
                            end_time=end_time,
                            confidence=0.99,
                            segment_id=segment.segment_id
                        )
                    )
                    
        return detections
export_keyword_processor = KeywordProcessor
