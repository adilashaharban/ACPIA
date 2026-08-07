# -*- coding: utf-8 -*-
"""Audio normalizer module."""

class AudioNormalizer:
    """Clamps audio timestamp alignments and standardizes volume decibels."""
    
    @staticmethod
    def clamp_timestamp(val: float, max_duration: float = 10000.0) -> float:
        """Clamps time values.
        
        Args:
            val: Raw float timestamp.
            max_duration: Audio duration limit.
            
        Returns:
            Clamped float.
        """
        val_clamped = max(0.0, min(val, max_duration))
        return round(val_clamped, 3)
