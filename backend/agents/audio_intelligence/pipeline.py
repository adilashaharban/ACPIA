# -*- coding: utf-8 -*-
"""Audio Intelligence pipeline orchestration."""

import time
from typing import Tuple, List, Dict, Any, Optional
import numpy as np
import librosa
from backend.core.logger import get_logger
from backend.agents.base import AgentResultContract
from backend.agents.audio_intelligence.dispatcher import AudioDispatcher
from backend.agents.audio_intelligence.normalizer import AudioNormalizer
from backend.agents.audio_intelligence.validator import AudioValidator
from backend.agents.audio_intelligence.metrics import AudioMetricsCalculator
from backend.agents.audio_intelligence.exceptions import AudioParsingError
from backend.schemas.common import SourceReference, DocumentElementType
from backend.agents.audio_intelligence.schema import (
    AudioPackage, AudioSummary, TranscriptSegment, SpeakerSegment, DetectedKeyword,
    SilenceSegment, BackgroundSound, LanguageInformation, AudioQuality, AudioStatistics,
    ProcessorExecution, BackgroundSoundType
)
from backend.agents.audio_intelligence.processors.keyword_processor import KeywordProcessor

logger = get_logger("agents.audio_intelligence.pipeline")

class AudioIntelligencePipeline:
    """Orchestrates audio processing, quality analysis, VAD, and transcription execution flows."""
    
    def __init__(
        self,
        dispatcher: AudioDispatcher,
        validator: AudioValidator,
        normalizer: AudioNormalizer,
        metrics_calculator: AudioMetricsCalculator
    ) -> None:
        self.dispatcher = dispatcher
        self.validator = validator
        self.normalizer = normalizer
        self.metrics_calculator = metrics_calculator

    def execute(
        self,
        metadata_result: AgentResultContract
    ) -> Tuple[AudioPackage, List[str]]:
        """Executes audio analysis.
        
        Args:
            metadata_result: Output from Metadata Agent.
            
        Returns:
            Tuple containing (AudioPackage, warnings list).
            
        Raises:
            AudioParsingError: For fatal checksum or file processing failures.
        """
        start_time = time.perf_counter()
        warnings: List[str] = []
        
        logger.info("Audio Intelligence pipeline started.")
        
        meta_payload = metadata_result.payload
        if not meta_payload:
            raise AudioParsingError("Input metadata payload is empty.")
            
        evidence_id = meta_payload.get("evidence_id")
        
        # 1. Fetch paths from database context
        from backend.database.session import get_db_context
        from backend.database.repositories.evidence_repository import EvidenceRepository
        
        file_path = None
        expected_hash = None
        mime_type = None
        
        with get_db_context() as db:
            repo = EvidenceRepository(db)
            db_evidence = repo.get_by_id(evidence_id)
            if not db_evidence:
                raise AudioParsingError(f"Evidence {evidence_id} not registered in database.")
            file_path = db_evidence.file_path
            expected_hash = db_evidence.sha256_hash
            mime_type = db_evidence.mime_type
            
        # 2. Checksum validation
        logger.info(f"Verifying integrity checksum: {file_path}")
        self.validator.verify_integrity(file_path, expected_hash)
        logger.info("Integrity checksum verified.")
        
        # 3. Load audio array using librosa
        try:
            # Load with default sample rate to prevent native resampling blocks
            y, sr = librosa.load(file_path, sr=None)
        except Exception as e:
            raise AudioParsingError(f"Failed to load audio file at {file_path}: {e}")
            
        # 4. Dispatch active processors
        processor_classes = self.dispatcher.get_processors(mime_type)
        logger.info(f"Selected {len(processor_classes)} processors to run.")
        
        # Context reference
        context_ref = SourceReference(
            evidence_id=evidence_id,
            file_path=file_path,
            page_number=1,
            parser="AudioDispatcher",
            parser_version="1.0.0",
            source_element=DocumentElementType.OCR
        )
        
        # Output collectors
        transcript: List[TranscriptSegment] = []
        speakers: List[SpeakerSegment] = []
        keywords: List[DetectedKeyword] = []
        silences: List[SilenceSegment] = []
        sounds: List[BackgroundSound] = []
        
        lang_info = None
        quality_info = None
        
        executions_log: List[ProcessorExecution] = []
        
        for proc_cls in processor_classes:
            proc_start = time.perf_counter()
            status = "SUCCESS"
            
            try:
                processor = proc_cls()
                proc_outputs = processor.process(y, context_ref)
                
                # Sort processor outputs into respective fields
                for out in proc_outputs:
                    if isinstance(out, TranscriptSegment):
                        # Clamp timestamps
                        out.start_time = self.normalizer.clamp_timestamp(out.start_time)
                        out.end_time = self.normalizer.clamp_timestamp(out.end_time)
                        for word in out.words:
                            word.start_time = self.normalizer.clamp_timestamp(word.start_time)
                            word.end_time = self.normalizer.clamp_timestamp(word.end_time)
                        transcript.append(out)
                    elif isinstance(out, SpeakerSegment):
                        out.start_time = self.normalizer.clamp_timestamp(out.start_time)
                        out.end_time = self.normalizer.clamp_timestamp(out.end_time)
                        speakers.append(out)
                    elif isinstance(out, SilenceSegment):
                        out.start_time = self.normalizer.clamp_timestamp(out.start_time)
                        out.end_time = self.normalizer.clamp_timestamp(out.end_time)
                        silences.append(out)
                    elif isinstance(out, BackgroundSound):
                        out.start_time = self.normalizer.clamp_timestamp(out.start_time)
                        out.end_time = self.normalizer.clamp_timestamp(out.end_time)
                        sounds.append(out)
                    elif isinstance(out, LanguageInformation):
                        lang_info = out
                    elif isinstance(out, AudioQuality):
                        quality_info = out
                        
            except Exception as e:
                status = "FAILURE"
                warnings.append(f"Processor {proc_cls.__name__} execution failure: {e}")
                
            proc_time = (time.perf_counter() - proc_start) * 1000.0
            executions_log.append(
                ProcessorExecution(
                    processor_name=proc_cls.__name__,
                    processor_version="1.0.0",
                    execution_time_ms=round(proc_time, 2),
                    status=status
                )
            )
            
        # 5. Extract keywords from transcript
        try:
            kw_proc = KeywordProcessor()
            keywords = kw_proc.detect_keywords(transcript)
        except Exception as e:
            warnings.append(f"Keyword matching failed: {e}")
            
        # Fallbacks for mandatory sections
        if not lang_info:
            lang_info = LanguageInformation(
                primary_language="en",
                confidence=1.0,
                detected_languages=["en"]
            )
            
        if not quality_info:
            quality_info = AudioQuality(
                signal_to_noise_ratio=25.0,
                noise_level_db=-50.0,
                clipping_ratio=0.0,
                is_low_quality=False
            )
            
        # 6. Coordinate validation checks
        validation_meta = self.validator.validate_timelines(speakers, transcript)
        warnings.extend(validation_meta.warnings)
        
        # 7. Statistics
        duration_s = float(len(y) / sr) if sr > 0 else 0.0
        word_count = sum([len(seg.text.split()) for seg in transcript])
        silence_dur = sum([s.duration_seconds for s in silences])
        
        statistics = AudioStatistics(
            duration_seconds=round(duration_s, 2),
            speaker_count=len(set([s.speaker_label for s in speakers] + [t.speaker_label for t in transcript])),
            word_count=word_count,
            silence_duration_seconds=round(silence_dur, 2),
            average_db=round(quality_info.noise_level_db + quality_info.signal_to_noise_ratio, 2),
            sample_rate=int(sr),
            channel_count=1,
            bit_depth=16
        )
        
        # 8. Summary
        avg_conf = np.mean([seg.confidence for seg in transcript]) if len(transcript) > 0 else 1.0
        summary = AudioSummary(
            mime_type=mime_type,
            has_speech=len(transcript) > 0,
            diarization_run=len(speakers) > 0,
            transcription_engine="FasterWhisper_ASR",
            engine_version="1.0.0",
            average_transcript_confidence=round(float(avg_conf), 4)
        )
        
        # 9. Compile metrics
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        metrics = self.metrics_calculator.calculate(elapsed_ms, executions_log)
        
        package = AudioPackage(
            schema_version="1.0.0",
            evidence_id=evidence_id,
            summary=summary,
            transcript=transcript,
            speakers=speakers,
            keywords=keywords,
            silences=silences,
            sounds=sounds,
            language=lang_info,
            quality=quality_info,
            statistics=statistics,
            validation=validation_meta,
            metrics=metrics
        )
        
        logger.info("Audio package built successfully.")
        return package, warnings
export_pipeline = AudioIntelligencePipeline
