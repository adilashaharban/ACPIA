# -*- coding: utf-8 -*-
"""Unit tests for Acoustic Processors."""

import numpy as np
from backend.schemas.common import SourceReference, DocumentElementType
from backend.agents.audio_intelligence.processors.transcription_processor import TranscriptionProcessor
from backend.agents.audio_intelligence.processors.diarization_processor import DiarizationProcessor
from backend.agents.audio_intelligence.processors.vad_processor import VadProcessor
from backend.agents.audio_intelligence.processors.keyword_processor import KeywordProcessor
from backend.agents.audio_intelligence.processors.language_processor import LanguageProcessor
from backend.agents.audio_intelligence.processors.quality_processor import QualityProcessor
from backend.agents.audio_intelligence.processors.silence_processor import SilenceProcessor
from backend.agents.audio_intelligence.processors.background_sound_processor import BackgroundSoundProcessor
from backend.agents.audio_intelligence.schema import BackgroundSoundType, KeywordMatchType

def test_processors_running() -> None:
    """Verifies that all acoustic processor algorithms output expected structures and values."""
    # 3 seconds of silent tone array resampled at 8000Hz
    audio_data = np.zeros(24000, dtype=np.float32)
    
    context = SourceReference(
        evidence_id="EVID-AUD-1",
        file_path="mock.wav",
        page_number=1,
        parser="Test",
        parser_version="1.0.0",
        source_element=DocumentElementType.OCR
    )
    
    # 1. TranscriptionProcessor
    tx_proc = TranscriptionProcessor()
    segments = tx_proc.process(audio_data, context)
    assert len(segments) == 1
    assert segments[0].text == "help please urgent"
    
    # 2. DiarizationProcessor
    diar_proc = DiarizationProcessor()
    speakers = diar_proc.process(audio_data, context)
    assert len(speakers) == 1
    assert speakers[0].speaker_label == "Speaker_1"
    
    # 3. VadProcessor
    vad_proc = VadProcessor()
    vad_intervals = vad_proc.process(audio_data, context)
    # Silent array yields empty intervals
    assert len(vad_intervals) == 0
    
    # 4. KeywordProcessor
    kw_proc = KeywordProcessor()
    kw_detections = kw_proc.detect_keywords(segments)
    assert len(kw_detections) == 2  # matches "help" and "urgent" from segments
    assert kw_detections[0].keyword == "help"
    assert kw_detections[0].match_type == KeywordMatchType.CASE_INSENSITIVE
    
    # 5. LanguageProcessor
    lang_proc = LanguageProcessor()
    langs = lang_proc.process(audio_data, context)
    assert len(langs) == 1
    assert langs[0].primary_language == "en"
    
    # 6. QualityProcessor
    qual_proc = QualityProcessor()
    qual = qual_proc.process(audio_data, context)
    assert len(qual) == 1
    assert qual[0].is_low_quality is True
    
    # 7. SilenceProcessor
    sil_proc = SilenceProcessor()
    silences = sil_proc.process(audio_data, context)
    assert len(silences) == 1
    assert silences[0].duration_seconds == 0.5
    
    # 8. BackgroundSoundProcessor
    sound_proc = BackgroundSoundProcessor()
    sounds = sound_proc.process(audio_data, context)
    assert len(sounds) == 1
    assert sounds[0].sound_class == BackgroundSoundType.BACKGROUND_NOISE
