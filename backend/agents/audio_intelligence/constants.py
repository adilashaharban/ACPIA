# -*- coding: utf-8 -*-
"""Constants for the Audio Intelligence Agent."""

from enum import Enum

class AudioState(str, Enum):
    """Lifecycle stages of acoustic and transcription analysis."""
    STARTED = "STARTED"
    VALIDATED = "VALIDATED"
    RUNNING_PROCESSORS = "RUNNING_PROCESSORS"
    NORMALIZING = "NORMALIZING"
    VALIDATING_OUTPUTS = "VALIDATING_OUTPUTS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


# MIME type categorizations mapping to audio
AUDIO_MIME_GROUPS = {
    "wav": ["audio/wav", "audio/x-wav"],
    "mp3": ["audio/mpeg", "audio/mp3"],
    "aac": ["audio/aac", "audio/x-aac"],
    "flac": ["audio/flac", "audio/x-flac"],
    "m4a": ["audio/m4a", "audio/x-m4a", "audio/mp4"],
    "ogg": ["audio/ogg", "audio/x-ogg"],
}

# Signal limits
SILENCE_THRESHOLD_DB = -40.0
NOISE_FLOOR_CLIPPING_RATIO = 0.05
DEFAULT_KEYWORDS_LIST = ["help", "stop", "police", "sos", "urgent"]
