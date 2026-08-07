# -*- coding: utf-8 -*-
"""Constants for the Vision Intelligence Agent."""

from enum import Enum

class VisionState(str, Enum):
    """Lifecycle stages of visual analysis processing."""
    STARTED = "STARTED"
    VALIDATED = "VALIDATED"
    DUP_CHECKED = "DUP_CHECKED"
    RUNNING_DETECTORS = "RUNNING_DETECTORS"
    NORMALIZING = "NORMALIZING"
    VALIDATING_OUTPUTS = "VALIDATING_OUTPUTS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


# MIME type categorizations mapping to images
IMAGE_MIME_GROUPS = {
    "jpeg": ["image/jpeg", "image/jpg"],
    "png": ["image/png"],
    "webp": ["image/webp"],
    "bmp": ["image/bmp"],
    "tiff": ["image/tiff"],
    "gif": ["image/gif"],
}

# Image assessment limits
BLUR_THRESHOLD_VARIANCE = 100.0  # Variance of Laplacian <= 100 means blurry
BRIGHTNESS_THRESHOLD_DARK = 40.0 # Average pixel value <= 40 means dark
DUPLICATE_HAMMING_DISTANCE = 5   # Hamming distance <= 5 matches near duplicates
