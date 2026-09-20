# AI-Assisted Vendor Risk Classification and Trust Assessment System

An academic, runnable, and empirically validated 50% prototype for assessing and classifying enterprise third-party vendor risks using multi-factor rule scoring, machine-learning classification (Random Forest & XGBoost), PostgreSQL persistence, and FastAPI REST endpoints.

---

## Problem Statement

Modern enterprises engage hundreds of external vendors for cloud hosting, software solutions, logistics, and data processing. Manual risk evaluations are subjective, slow, and prone to inconsistent auditing. Organizations require an automated, transparent, and reproducible system that combines structured quantitative risk dimensions with predictive machine learning to categorize vendor risk objectively.

---

## Objectives

1. Maintain structured vendor profiles across 5 risk dimensions: Financial, Security, Compliance, Operational, and Reputation.
2. Provide deterministic rule-based weighted risk calculation and categorization.
3. Train and compare supervised machine learning classifiers (Random Forest vs XGBoost) on actual vendor data.
4. Expose clean REST endpoints with interactive Swagger documentation.
5. Provide data-grounded, explainable risk assessments.
6. Provide an automated test suite verifying business logic and endpoints.

---

## Architecture

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

---

## Technology Stack

* **Backend**: Python 3.14+, FastAPI, Uvicorn, Pydantic v2
* **Database**: PostgreSQL, SQLAlchemy ORM
* **Data & ML**: Pandas, NumPy, Scikit-learn, XGBoost, Joblib
* **Testing**: Pytest, HTTPX
* **API Documentation**: OpenAPI / Swagger UI
* **Version Control**: Git

---

## Directory Structure

```
vendor-risk-system/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   ├── config.py         # App configurations & risk weights
│   │   │   └── database.py       # Engine & session management
│   │   ├── models/
│   │   │   ├── vendor.py         # Vendor SQLAlchemy model
│   │   │   └── assessment.py     # Assessment SQLAlchemy model
│   │   ├── schemas/
│   │   │   ├── vendor.py         # Pydantic validation schemas
│   │   │   └── assessment.py     # Assessment response schemas
│   │   ├── routes/
│   │   │   ├── vendors.py        # /vendors CRUD routes
│   │   │   └── assessments.py    # /assess routes
│   │   ├── services/
│   │   │   ├── preprocessing.py  # Validation & feature cleaning
│   │   │   ├── risk_engine.py    # Weighted 5-factor scoring engine
│   │   │   └── ml_service.py     # Random Forest / XGBoost inference
│   │   ├── utils/
│   │   │   └── helpers.py        # Formatting utilities
│   │   └── main.py               # FastAPI entry point
│   └── requirements.txt          # Python dependencies
├── ml/
│   ├── preprocessing.py          # Synthetic dataset generator & loader
│   ├── train.py                  # Random Forest & XGBoost training
│   ├── predict.py                # Prediction utility
│   └── evaluate.py               # Model evaluation & comparison
├── data/
│   ├── raw/                      # vendors.csv (synthetic data)
│   └── processed/
├── models/                       # random_forest.pkl, xgboost.pkl
├── tests/
│   ├── test_risk_engine.py       # Rule engine unit tests
│   ├── test_vendors.py           # Vendor endpoint tests
│   └── test_assessments.py       # Assessment flow tests
├── notebooks/
├── .env.example
├── .gitignore
├── README.md
└── PROJECT_ROADMAP.md
```

---

## Installation & Setup

### 1. Clone or Open Workspace
Ensure you are in the workspace root directory:
```bash
cd "D:\EDI SEM 5 PROJECT FILE"
```

### 2. Python Environment Setup
Create and activate a virtual environment:
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:
```powershell
pip install -r backend/requirements.txt
```

### 3. PostgreSQL Setup
1. Install PostgreSQL (e.g. version 15 or 16).
2. Create the database:
   ```sql
   CREATE DATABASE vendor_risk_db;
   ```
3. Copy `.env.example` to `.env` and set your credentials:
   ```bash
   DATABASE_URL=postgresql://postgres:your_password@localhost:5432/vendor_risk_db
   ```
*(Note: If PostgreSQL is not yet running locally, the application automatically employs SQLite fallback for local verification and testing without crashing.)*

---

## Dataset & Machine Learning Workflow

### 1. Generate Synthetic Dataset (Milestone 2)
Generates 600 realistic vendor records logically labeled across LOW, MEDIUM, and HIGH risk:
```powershell
.\.venv\Scripts\python.exe -c "from ml.preprocessing import generate_synthetic_dataset, RAW_DATA_PATH; df = generate_synthetic_dataset(); df.to_csv(RAW_DATA_PATH, index=False); print(f'Saved {len(df)} records to {RAW_DATA_PATH}')"
```

### 2. Train Machine Learning Classifiers (Milestones 5 & 6)
Trains both Random Forest and XGBoost models and persists them to `models/`:
```powershell
.\.venv\Scripts\python.exe -m ml.train
```

### 3. Evaluate Models (Milestone 7)
Computes genuine test-set metrics (Accuracy, Precision, Recall, F1, Confusion Matrix):
```powershell
.\.venv\Scripts\python.exe -m ml.evaluate
```

---

## Running the API

Start the FastAPI application with Uvicorn:
```powershell
.\.venv\Scripts\uvicorn.exe backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

Interactive Swagger UI documentation is available at:
👉 **`http://127.0.0.1:8000/docs`**

Alternative ReDoc documentation:
👉 **`http://127.0.0.1:8000/redoc`**

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Health check & API status |
| `POST` | `/vendors` | Register new vendor with dimension scores |
| `GET` | `/vendors` | List registered vendors |
| `GET` | `/vendors/{vendor_id}` | Retrieve vendor details by ID |
| `POST` | `/assess/{vendor_id}` | Run combined rule-based and ML risk evaluation |
| `GET` | `/assessments/{vendor_id}` | Retrieve historical risk assessments for a vendor |

---

## Running Automated Tests

Run the full pytest suite:
```powershell
.\.venv\Scripts\pytest.exe -v
```

---

## Implementation Status

### COMPLETED (50% Prototype)
- [x] Project architecture and modular package structure (M1)
- [x] Synthetic 600-sample vendor dataset with grounded labels (M2)
- [x] Reusable data validation and preprocessing pipeline (M3)
- [x] 5-dimension rule-based weighted risk calculation engine (M4)
- [x] Random Forest multi-class risk classifier (M5)
- [x] XGBoost multi-class risk classifier (M6)
- [x] Empirical evaluation and comparison report (M7)
- [x] PostgreSQL & resilient SQLAlchemy ORM integration (M8 & M9)
- [x] Vendor CRUD REST API endpoints (M10)
- [x] Unified assessment API endpoint (M11)
- [x] Automated pytest test suite (M12)
- [x] Project documentation & viva preparation guide (M13)

### FUTURE WORK (Phase 2)
- [ ] PDF document ingestion via PyMuPDF
- [ ] Semantic vector search using ChromaDB
- [ ] Retrieval-Augmented Generation (RAG)
- [ ] LangGraph multi-agent orchestration (Financial, Security, Compliance, Operational, Reputation Agents)
- [ ] Verification Agent with citation cross-referencing
- [ ] React + Tailwind CSS interactive frontend dashboard
- [ ] Docker containerization and cloud deployment
