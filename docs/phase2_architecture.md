# Phase 2 Architecture & Technical Specification

## Project: AI-Assisted Vendor Risk Classification and Trust Assessment System
**Institution**: Vishwakarma Institute of Technology, Pune  
**Department**: Information Technology  
**Academic Year**: 2026–2027  

---

## 1. System Overview & Architecture

Phase 2 augments the verified quantitative Phase 1 foundation (multi-factor rule scoring, scikit-learn & XGBoost classification, PostgreSQL persistence) with an evidence-grounded Document Intelligence & Multi-Agent RAG platform.

```
                    UNSTRUCTURED & TABULAR VENDOR DATA
                    (PDF, DOCX, TXT, CSV, Scanned Docs)
                                    |
                                    v
                     [ Document Ingestion Engine ]
                     - File validation & Sanitization
                     - SHA-256 Deduplication
                     - Extractor Dispatcher (PyMuPDF, python-docx, pandas)
                     - Tesseract OCR Fallback
                                    |
                                    v
                     [ Text Cleaning & Chunking ]
                     - Whitespace & Heading Normalization
                     - Semantic Chunking (800 tokens, 150 overlap)
                     - Source & Page Metadata Tagging
                                    |
                                    v
                     [ Vector Storage & Retrieval ]
                     - ChromaDB Local Persistent Collections
                     - Vendor-Isolated Collections / Metadata Filtering
                     - Hybrid RAG Retrieval Layer
                                    |
                                    v
             ============= LangGraph Multi-Agent Layer =============
             |                                                     |
             +--> [ Financial Risk Agent ]                         |
             +--> [ Cybersecurity Risk Agent ]                     |
             +--> [ Regulatory Compliance Agent ]                  |
             +--> [ Operational Risk Agent ]                       |
             +--> [ Reputation Risk Agent ]                        |
             =======================================================
                                    |
                                    v
                     [ Verification & Evidence Agent ]
                     - Quote verification & Page cross-referencing
                     - Hallucination downgrade & Anti-fabrication check
                                    |
                                    v
                     [ Unified Risk Aggregator ]
                     - Phase 1 Quantitative (50%) + Phase 2 Qualitative (50%)
                     - Mathematical Trust Assessment Score (TAS)
                                    |
                                    v
                     [ FastAPI REST API + React UI Dashboard ]
```

---

## 2. Phase 2 Database Schema Plan

### A. Document Metadata Table (`documents`)
* `document_id` (VARCHAR(64), Primary Key): Unique identifier (`doc_<hex>`).
* `vendor_id` (INTEGER, Foreign Key -> `vendors.vendor_id` ON DELETE CASCADE): Vendor relationship.
* `original_filename` (VARCHAR(255)): Sanitized original filename.
* `stored_filepath` (VARCHAR(512)): Absolute path on filesystem.
* `file_type` (VARCHAR(32)): File extension (`pdf`, `docx`, `txt`, `csv`).
* `file_size` (INTEGER): Size in bytes.
* `content_hash` (VARCHAR(64), Indexed): SHA-256 digest to prevent duplicate processing.
* `upload_timestamp` (TIMESTAMP): Upload timestamp.
* `processing_status` (VARCHAR(32)): `PENDING`, `PROCESSED`, `FAILED`.
* `page_count` (INTEGER): Number of detected pages.
* `extraction_method` (VARCHAR(64)): `PYMUPDF`, `PYTHON_DOCX`, `PLAIN_TEXT`, `PANDAS_CSV`, `PYMUPDF+OCR`.
* `extracted_text` (TEXT): Full raw text extracted.
* `error_message` (TEXT, Nullable): Diagnostic error if extraction failed.

### B. Document Chunks Table (`document_chunks`) [Milestone 2]
* `chunk_id` (VARCHAR(64), Primary Key): Unique chunk ID.
* `document_id` (VARCHAR(64), Foreign Key -> `documents.document_id`).
* `vendor_id` (INTEGER): Vendor ownership.
* `page_number` (INTEGER): Source page.
* `chunk_index` (INTEGER): 0-indexed sequence.
* `token_count` (INTEGER): Estimated token count.
* `chunk_text` (TEXT): Chunk text content.
* `content_hash` (VARCHAR(64)): Chunk content hash.

### C. Multi-Agent Assessment Table (`ai_assessments`) [Milestone 5-7]
* `assessment_id` (INTEGER, Primary Key): Autoincrement ID.
* `vendor_id` (INTEGER, Foreign Key -> `vendors.vendor_id`).
* `financial_score` (FLOAT) & `financial_findings` (JSON)
* `cybersecurity_score` (FLOAT) & `cybersecurity_findings` (JSON)
* `compliance_score` (FLOAT) & `compliance_findings` (JSON)
* `operational_score` (FLOAT) & `operational_findings` (JSON)
* `reputation_score` (FLOAT) & `reputation_findings` (JSON)
* `verification_status` (VARCHAR(32))
* `aggregated_tas_score` (FLOAT)
* `final_risk_classification` (VARCHAR(32))
* `created_at` (TIMESTAMP)

---

## 3. Milestone Status Tracker

| Milestone | Description | Status |
|---|---|---|
| **Milestone 0** | Inspection, Architecture Design, Compatibility Audit | **COMPLETED** |
| **Milestone 1** | Document Ingestion Engine & Extractors (PDF, DOCX, TXT, CSV, OCR) | **COMPLETED** |
| **Milestone 2** | Text Cleaning, Deduplication, and Chunking Service | *Pending Approval* |
| **Milestone 3** | Embeddings Generation & ChromaDB Vector Store Integration | *Pending Approval* |
| **Milestone 4** | RAG Retrieval Layer & Evidence Citation Attribution | *Pending Approval* |
| **Milestone 5** | Five Specialized Risk Agents (Financial, Security, Compliance, Operational, Reputation) | *Pending Approval* |
| **Milestone 6** | Verification Agent & LangGraph Orchestration Workflow | *Pending Approval* |
| **Milestone 7** | Risk Aggregation Engine (Phase 1 + Phase 2 Integration) | *Pending Approval* |
| **Milestone 8** | Modern Interactive React + Tailwind Dashboard | *Pending Approval* |
| **Milestone 9** | End-to-End Testing, Documentation & Viva Preparation | *Pending Approval* |

