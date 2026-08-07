# -*- coding: utf-8 -*-
"""Audio processor dispatcher."""

from typing import List, Type, Optional
from backend.agents.audio_intelligence.exceptions import UnsupportedCodecError
from backend.agents.audio_intelligence.processors.base_processor import BaseProcessor
from backend.agents.audio_intelligence.processors.transcription_processor import TranscriptionProcessor
from backend.agents.audio_intelligence.processors.diarization_processor import DiarizationProcessor
from backend.agents.audio_intelligence.processors.vad_processor import VadProcessor
from backend.agents.audio_intelligence.processors.keyword_processor import KeywordProcessor
from backend.agents.audio_intelligence.processors.language_processor import LanguageProcessor
from backend.agents.audio_intelligence.processors.quality_processor import QualityProcessor
from backend.agents.audio_intelligence.processors.silence_processor import SilenceProcessor
from backend.agents.audio_intelligence.processors.background_sound_processor import BackgroundSoundProcessor
from backend.agents.audio_intelligence.constants import AUDIO_MIME_GROUPS

class AudioDispatcher:
    """Dispatches audio signals to registered sub-processors."""
    
    def __init__(self, custom_processors: Optional[List[Type[BaseProcessor]]] = None) -> None:
        """Registers default acoustic processors."""
        self._processors: List[Type[BaseProcessor]] = [
            TranscriptionProcessor,
            DiarizationProcessor,
            VadProcessor,
            KeywordProcessor,
            LanguageProcessor,
            QualityProcessor,
            SilenceProcessor,
            BackgroundSoundProcessor,
        ]
        if custom_processors:
            self._processors = custom_processors

    def get_processors(self, mime_type: str) -> List[Type[BaseProcessor]]:
        """Resolves active processor classes.
        
        Args:
            mime_type: File signature MIME type string.
            
        Returns:
            A list of processor classes inheriting BaseProcessor.
            
        Raises:
            UnsupportedCodecError: If MIME is not associated with audios.
        """
        if not mime_type:
            raise UnsupportedCodecError("MIME type string is empty.")
            
        normalized = mime_type.lower().strip()
        
        # Verify visual signature
        is_supported = False
        for category, mimes in AUDIO_MIME_GROUPS.items():
            if normalized in mimes:
                is_supported = True
                break
                
        if not is_supported and not normalized.startswith("audio/"):
            raise UnsupportedCodecError(f"Unsupported audio codec or MIME format: {mime_type}")
            
        return self._processors
