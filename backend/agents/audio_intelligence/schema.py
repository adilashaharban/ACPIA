# -*- coding: utf-8 -*-
"""Pydantic V2 schema definitions for the Audio Intelligence Agent."""

from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import Field
from backend.schemas.common import ACPIABaseModel, SourceReference

class BackgroundSoundType(str, Enum):
    """Supported acoustic class categorization enums."""
    SIREN = "SIREN"
    GUNSHOT = "GUNSHOT"
    SCREAM = "SCREAM"
    EXPLOSION = "EXPLOSION"
    VEHICLE = "VEHICLE"
    FOOTSTEPS = "FOOTSTEPS"
    DOG_BARK = "DOG_BARK"
    BACKGROUND_NOISE = "BACKGROUND_NOISE"
    UNKNOWN = "UNKNOWN"


class KeywordMatchType(str, Enum):
    """Types of keyword match checks."""
    EXACT = "EXACT"
    CASE_INSENSITIVE = "CASE_INSENSITIVE"


class SpeakerSegment(ACPIABaseModel):
    """Conversation turn segment mapping Speaker_N intervals."""
    segment_id: str
    speaker_label: str = Field(..., pattern=r"^Speaker_\d+$", description="Constrained label Speaker_1, Speaker_2...")
    start_time: float
    end_time: float
    confidence: float
    source_reference: SourceReference


class WordTimestamp(ACPIABaseModel):
    """Specific word timestamp alignment details."""
    word: str
    start_time: float
    end_time: float
    confidence: float


class TranscriptSegment(ACPIABaseModel):
    """Textual speech segment."""
    segment_id: str
    speaker_label: str = Field(..., pattern=r"^Speaker_\d+$")
    start_time: float
    end_time: float
    text: str
    words: List[WordTimestamp] = Field(default_factory=list)
    confidence: float
    source_reference: SourceReference
    transcription_engine: str
    engine_version: str


class AudioStatistics(ACPIABaseModel):
    """Acoustic signal counts and formats."""
    duration_seconds: float
    speaker_count: int
    word_count: int
    silence_duration_seconds: float
    average_db: float
    sample_rate: int
    channel_count: int
    bit_depth: Optional[int] = Field(default=None)


class AudioQuality(ACPIABaseModel):
    """Signal assessment details."""
    signal_to_noise_ratio: float
    noise_level_db: float
    clipping_ratio: float
    is_low_quality: bool


class LanguageInformation(ACPIABaseModel):
    """Language detection details."""
    primary_language: str
    confidence: float
    detected_languages: List[str] = Field(default_factory=list)


class DetectedKeyword(ACPIABaseModel):
    """Keyword search detection metrics."""
    keyword: str
    matched_text: str
    match_type: KeywordMatchType
    start_time: float
    end_time: float
    confidence: float
    segment_id: str


class BackgroundSound(ACPIABaseModel):
    """Ambient background sound classification details."""
    sound_class: BackgroundSoundType
    start_time: float
    end_time: float
    confidence: float


class SilenceSegment(ACPIABaseModel):
    """Silence timeline sections."""
    start_time: float
    end_time: float
    duration_seconds: float


class AudioValidation(ACPIABaseModel):
    """Diagnostic checks warning lists."""
    integrity_status: str = "PASS"
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)


class ProcessorExecution(ACPIABaseModel):
    """Provenance execution logs per signal engine."""
    processor_name: str
    processor_version: str
    execution_time_ms: float
    status: str


class AudioMetrics(ACPIABaseModel):
    """Consolidated performance profile."""
    processing_time_ms: float
    executions: List[ProcessorExecution] = Field(default_factory=list)


class AudioSummary(ACPIABaseModel):
    """General summary metrics."""
    mime_type: str
    has_speech: bool
    diarization_run: bool
    transcription_engine: str
    engine_version: str
    average_transcript_confidence: float


class AudioPackage(ACPIABaseModel):
    """Root standardized acoustic package payload schema."""
    schema_version: str = "1.0.0"
    evidence_id: str
    summary: AudioSummary
    transcript: List[TranscriptSegment] = Field(default_factory=list)
    speakers: List[SpeakerSegment] = Field(default_factory=list)
    keywords: List[DetectedKeyword] = Field(default_factory=list)
    silences: List[SilenceSegment] = Field(default_factory=list)
    sounds: List[BackgroundSound] = Field(default_factory=list)
    language: LanguageInformation
    quality: AudioQuality
    statistics: AudioStatistics
    validation: AudioValidation
    metrics: AudioMetrics
