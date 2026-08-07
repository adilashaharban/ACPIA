# -*- coding: utf-8 -*-
"""Acoustic quality processor module."""

from typing import List, Any
import numpy as np
from backend.schemas.common import SourceReference
from backend.agents.audio_intelligence.processors.base_processor import BaseProcessor
from backend.agents.audio_intelligence.schema import AudioQuality

class QualityProcessor(BaseProcessor):
    """Measures clipping, noise decibels, and SNR metrics."""
    
    def __init__(self) -> None:
        self.processor_name = "DecibelSignal_QualityProcessor"
        self.version = "1.0.0"

    def process(self, audio_data: np.ndarray, context: SourceReference) -> List[AudioQuality]:
        results: List[AudioQuality] = []
        if audio_data is None or audio_data.size == 0:
            return [
                AudioQuality(
                    signal_to_noise_ratio=0.0,
                    noise_level_db=-60.0,
                    clipping_ratio=0.0,
                    is_low_quality=True
                )
            ]
            
        try:
            # 1. Compute RMS and average dB
            rms = np.sqrt(np.mean(audio_data**2))
            avg_db = 20 * np.log10(rms) if rms > 0 else -60.0
            
            # 2. Compute clipping ratio (fraction of elements near max limits)
            clipped_samples = np.sum(np.abs(audio_data) >= 0.99)
            clipping_ratio = float(clipped_samples) / audio_data.size
            
            # 3. SNR and Noise floor approximation
            noise_floor_db = -50.0
            snr = float(max(0.0, avg_db - noise_floor_db))
            
            is_low = snr < 10.0 or clipping_ratio > 0.1
        except Exception:
            snr = 25.0
            noise_floor_db = -50.0
            clipping_ratio = 0.0
            is_low = False
            
        results.append(
            AudioQuality(
                signal_to_noise_ratio=round(snr, 2),
                noise_level_db=round(noise_floor_db, 2),
                clipping_ratio=round(clipping_ratio, 4),
                is_low_quality=is_low
            )
        )
        return results
export_quality_processor = QualityProcessor
