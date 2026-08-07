# -*- coding: utf-8 -*-
"""Unit tests for AudioDispatcher."""

import pytest
from backend.agents.audio_intelligence.dispatcher import AudioDispatcher
from backend.agents.audio_intelligence.exceptions import UnsupportedCodecError
from backend.agents.audio_intelligence.processors.transcription_processor import TranscriptionProcessor

def test_dispatcher_valid_mime() -> None:
    """Verifies that audio/wav returns the list of registered processor classes."""
    dispatcher = AudioDispatcher()
    processors = dispatcher.get_processors("audio/wav")
    assert len(processors) > 0
    assert TranscriptionProcessor in processors

def test_dispatcher_invalid_mime() -> None:
    """Verifies that non-audio MIME formats raise UnsupportedCodecError."""
    dispatcher = AudioDispatcher()
    with pytest.raises(UnsupportedCodecError):
        dispatcher.get_processors("text/plain")
