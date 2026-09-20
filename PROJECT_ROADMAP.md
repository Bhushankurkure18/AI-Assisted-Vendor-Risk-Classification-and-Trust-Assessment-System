# Project Roadmap: AI-Assisted Vendor Risk Classification and Trust Assessment System

This document outlines the phased development roadmap of the Vendor Risk Classification and Trust Assessment System, distinguishing the core 50% academic prototype from future production enhancements.

---

## Phase 1: 50% Core Architecture (Current Scope)

The primary goal of Phase 1 is to establish a rigorous, verified, and runnable quantitative risk assessment foundation:

```
                VENDOR INPUT
                     |
                     v
             +---------------+
             |    FastAPI    |
             |   REST API    |
             +-------+-------+
                     |
         +-----------+-----------+
         |                       |
         v                       v
+----------------+      +------------------+
|   PostgreSQL   |      | Data Validation  |
| Vendor Storage |      | & Preprocessing  |
+-------+--------+      +---------+--------+
        |                         |
        +------------+------------+
                     |
                     v
             +------------------+
             | Feature          |
             | Extraction       |
             +--------+---------+
                      |
         +------------+------------+
         |                         |
         v                         v
+-----------------+       +-----------------+
| Rule-Based      |       | ML Classifiers  |
| Risk Engine     |       | (Random Forest  |
| (5 Dimensions)  |       |  & XGBoost)     |
+--------+--------+       +--------+--------+
         |                         |
         +------------+------------+
                      |
                      v
             +------------------+
             | Risk Assessment  |
             | Score + Level    |
             +--------+---------+
                      |
                      v
             +------------------+
             | Explainable      |
             | Risk Report      |
             +------------------+
```

### Components in Current Prototype
1. **Vendor Registry**: CRUD storage for vendor metadata and financial/risk metrics.
2. **Deterministic Rule Engine**:
   - Financial: 25%
   - Security: 25%
   - Compliance: 20%
   - Operational: 20%
   - Reputation: 10%
   - Implementation Thresholds: 0–39 (LOW), 40–69 (MEDIUM), 70–100 (HIGH).
3. **Machine Learning Pipeline**:
   - Synthetic balanced dataset generator (500+ samples).
   - Random Forest Classifier.
   - XGBoost Classifier.
   - Empirical evaluation metrics (Accuracy, Precision, Recall, F1, Confusion Matrix).
4. **Data Persistence**: PostgreSQL with SQLAlchemy ORM (and resilient local fallback).
5. **REST API**: FastAPI with automatic OpenAPI / Swagger documentation at `/docs`.
6. **Automated Testing Suite**: Pytest test suite covering endpoints and business logic.

---

## Phase 2: Advanced Multi-Agent & RAG Architecture (Future Scope)

Phase 2 builds upon the validated Phase 1 foundation by augmenting quantitative metrics with unstructured qualitative document intelligence:

```
[ Unstructured Vendor Documents (Audit Reports, SOC2, Financial Statements) ]
                                |
                                v
                     [ PDF Document Extraction ] (PyMuPDF)
                                |
                                v
                     [ Chunking & Embeddings ]
                                |
                                v
                     [ Vector Database ] (ChromaDB)
                                |
                                v
                  [ Retrieval-Augmented Generation ] (RAG)
                                |
                                v
               [ Local / Hosted LLM ] (Ollama / Open-Weights)
                                |
                                v
         ================ Multi-Agent Analysis Layer ================
         |                                                         |
         +--> [ Financial Agent ]   (Balance sheets, debt trends)  |
         +--> [ Security Agent ]    (SOC2, ISO27001, pentests)     |
         +--> [ Compliance Agent ]  (GDPR, HIPAA, regulatory fines)|
         +--> [ Operational Agent ] (SLA history, business continuity)
         +--> [ Reputation Agent ]  (Adverse media, lawsuits)      |
         ===========================================================
                                |
                                v
                     [ Verification Agent ]
             (Cross-validates claims vs evidence citations)
                                |
                                v
         [ Unified Explainable Risk Dossier & Trust Score ]
                                |
                                v
               [ Interactive React + Tailwind Dashboard ]
```

### Planned Phase 2 Milestones
1. **Unstructured Document Ingestion**:
   - Native PDF processing using PyMuPDF.
   - Document metadata extraction and section tagging.
2. **Vector Store & Semantic Search**:
   - Document chunking, embedding generation, and ChromaDB vector persistence.
3. **LangGraph Multi-Agent Orchestration**:
   - Autonomous specialized agents for each of the 5 risk dimensions.
   - Verification Agent to eliminate hallucinations and confirm citations.
4. **Interactive Dashboard**:
   - React 18+ with Tailwind CSS for visual vendor risk exploration, radar charts, and audit trails.
5. **Containerization & Deployment**:
   - Docker Compose configuration for multi-container deployment (FastAPI + Postgres + ChromaDB + Ollama + Frontend).
