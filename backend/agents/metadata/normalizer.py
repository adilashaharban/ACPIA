# -*- coding: utf-8 -*-
"""Metadata normalizer helper."""

from datetime import datetime, timezone
import re
from typing import Any, Optional, Tuple

class MetadataNormalizer:
    """Provides utility methods to standardize data types and layouts in metadata packages."""
    
    @staticmethod
    def normalize_date(date_val: Any) -> Optional[datetime]:
        """Ensures input timestamps are converted to timezone-aware UTC datetime.
        
        Args:
            date_val: String or datetime objects.
            
        Returns:
            Timezone-aware datetime in UTC, or None if invalid.
        """
        if not date_val:
            return None
            
        if isinstance(date_val, datetime):
            return date_val.astimezone(timezone.utc)
            
        date_str = str(date_val).strip()
        try:
            # Strip standard PDF or EXIF formats
            clean_str = re.sub(r"[^\d:\-\sT]", "", date_str)
            # Try YYYY-MM-DDTHH:MM:SS
            for fmt in (
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%d %H:%M:%S",
                "%Y:%m:%d %H:%M:%S",
                "%Y%m%d%H%M%S"
            ):
                try:
                    dt = datetime.strptime(clean_str[:19], fmt[:19])
                    return dt.replace(tzinfo=timezone.utc)
                except ValueError:
                    continue
        except Exception:
            pass
        return None

    @staticmethod
    def normalize_gps(degrees: float, minutes: float, seconds: float, ref: str) -> Optional[float]:
        """Normalizes degrees/minutes/seconds GPS rational arrays to decimal degrees.
        
        Args:
            degrees: GPS base degrees.
            minutes: GPS minutes.
            seconds: GPS seconds.
            ref: Cardinal reference compass direction (N, S, E, W).
            
        Returns:
            Decimal degrees float value, or None if invalid.
        """
        if not ref or ref.upper() not in ("N", "S", "E", "W"):
            return None
            
        try:
            decimal = float(degrees) + (float(minutes) / 60.0) + (float(seconds) / 3600.0)
            
            # South / West reference checks
            if ref.upper() in ("S", "W"):
                decimal = -decimal
                
            return decimal
        except (ValueError, TypeError):
            return None

    @staticmethod
    def normalize_codec(codec_name: Optional[str]) -> str:
        """Resolves raw codec names to uppercase canonical versions.
        
        Args:
            codec_name: Raw codec string.
            
        Returns:
            Standardized name string.
        """
        if not codec_name:
            return "unknown"
            
        clean = codec_name.strip().lower()
        if "h264" in clean or "avc" in clean:
            return "H.264/AVC"
        if "h265" in clean or "hevc" in clean:
            return "H.265/HEVC"
        if "mp3" in clean:
            return "MP3"
        if "aac" in clean or "mp4a" in clean:
            return "AAC"
        if "pcm" in clean or "wave" in clean:
            return "PCM/WAV"
            
        return codec_name.upper()
