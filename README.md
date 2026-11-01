# GigPulse AI

> **AI-Driven Machine Learning for Spatio-Temporal Earnings Prediction, Demand Forecasting & Intelligent Optimization of Multi-Platform Gig Delivery Partners**

[![Python Version](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.135.2-009688.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14.2-black.svg)](https://nextjs.org/)
[![Tests Passing](https://img.shields.io/badge/tests-53%20passed-brightgreen.svg)](#testing)
[![Budget](https://img.shields.io/badge/cost-%E2%82%B90%20(Local%20CPU)-teal.svg)](#zero-cost-architecture)

---

## 1. Project Overview

**GigPulse AI** is an academic research and operational platform engineered to empower gig delivery workers (food delivery, quick-commerce, parcel couriers) operating across multiple concurrent platforms (e.g., Zomato, Swiggy, Zepto, Blinkit, FlashDrop, SwiftBite).

Delivery gig workers face severe income volatility, opaque algorithmic compensation, and platform multi-homing friction. GigPulse AI provides:

1. **Net Earnings Prediction:** Quantile regression and Gradient Boosted Trees forecasting net take-home pay per online hour with 80% confidence envelopes, subtracting operating costs (fuel, maintenance) and unioning overlapping multi-app shifts using a sweepline algorithm.
2. **Spatio-Temporal Zone Demand Forecasting:** Multi-step forward-looking demand predictions per geographical zone, strictly preserving target taxonomy (never conflating individual observed deliveries with total market demand).
3. **Intelligent Opportunity Optimization:** An explainable recommendation engine that scores and ranks candidate `(platform, zone, time)` options under worker constraints (maximum travel distance, minimum rate, risk preference) with transparent reason attribution.

---

## 2. System Architecture

GigPulse AI is designed as a **local-first modular monolith**:

```
GigPulse-AI/
├── packages/
│   └── gigpulse-core/               # Core domain logic, models, and ML pipelines
│       ├── gigpulse_core/
│       │   ├── db/                  # SQLite schema, importer, repository, seed scripts
│       │   ├── ml/                  # Earnings predictor, demand forecaster, optimizer
│       │   ├── money.py             # Authoritative 64-bit integer paise arithmetic
│       │   ├── intervals.py         # Sweepline interval union algorithm
│       │   ├── validator.py         # CSV sanitization & formula-injection neutralization
│       │   └── synthetic_generator.py # Deterministic synthetic baseline generator
├── services/
│   └── api/                         # FastAPI REST API service
│       ├── main.py                  # Entrypoint runner with port auto-detection
│       └── api/                     # Config, dependencies, errors, schemas, routers
├── apps/
│   └── web/                         # Next.js 14 + Tailwind CSS dashboard
│       ├── src/app/                 # Next.js App Router (layout, page, globals.css)
│       ├── src/components/          # 11 interactive dashboard views
│       └── src/lib/api.ts           # Typed API client with port-fallback resilience
├── data/
│   └── synthetic/                   # 8-week validated baseline fixtures
├── tests/                           # 53 automated tests (unit, integration, ML, API)
├── models/                          # Serialized model artifacts & evaluation metadata
└── IMPLEMENTATION_PLAN.md           # Master roadmap audit
```

---

## 3. Quickstart Guide (Windows PowerShell)

### Prerequisites
- Python 3.11+ (Python 3.13 tested)
- Node.js 18+ & npm (Node v24 tested)
- Git

### Step 1: Install Python Package & Dependencies

```powershell
# In the repository root
pip install -e packages/gigpulse-core
pip install fastapi uvicorn sqlalchemy pydantic scikit-learn pandas joblib pytest
```

### Step 2: Initialize SQLite Database & Seed Data

```powershell
python -m gigpulse_core.db.seed gigpulse.db data/synthetic
```

### Step 3: Train Machine Learning Models

```powershell
python -m gigpulse_core.ml.training gigpulse.db
```

### Step 4: Run the Complete Test Suite

```powershell
python -m pytest
```
*(All 53 tests will execute and pass)*

---

## 4. Starting the Application

### Start Backend API

```powershell
# Starts FastAPI server on http://127.0.0.1:8000 (or 8001 if 8000 is occupied)
python services/api/main.py
```
- Swagger Interactive Docs: `http://127.0.0.1:8000/docs` (or `:8001/docs`)
- OpenAPI Schema: `http://127.0.0.1:8000/openapi.json`

### Start Frontend Dashboard

In a second terminal:

```powershell
cd apps/web
npm install
npm run dev
```
Open **`http://localhost:3000`** in any web browser.

---

## 5. Frontend Dashboard Capabilities

The Next.js dashboard features 11 dedicated analytical sections:

1. **Overview:** Holistic KPI strip (Gross Payout, Operating Expenses, Net Take-Home, Unioned Online Hours, Rate/hr), platform share bars, and top recommendation banner.
2. **Earnings Analytics:** Net vs Gross toggle, multi-platform revenue distribution, and dispatch records table.
3. **Earnings Predictor:** Interactive ML inference form (platform, zone, time, duration) with Q10–Q50–Q90 uncertainty envelopes.
4. **Delivery Performance:** Dispatch logs, transit distances, completion durations, incentives, and tips.
5. **Zone Demand:** Spatio-temporal forecasting timeline across 30-minute intervals with lower and upper prediction intervals.
6. **Platform Comparisons:** Head-to-head metrics (order counts, payout averages, tip frequencies).
7. **Opportunity Planner:** Multi-objective candidate ranking with constraint sliders (max travel distance, minimum rate, risk preference) and explainability bullets.
8. **Expense Analysis:** Fuel and maintenance breakdown with operating expense ratio tracking.
9. **Data Imports:** 3-step safe CSV ingestion stepper (upload, schema validation audit, and explicit commit).
10. **Model Lab:** Held-out backtest evaluation tables comparing candidate models against baselines, plus interval calibration and retrain button.
11. **Settings & Privacy:** Worker profile configuration, structured JSON data export, and confirmed account data purge.

---

## 6. Machine Learning Evaluation Highlights

| Target | Candidate Model | Naive Baseline | Out-of-Sample MAE | Out-of-Sample WAPE | Interval Coverage |
|:---|:---|:---|:---:|:---:|:---:|
| **Net Earnings (₹/hr)** | Gradient Boosted Trees (Q50) | Global Median Baseline | **₹29.53/hr** (vs ₹44.80) | **27.26%** (vs 41.35%) | 64.71% (80% nominal) |
| **Zone Demand (count)** | HistGradientBoosting Regressor | Last-Bucket Naive | **5.83** (vs 9.69) | **22.80%** (vs 37.88%) | 76.32% (80% nominal) |

Both models were backtested on strictly chronological splits with zero time-leakage.

---

## 7. Zero-Cost & Security Architecture

- **₹0 Cost:** Fully runnable on local CPU laptop; zero cloud subscriptions, paid databases, or external AI APIs required.
- **SQL Injection Prevention:** 100% of queries use SQLAlchemy parameterized constructs.
- **CSV Formula Injection Neutralization:** Dangerous spreadsheet prefixes (`=`, `+`, `-`, `@`) are stripped or escaped during import validation.
- **Integer Minor Units:** All monetary arithmetic is computed in 64-bit integer paise to prevent IEEE 754 floating-point rounding errors.

---

## 8. License & Academic Attribution

Developed as an academic software engineering and research project under the title:  
*AI-Driven Machine Learning for Spatio-Temporal Earnings Prediction, Demand Forecasting & Intelligent Optimization of Multi-Platform Gig Delivery Partners.*

