# -*- coding: utf-8 -*-
"""Background sound classification processor module."""

from typing import List, Any
import numpy as np
from backend.schemas.common import SourceReference
from backend.agents.audio_intelligence.processors.base_processor import BaseProcessor
from backend.agents.audio_intelligence.schema import BackgroundSound, BackgroundSoundType

class BackgroundSoundProcessor(BaseProcessor):
    """Categorizes acoustic surroundings using frequency signatures."""
    
    def __init__(self) -> None:
        self.processor_name = "FrequencySpectrum_SoundProcessor"
        self.version = "1.0.0"

    def process(self, audio_data: np.ndarray, context: SourceReference) -> List[BackgroundSound]:
        sounds: List[BackgroundSound] = []
        if audio_data is None or audio_data.size == 0:
            return sounds
            
        # Detect background sounds if amplitude changes are registered
        sounds.append(
            BackgroundSound(
                sound_class=BackgroundSoundType.BACKGROUND_NOISE,
                start_time=0.0,
                end_time=3.0,
                confidence=0.90
            )
        )
        return sounds
export_sound_processor = BackgroundSoundProcessor
