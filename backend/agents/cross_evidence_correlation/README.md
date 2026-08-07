# ACPIA Cross-Evidence Correlation Agent

## Purpose
The **Cross-Evidence Correlation Agent** identifies deterministic links and conflicts across entities, timelines, metadata, visual, and graph structures.

## Repositories
Supports:
- **MemoryRepository:** thread-safe local dictionary storage.
- **SQLiteRepository:** persistent database storage with custom entity, evidence, and time-range query support.

## Running Tests
Run tests from repository root:
```bash
python -m pytest backend/agents/cross_evidence_correlation/tests/
```
