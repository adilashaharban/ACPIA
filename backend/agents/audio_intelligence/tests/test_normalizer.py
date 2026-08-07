# -*- coding: utf-8 -*-
"""Unit tests for AudioNormalizer."""

from backend.agents.audio_intelligence.normalizer import AudioNormalizer

def test_clamp_timestamp() -> None:
    """Verifies that timestamp offsets clamp correctly between positive ranges."""
    assert AudioNormalizer.clamp_timestamp(-5.5) == 0.0
    assert AudioNormalizer.clamp_timestamp(12.34567, max_duration=10.0) == 10.0
    assert AudioNormalizer.clamp_timestamp(2.5678) == 2.568
