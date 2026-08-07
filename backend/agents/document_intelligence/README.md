# ACPIA Document Intelligence Agent

## Purpose
The **Document Intelligence Agent** converts visual or structural document formats (PDF, DOCX, TXT, CSV, HTML, JSON, XML, EML, WhatsApp Export) into standardized text blocks, tables, and form fields. It provides downsteam agents with layout-independent text feeds, complete with geometric coordinate tracing (bounding boxes) and reading orders.

## Architecture
- **Dispatcher:** Dynamically routes incoming document types to their format-specific parser engine.
- **Parsers:** Separate classes inheriting `BaseParser` using pdfplumber, python-docx, BS4, EML, or WhatsApp regex sweeps.
- **OCR Engine:** Pluggable scan fallback triggering OCR if embedded page word counts drop below threshold.
- **Normalizer & Validator:** Collapses whitespace and evaluates row/cell structural warnings.

## Inputs
Accepts `AgentResultContract` from the Metadata Agent containing:
- `evidence_id` (str)
- `file_specs` (FileMetadata)

## Outputs
Returns `AgentResultContract` wrapping `DocumentPackage` payload:
- **Pages Structure:** Extracted paragraph sequences, reading flow indexes.
- **Tables Array:** Cells, headers, rows, columns, reading orders.
- **Diagnostics:** Completeness ratios, validation warnings.

## Integration & Consumption
- **Entity Resolution:** Consumes normalized paragraph lists.
- **Timeline:** Inspects text blocks and header boundaries.
- **RAG:** Maps page-segmented text elements directly to vector embeddings.

## Running Tests
Run all document tests from root directory:
```bash
python -m pytest backend/agents/document_intelligence/tests/
```
