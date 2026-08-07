# -*- coding: utf-8 -*-
"""Constants used by the Metadata Agent."""

from enum import Enum

class MetadataState(str, Enum):
    """Lifecycle stages during metadata extraction processing."""
    STARTED = "STARTED"
    INTEGRITY_VERIFIED = "INTEGRITY_VERIFIED"
    EXTRACTING = "EXTRACTING"
    NORMALIZING = "NORMALIZING"
    VALIDATING = "VALIDATING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


# MIME Type categories mapping to specific extractors
MIME_GROUPS = {
    "image": ["image/jpeg", "image/png", "image/gif", "image/webp"],
    "video": ["video/mp4", "video/mpeg", "video/quicktime", "video/x-msvideo"],
    "audio": ["audio/mpeg", "audio/wav", "audio/ogg", "audio/x-wav"],
    "document": ["application/pdf"],
    "text": ["text/plain", "application/json"],
}

# Coordinate limits for physical verification checks
GPS_LIMITS = {
    "MIN_LATITUDE": -90.0,
    "MAX_LATITUDE": 90.0,
    "MIN_LONGITUDE": -180.0,
    "MAX_LONGITUDE": 180.0,
}

# Tag names mappings for normalized fields
EXIF_TAGS_MAP = {
    "MAKE": "Make",
    "MODEL": "Model",
    "SOFTWARE": "Software",
    "DATETIME": "DateTime",
    "GPS_LAT": "GPSLatitude",
    "GPS_LONG": "GPSLongitude",
    "GPS_ALT": "GPSAltitude",
}
