# ACPIA Evidence Intake Agent

## Purpose
The **Evidence Intake Agent** is the secure, deterministic gateway of the entire ACPIA platform. Every file uploaded for investigation must pass through this agent for fingerprinting, validation, storage, and initial registration before downstream analysis agents process it.

## Responsibilities
- Validate file sizes, empty uploads, and extensions.
- Detect actual file MIME types via binary magic signatures.
- Guard against path traversal attempts.
- Compute secure SHA-256 digests.
- Prevent duplicate evidence ingestion.
- Store file blocks to partition-friendly directory layouts.
- Record metadata and Chain of Custody trails to the database.
- Determine downstream routing targets.

## Inputs
Passed dynamically via the public interface execution call:
- `file_bytes` (bytes)
- `filename` (str)
- `case_id` (str)
- `uploader` (str)

## Outputs
Returns a standard `AgentResultContract` wrapping an `EvidencePackageContract` payload:
- **Evidence Identity:** `evidence_id`, `case_id`, `uploader`.
- **Integrity Information:** `sha256_hash`, timestamps.
- **Storage Details:** `file_path`, `object_storage_path`.
- **Routing Details:** Suggested list of downstream agents.
- **Chain of Custody Logs:** Full audit history.

## Config Options
Controlled by environmental variables parsed in `backend/core/config.py`:
- `ACPIA_ENV`: `development` or `production`.
- `ACPIA_DATABASE_URL`: Connection string (defaults to local SQLite).
- `ACPIA_STORAGE_DIR`: Local file persistence folder.
- `ACPIA_MAX_FILE_SIZE_BYTES`: Max bytes threshold.
