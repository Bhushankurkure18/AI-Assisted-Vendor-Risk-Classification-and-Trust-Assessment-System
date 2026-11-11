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
│   │   ├── core/                 # App configurations & database engine
│   │   ├── models/               # Vendor & Assessment SQLAlchemy models
│   │   ├── schemas/              # Pydantic validation & ML schemas
│   │   ├── routes/               # API endpoints (/vendors, /assess, /api/v1/ml)
│   │   ├── services/             # RiskEngine, MLService, MFG006MLService
│   │   └── main.py               # FastAPI entry point
│   └── requirements.txt          # Python dependencies
├── ml/
│   ├── mfg006_preprocessing.py   # Zero-leakage ColumnTransformer pipeline
│   ├── mfg006_train.py           # RF & XGBoost training & explainability
│   ├── rule_based_baseline.py    # Deterministic multi-factor baseline
│   ├── preprocessing.py          # Legacy synthetic generator
│   ├── train.py                  # Legacy training script
│   └── evaluate.py               # Legacy evaluation script
├── data/
│   ├── raw/
│   │   ├── mfg006_disruptions.csv # Primary empirical dataset (3000 rows x 113 cols)
│   │   └── vendors.csv           # Legacy synthetic dataset
│   └── processed/
├── models/
│   ├── mfg006_random_forest.joblib  # Trained Random Forest model (MFG006)
│   ├── mfg006_xgboost.joblib        # Trained XGBoost model (MFG006)
│   ├── mfg006_preprocessor.joblib   # Fitted ColumnTransformer (151 features)
│   └── mfg006_feature_metadata.json # Complete feature schema & class metadata
├── reports/
│   ├── figures/mfg006/           # 12 publication-grade EDA & importance plots
│   ├── MFG006_EDA_SUMMARY.md     # Empirical data analysis summary
│   ├── MFG006_MODEL_COMPARISON.md# Comprehensive RF vs XGBoost benchmark
│   ├── MFG006_EXPLAINABILITY.md  # Top 20 feature drivers & attribution
│   └── mfg006_metrics.json       # Machine-readable evaluation metrics
├── docs/
│   ├── MFG006_FEATURE_SELECTION.md   # Zero-leakage audit (40 kept, 61 dropped)
│   ├── MFG006_FEATURE_ENGINEERING.md # 4 pre-disruption engineered features
│   ├── MFG006_RULE_BASELINE.md       # Deterministic baseline specification
│   ├── PROJECT_METHODOLOGY_AND_SCORING.md # Full mathematical scoring framework
│   └── FIRST_50_PERCENT_STATUS.md    # Formal 50% milestone audit report
├── tests/
│   ├── test_mfg006_ml.py         # 18 automated tests for MFG006 ML pipeline
│   ├── test_risk_engine.py       # Legacy rule engine tests
│   ├── test_vendors.py           # Legacy vendor CRUD tests
│   └── test_assessments.py       # Legacy assessment flow tests
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

## MFG006 Machine Learning Workflow (Primary Structured Component)

The structured ML foundation utilizes the empirical **MFG006 Disruption Dataset** (`mfg006_disruptions.csv`, 3000 rows × 113 columns) to predict operational disruption severity (`low`, `medium`, `high`, `critical`) using **only pre-disruption variables** (zero target leakage).

### 1. Validate Dataset & Fit Preprocessing Pipeline
Splits data into stratified 80/20 train/test sets, fits scikit-learn `ColumnTransformer` (RobustScaler + OneHotEncoder) strictly on $X_{\text{train}}$, and saves artifacts:
```powershell
.\.venv\Scripts\python.exe scripts/validate_dataset_and_pipeline.py
```

### 2. Generate Exploratory Data Analysis (EDA) Figures
Generates 11 publication-grade figures saved to `reports/figures/mfg006/`:
```powershell
.\.venv\Scripts\python.exe scripts/generate_mfg006_eda.py
```

### 3. Run Rule-Based Baseline
Evaluates the deterministic 5-dimension rule engine on the held-out test set:
```powershell
.\.venv\Scripts\python.exe -m ml.rule_based_baseline
```

### 4. Train Random Forest & XGBoost Classifiers
Trains both balanced ensemble models, calculates metrics on the held-out test set, extracts top 20 feature importances, and generates comparison reports:
```powershell
.\.venv\Scripts\python.exe -m ml.mfg006_train
```

### Model Performance Benchmark on Test Set ($N_{\text{test}} = 600$)

| Model | Accuracy | Macro Precision | Macro Recall | Macro F1-Score | Weighted F1-Score |
|---|---|---|---|---|---|
| **Rule-Based Baseline** | `35.00%` | `0.2631` | `0.2585` | `0.2594` | `0.3438` |
| **Random Forest** | `64.33%` | `0.6282` | `0.5489` | `0.5376` | `0.6292` |
| **XGBoost (Recommended)** | `91.50%` | `0.8843` | `0.8310` | `**0.8532**` | `**0.9127**` |

---

## Running the API

Start the FastAPI application with Uvicorn:
```powershell
.\.venv\Scripts\uvicorn.exe backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

Interactive Swagger UI documentation is available at:
👉 **`http://127.0.0.1:8000/docs`**

---

## API Endpoints

### 1. Structured MFG006 Machine Learning Endpoints
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/ml/health` | Check ML models, preprocessor, and library health |
| `POST` | `/api/v1/ml/predict` | Predict disruption severity level (`low`, `medium`, `high`, `critical`) + softmax probabilities |
| `POST` | `/api/v1/ml/risk-explanation` | Feature attribution explaining key risk drivers and resilience buffers |

### 2. Vendor Registry & Assessment Endpoints (Legacy / Database)
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Root API health status |
| `POST` | `/vendors` | Register new vendor with dimension scores |
| `GET` | `/vendors` | List registered vendors |
| `GET` | `/vendors/{vendor_id}` | Retrieve vendor details by ID |
| `POST` | `/assess/{vendor_id}` | Run combined rule-based and ML risk evaluation on database vendor |
| `GET` | `/assessments/{vendor_id}` | Retrieve historical risk assessments for a vendor |

---

## Running Automated Tests

Run the full pytest suite (31 tests covering both legacy endpoints and new MFG006 ML pipeline):
```powershell
.\.venv\Scripts\pytest.exe -v
```

---

## Implementation Status

### COMPLETED (First 50% Milestone)
- [x] MFG006 empirical dataset validation (3000 rows × 113 columns)
- [x] Zero-target-leakage feature selection audit (40 pre-disruption features kept, 61 leakage dropped, 11 identifiers removed)
- [x] Reproducible scikit-learn `ColumnTransformer` preprocessing pipeline (`mfg006_preprocessor.joblib`)
- [x] 11 publication-grade EDA figures and empirical summary (`reports/figures/mfg006/`)
- [x] 4 pre-disruption engineered features with division-by-zero safeguards
- [x] Transparent deterministic rule-based baseline (`ml/rule_based_baseline.py`)
- [x] Balanced Random Forest classifier (`mfg006_random_forest.joblib`)
- [x] High-accuracy XGBoost classifier (`mfg006_xgboost.joblib`)
- [x] Model comparison report & metrics JSON (`reports/MFG006_MODEL_COMPARISON.md`)
- [x] Model explainability, feature attribution, and importance plots (`reports/MFG006_EXPLAINABILITY.md`)
- [x] Saved reusable model & metadata artifacts (`models/`)
- [x] Non-breaking FastAPI REST endpoints (`/api/v1/ml/health`, `/predict`, `/risk-explanation`)
- [x] Automated test suite: 31 passed in Pytest with zero failures
- [x] Comprehensive college project documentation in `docs/` and `reports/`

### FUTURE WORK (Phase 2: Multi-Agent & Qualitative Intelligence)
- [ ] PDF document ingestion via PyMuPDF
- [ ] Semantic vector search using ChromaDB
- [ ] Retrieval-Augmented Generation (RAG)
- [ ] Multi-agent orchestration (Financial, Security, Compliance, Operational, Reputation Agents)
- [ ] Verification Agent with citation cross-referencing
- [ ] React + Tailwind CSS interactive frontend dashboard
