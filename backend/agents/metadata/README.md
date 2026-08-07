# ACPIA Metadata Agent

## Purpose
The **Metadata Agent** extracts technical, structural, and hardware attributes from evidence files. It processes files deterministically to ensure forensic trace accuracy without altering data or performing AI reasoning.

## Responsibilities
- Read raw filesystem metadata (size, permissions, OS timestamps).
- Check integrity match of the file against the ingestion hash.
- Dispatch parsing tasks based on verified MIME classes.
- Extract EXIF, GPS, camera details, video resolutions, frame rates, audio specs, and PDF properties.
- Normalise coordinates, codec names, and dates to timezone-aware UTC datetime.

## Folder Structure
```
backend/
└── agents/
    └── metadata/
        ├── __init__.py
        ├── constants.py
        ├── contracts.py
        ├── exceptions.py
        ├── schema.py
        ├── metrics.py
        ├── dispatcher.py
        ├── normalizer.py
        ├── validator.py
        ├── pipeline.py
        ├── agent.py
        ├── README.md
        │
        ├── extractors/
        │   ├── __init__.py
        │   ├── generic_extractor.py
        │   ├── image_extractor.py
        │   ├── video_extractor.py
        │   ├── audio_extractor.py
        │   └── document_extractor.py
        │
        └── tests/
```

## Inputs
Accepts `AgentResultContract` from the Intake Agent:
- `file_path` (str)
- `sha256_hash` (str)
- `mime_type` (str)

## Outputs
Returns a standard `AgentResultContract` wrapping `MetadataPackage` payload:
- **Summary details:** category flags, completeness ratios.
- **File statistics:** dimensions, codecs, formats, durations.
- **Hardware trace:** Camera make/model, GPS coordinates.
- **Diagnostics:** Completeness, validation issues.

## Testing & Execution
Run tests from the root directory:
```bash
python -m pytest backend/agents/metadata/tests/
```
