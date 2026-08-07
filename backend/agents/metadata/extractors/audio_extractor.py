# -*- coding: utf-8 -*-
"""Audio metadata extractor using mutagen."""

import mutagen
from backend.agents.metadata.exceptions import ParserFailureError
from backend.agents.metadata.schema import AudioMetadata

class AudioExtractor:
    """Extracts durations, sample rates, sound channels, and codecs from audio streams."""
    
    @staticmethod
    def extract(file_path: str) -> AudioMetadata:
        """Parses audio files.
        
        Args:
            file_path: Absolute string path.
            
        Returns:
            AudioMetadata schema.
            
        Raises:
            ParserFailureError: If unable to read or parse file tags.
        """
        try:
            audio = mutagen.File(file_path)
            if audio is None or audio.info is None:
                raise ParserFailureError(f"Mutagen could not parse audio track: {file_path}")
                
            info = audio.info
            
            # Duration (seconds)
            duration_seconds = float(getattr(info, "length", 0.0))
            
            # Sample rate (Hz)
            sample_rate = int(getattr(info, "sample_rate", 0))
            
            # Sound channels (1 = mono, 2 = stereo)
            channels = int(getattr(info, "channels", 0))
            
            # Bitrate (mutagen typically returns bits per second)
            bitrate_bps = getattr(info, "bitrate", 0.0)
            bitrate_kbps = float(bitrate_bps) / 1000.0 if bitrate_bps else 0.0
            
            # Audio codec identification
            codec = type(info).__name__.replace("Header", "").replace("Info", "").lower()
            if hasattr(audio, "mime") and audio.mime:
                codec = audio.mime[0].split("/")[-1].replace("x-", "")
                
            return AudioMetadata(
                duration_seconds=duration_seconds,
                sample_rate=sample_rate,
                bitrate_kbps=bitrate_kbps,
                channels=channels,
                audio_codec=codec
            )
            
        except Exception as e:
            raise ParserFailureError(f"Failed parsing audio file: {e}")
