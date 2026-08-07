# -*- coding: utf-8 -*-
"""Timestamp normalizer module."""

from datetime import datetime, timezone
import dateutil.parser
from backend.agents.timeline_intelligence.exceptions import TimestampNormalizationError
from backend.agents.timeline_intelligence.schema import TimestampPrecision

class TimestampNormalizer:
    """Normalizes string datetimes into timezone-aware UTC datetime values."""
    
    @staticmethod
    def normalize(raw_val: str) -> datetime:
        """Parses ISO or standard string datetimes and shifts timezone to UTC.
        
        Args:
            raw_val: Raw datetime string.
            
        Returns:
            Timezone-aware UTC datetime object.
            
        Raises:
            TimestampNormalizationError: If value is empty or unparseable.
        """
        if not raw_val:
            raise TimestampNormalizationError("Timestamp value is empty.")
            
        try:
            parsed = dateutil.parser.parse(raw_val.strip())
            # If naive, localize to UTC
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            else:
                parsed = parsed.astimezone(timezone.utc)
            return parsed
        except Exception as e:
            raise TimestampNormalizationError(f"Failed to normalize timestamp '{raw_val}': {e}")

    @staticmethod
    def infer_precision(raw_val: str) -> TimestampPrecision:
        """Infers the precision from string patterns.
        
        Args:
            raw_val: Raw datetime string.
            
        Returns:
            TimestampPrecision enum.
        """
        val = raw_val.strip()
        if len(val) == 4 and val.isdigit():
            return TimestampPrecision.YEAR
        if len(val) == 7 and val[4] == "-" and val[:4].isdigit() and val[5:].isdigit():
            return TimestampPrecision.MONTH
            
        # Standard fallback is SECOND or MILLISECOND
        if "." in val:
            return TimestampPrecision.MILLISECOND
        return TimestampPrecision.SECOND
export_normalizer = TimestampNormalizer
