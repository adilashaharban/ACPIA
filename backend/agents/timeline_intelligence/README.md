# ACPIA Timeline Intelligence Agent

## Purpose
The **Timeline Intelligence Agent** normalizes, deduplicates, and sorts timeline events from ingestion files, document pages, images, and audio tracks to construct a unified chronological sequence.

## Repositories
Supports:
- **MemoryRepository:** thread-safe local dictionary storage.
- **SQLiteRepository:** persistent database storage with entity, evidence, and time-range query support.

## Running Tests
Run tests from repository root:
```bash
python -m pytest backend/agents/timeline_intelligence/tests/
```
