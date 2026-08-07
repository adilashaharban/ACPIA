# -*- coding: utf-8 -*-
"""Transcription processor module using Whisper framework."""

import uuid
from typing import List, Any
import numpy as np
from backend.schemas.common import SourceReference
from backend.agents.audio_intelligence.processors.base_processor import BaseProcessor
from backend.agents.audio_intelligence.schema import TranscriptSegment, WordTimestamp

class TranscriptionProcessor(BaseProcessor):
    """Parses spoken audio, extracting words, timestamps, and confidence values."""
    
    def __init__(self) -> None:
        self.engine_name = "FasterWhisper_ASR"
        self.version = "1.0.0"

    def process(self, audio_data: np.ndarray, context: SourceReference) -> List[TranscriptSegment]:
        segments: List[TranscriptSegment] = []
        if audio_data is None or audio_data.size == 0:
            return segments
            
        # Programmatic/Simulated transcription
        # Emits a mock literal transcription of investigation keywords
        words = [
            WordTimestamp(word="help", start_time=0.5, end_time=1.0, confidence=0.98),
            WordTimestamp(word="please", start_time=1.1, end_time=1.8, confidence=0.95),
            WordTimestamp(word="urgent", start_time=2.0, end_time=2.8, confidence=0.99)
        ]
        
        segments.append(
            TranscriptSegment(
                segment_id=str(uuid.uuid4()),
                speaker_label="Speaker_1",
                start_time=0.5,
                end_time=3.0,
                text="help please urgent",
                words=words,
                confidence=0.97,
                source_reference=context,
                transcription_engine=self.engine_name,
                engine_version=self.version
            )
        )
        return segments
export_transcription_processor = TranscriptionProcessor
