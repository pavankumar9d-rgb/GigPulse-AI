# GigPulse AI — Master Implementation Plan

**Project:** GigPulse AI (Multi-Platform Gig Worker Earnings Intelligence)  
**Based on:** `docs/10_IMPLEMENTATION_ROADMAP.md` and `docs/09_TESTING_EVALUATION.md`  
**Current Status:** Phase 0 Completed (Reconnaissance) — Ready for Phase 1  

---

## Roadmap Overview

```
Phase 0: Reconnaissance & Environment Audit [COMPLETED]
   │
   ▼
Phase 1: Research Contract, Data Foundations & Deterministic Generator
   │
   ▼
Phase 2: Local-First Modular Monolith (Core Ledger & Overview Slice)
   │
   ▼
Phase 3: Worker Earnings Prediction Engine (Baseline to Tree Models)
   │
   ▼
Phase 4: Zone/Time Demand & Activity Forecasting (Spatial/Temporal)
   │
   ▼
Phase 5: Intelligent Opportunity Recommendation & Decision Engine
   │
   ▼
Phase 6: Mobility-Fintech UI/UX Polish & Model Lab
   │
   ▼
Phase 7: Security, Privacy, Governance & Deployment Hardening
   │
   ▼
Phase 8: Research Evaluation, Documentation & Viva Preparation
```

---

## Phase Details & Acceptance Criteria

### Phase 0: Reconnaissance & Environment Audit
- **Status:** **COMPLETED**
- **Artifacts:**
  - `RECONNAISSANCE.md` (completed)
  - `IMPLEMENTATION_PLAN.md` (completed)
- **Stop Gate:** Await user sign-off on Phase 0 before writing application code.

---

### Phase 1: Research Contract & Data Foundation
- **Goal:** Establish core domain entities, integer paise monetary math, time-interval union logic, CSV schema validation, and deterministic synthetic data generator.
- **Tasks:**
  1. Initialize git repository (`git init`) and commit documentation baseline.
  2. Setup root-level structure or symlinks (`docs/`, `data/`, `diagrams/`).
  3. Create isolated Python environment (`.venv`) with core data libraries (`polars` or `pandas`, `pydantic`, `pytest`).
  4. Implement `gigpulse-core` domain logic:
     - Integer paise currency types and conversion helpers.
     - Overlapping session interval union algorithm (`IntervalSet`).
     - Gross vs net earnings calculator with itemized expenses.
  5. Implement CSV ingestion and validation engine conforming to the 4 template schemas:
     - `deliveries_template.csv`
     - `work_sessions_template.csv`
     - `expenses_template.csv`
     - `zone_demand_template.csv`
  6. Implement deterministic synthetic data generator adhering strictly to `SYNTHETIC_DATA_SPEC.md` (`source_type="synthetic"`, seed-based, JSON manifest).
- **Acceptance Criteria & Verification:**
  - Unit tests verify 100% precision on integer paise math (no float inaccuracies).
  - Interval union handles edge cases (subsumed, touching, disjoint intervals).
  - Validation engine rejects malformed headers, missing required fields, and invalid enum values.
  - Synthetic dataset generates valid CSVs and passes its own validation suite with `synthetic=true` manifest.
  - Run: `pytest tests/test_domain_core.py tests/test_synthetic_generator.py`

---

### Phase 2: Local-First Vertical Slice (Modular Monolith)
- **Goal:** Working local-first prototype covering DB schema, API CRUD for sessions/deliveries/expenses, and single-page overview dashboard.
- **Tasks:**
  1. Setup SQLite database with SQLAlchemy/Alembic schema models (12 entities from `05_DATA_DICTIONARY_SCHEMA.md`).
  2. Implement FastAPI service (`services/api`) with endpoints:
     - `GET /api/v1/health`
     - `GET /api/v1/dashboard/summary`
     - `POST /api/v1/imports/validate` (preview)
     - `POST /api/v1/imports/{id}/commit` (idempotent commit)
     - Core CRUD for platforms, sessions, deliveries, expenses.
  3. Scaffold Next.js + TypeScript + Tailwind frontend (`apps/web`):
     - Mobility-fintech dark theme tokens (`#0B1220`, `#111C2E`, teal `#36C8B4`).
     - Persistent "Synthetic Data" warning banner.
     - Overview dashboard cards: Gross earnings, net earnings, online hours (unioned), active hours, earnings/online hour.
  4. Seed database with Phase 1 synthetic fixtures.
- **Acceptance Criteria & Verification:**
  - End-to-end flow: start backend + frontend, load dashboard, display KPIs computed from seeded SQLite data.
  - API validation tests pass with zero errors.
  - UI renders cleanly at 360px mobile and 1440px desktop widths.
  - Run: `pytest tests/test_api_endpoints.py` and frontend test suite.

---

### Phase 3: Worker Earnings Prediction Engine
- **Goal:** Predict worker gross/net earnings per online hour using chronological cross-validation and baseline comparison.
- **Tasks:**
  1. Construct feature extraction pipeline with point-in-time constraints (worker historical rates, temporal cyclical features, platform factors).
  2. Implement baseline models:
     - Global median
     - Platform median
     - Platform × Day-of-week × Hour-of-day median
     - Seasonal naive
  3. Implement machine learning models (ElasticNet, Random Forest / HistGradientBoosting / LightGBM).
  4. Implement uncertainty estimation (quantile regression / residual prediction intervals).
  5. Backtest evaluation harness: 70/15/15 chronological split. Compute MAE, RMSE, WAPE.
  6. Model registry persistence & serialization.
- **Acceptance Criteria & Verification:**
  - Zero time-leakage: test set features use only past information relative to cutoff.
  - Candidate model must outperform median/seasonal baselines on held-out test data, or baseline is retained.
  - Run: `pytest tests/test_earnings_models.py` and generate evaluation report.

---

### Phase 4: Zone/Time Demand & Activity Forecasting
- **Goal:** Forecast zone-level delivery demand or activity proxy counts with explicit target labelling.
- **Tasks:**
  1. Build spatio-temporal aggregation pipeline for hourly zone buckets.
  2. Implement strict target classification (`requested_orders` vs `completed_orders` vs `observed_deliveries` vs `proxy`).
  3. Implement demand baselines (Last-bucket, Seasonal-naive, Rolling mean).
  4. Implement demand forecasting models (Poisson/Negative-Binomial GLM, Gradient Boosted Regressor).
  5. API endpoint `POST /api/v1/forecasts/demand` returning prediction envelope with target quality and coverage fraction.
  6. Frontend Demand Map component with zone overlays.
- **Acceptance Criteria & Verification:**
  - System refuses to label individual delivery observations as city-wide requested orders.
  - Demand predictions provide prediction intervals and data quality flags.
  - Run: `pytest tests/test_demand_forecasting.py`.

---

### Phase 5: Intelligent Opportunity Recommendation Engine
- **Goal:** Rank feasible platform-zone-time candidate work options under user constraints and uncertainty penalties.
- **Tasks:**
  1. Implement candidate generator for `(platform, zone, time_window)`.
  2. Implement hard constraint filtering (max travel distance, vehicle type, committed hours).
  3. Implement multi-objective scoring formula:
     $$\text{Score} = \hat{y}_{\text{net}} - \lambda_{\text{risk}} \cdot \text{UncertaintyPenalty} - \text{TravelCost}$$
  4. Implement explainability breakdown (transparent components, no black-box scores).
  5. Implement abstention rules for out-of-distribution or data-sparse zones.
  6. API endpoint `POST /api/v1/recommendations/preview` and Opportunity Planner UI.
- **Acceptance Criteria & Verification:**
  - Recommendations satisfy all user hard constraints.
  - Explanations list exact mathematical contributions of payout, fuel cost, and uncertainty penalty.
  - Advisory language only: no income promises or automated dispatch.
  - Run: `pytest tests/test_recommendation_engine.py`.

---

### Phase 6: Product & UX Polish + Model Lab
- **Goal:** High-standard mobility-fintech experience across all 7 views.
- **Tasks:**
  1. Complete 7 core views: Overview, Earnings, Demand Map, Opportunity Planner, Activity & Imports, Model Lab, Settings & Privacy.
  2. Build Model Lab view: show backtest performance curves, baseline comparisons, feature importances (SHAP/coefficients), and limitations.
  3. Accessibility audit: WCAG 2.2 AA compliance, keyboard navigation, focus indicators, tabular data alternatives for charts.
  4. Responsive styling verification across mobile, tablet, and desktop viewports.
- **Acceptance Criteria & Verification:**
  - Every chart displays metric name, unit, time window, and data source/quality.
  - Zero dead buttons or mock handlers.
  - Persistent synthetic demo banner is visible across all views when in demo mode.

---

### Phase 7: Security, Privacy & Governance Hardening
- **Goal:** Production-readiness review, privacy safeguards, and threat model verification.
- **Tasks:**
  1. Input sanitization and SQL injection audit (all queries parameterized).
  2. Safe CSV import/export audit (formula injection prevention, file size limits).
  3. Location privacy check: ensure only H3 zone indices are stored, no precise GPS coordinates.
  4. Test data export and account deletion endpoints (`POST /api/v1/data/export`, `DELETE /api/v1/account/data`).
  5. Security test suite covering IDOR, injection, and oversized payloads.
- **Acceptance Criteria & Verification:**
  - Negative security test suite passes 100%.
  - Zero hardcoded secrets, API keys, or platform credentials in codebase or git.

---

### Phase 8: Academic Deliverables & Research Documentation
- **Goal:** Research artifacts, final report chapters, viva prep, and demo verification.
- **Tasks:**
  1. Compile evaluation metrics table comparing all models vs baselines on held-out splits.
  2. Export high-resolution diagrams using the Archify skill from `diagrams/*.mmd`.
  3. Generate final academic report sections matching `docs/12_ACADEMIC_DELIVERABLES.md`.
  4. Execute and rehearse the 5–7 minute end-to-end evaluation demo script.
- **Acceptance Criteria & Verification:**
  - All research claims are tied directly to reproducible experiment runs.
  - 100% of test suites passing cleanly.

---

## Next Immediate Action

Awaiting user approval of Phase 0. Upon approval, begin **Phase 1: Research Contract & Data Foundation** (git initialization, domain-core types, CSV validators, and synthetic data generator).

