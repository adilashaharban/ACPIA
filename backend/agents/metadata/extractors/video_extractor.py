# -*- coding: utf-8 -*-
"""Video metadata extractor using hachoir."""

from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata
from backend.agents.metadata.exceptions import ParserFailureError
from backend.agents.metadata.schema import VideoMetadata

class VideoExtractor:
    """Extracts width, height, duration, codecs, FPS, and bitrates from video streams."""
    
    @staticmethod
    def extract(file_path: str) -> VideoMetadata:
        """Parses video metadata tags.
        
        Args:
            file_path: Absolute string path.
            
        Returns:
            VideoMetadata schema.
            
        Raises:
            ParserFailureError: If parsing fails or file is unreadable.
        """
        parser = None
        try:
            parser = createParser(file_path)
            if not parser:
                raise ParserFailureError(f"Hachoir could not create parser for: {file_path}")
                
            metadata = extractMetadata(parser)
            if not metadata:
                raise ParserFailureError(f"Hachoir could not extract metadata from: {file_path}")
                
            # Width & Height
            width = metadata.get("width")
            height = metadata.get("height")
            
            # Duration (normally returned as timedelta)
            duration_val = metadata.get("duration")
            if isinstance(duration_val, timedelta):
                duration_seconds = duration_val.total_seconds()
            else:
                duration_seconds = float(duration_val or 0.0)
                
            # Frame rate (FPS)
            fps = float(metadata.get("frame_rate") or 0.0)
            
            # Codecs
            video_codec = str(metadata.get("video_codec") or "unknown")
            audio_codec = metadata.get("audio_codec")
            audio_codec_str = str(audio_codec) if audio_codec else None
            
            # Bitrate (hachoir returns bits per second)
            bitrate_bps = metadata.get("bitrate")
            bitrate_kbps = float(bitrate_bps) / 1000.0 if bitrate_bps else None
            
            # File container format
            container = Path(file_path).suffix.replace(".", "").lower()
            
            # Standardize resolution and duration defaults to prevent schema validation failures
            if not width or not height:
                # Default fallback or throw error
                width = width or 0
                height = height or 0
                
            return VideoMetadata(
                width=width,
                height=height,
                duration_seconds=duration_seconds,
                fps=fps,
                video_codec=video_codec,
                audio_codec=audio_codec_str,
                bitrate_kbps=bitrate_kbps,
                container=container
            )
            
        except Exception as e:
            raise ParserFailureError(f"Failed parsing video file: {e}")
        finally:
            if parser:
                parser.stream.close()
                
def _dummy_install_warning():
    """Hachoir requires no binary dll dependencies."""
    pass
