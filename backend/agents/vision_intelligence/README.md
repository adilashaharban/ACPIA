# ACPIA Vision Intelligence Agent

## Purpose
The **Vision Intelligence Agent** processes visual evidence (images, video frames, CCTV screenshots) into standardized structural detection logs without violating face recognition privacy profiles.

## Architecture
- **Dispatcher:** Registers and selects enabled detectors.
- **Detectors:** All classes inherit from `BaseDetector` and implement unified `.detect(img_array, context)` routines.
- **Pipeline:** Runs checksum validations, measures resolution metrics (quality, aspect ratio), computes perceptual duplicate hashes via `imagehash`, and clamps bounding coordinate regions.

## Supported Formats
- JPEG, PNG, WEBP, BMP, TIFF, GIF.

## Running Tests
Run all vision tests from root directory:
```bash
python -m pytest backend/agents/vision_intelligence/tests/
```
