# -*- coding: utf-8 -*-
"""Constants for the Cross-Evidence Correlation Agent."""

ENTITY_SIMILARITY_THRESHOLD = 0.85
TEMPORAL_TOLERANCE_SECONDS = 60.0
GPS_RADIUS_METERS = 500.0

# Confidence weights (summing up to 1.0)
WEIGHT_ENTITY = 0.30
WEIGHT_TEMPORAL = 0.20
WEIGHT_LOCATION = 0.20
WEIGHT_GRAPH = 0.15
WEIGHT_CONTENT = 0.15
