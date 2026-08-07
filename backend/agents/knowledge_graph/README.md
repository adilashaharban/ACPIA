# ACPIA Knowledge Graph Agent

## Purpose
The **Knowledge Graph Agent** transforms canonical entities and observables into standard graph representations.

## Repositories
Supports:
- **MemoryRepository:** thread-safe local dictionary storage.
- **NetworkXRepository:** builds a `networkx.MultiDiGraph` for density and cycles checks.
- **Neo4jRepository:** mock persistence layer.

## Running Tests
Run tests from repository root:
```bash
python -m pytest backend/agents/knowledge_graph/tests/
```
