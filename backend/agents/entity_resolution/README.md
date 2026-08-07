# ACPIA Entity Resolution Agent

## Purpose
The **Entity Resolution Agent** groups candidate observations extracted from metadata, document content, vision tags, and transcripts into canonical resolved entities.

## Matching Strategy
- **Exact Blocking:** Buckets candidate elements by Type.
- **Fuzzy Cluster Matching:** Checks similarity using Levenshtein distance and Jaro-Winkler via `rapidfuzz`.

## Running Tests
Run tests from repository root:
```bash
python -m pytest backend/agents/entity_resolution/tests/
```
