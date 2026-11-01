# 03 — System Architecture and Technical Design

## 1. Architecture style

Use a **modular monolith** with a separately testable Python ML package. The MVP does not need microservices. Keep ingestion, domain logic, forecasting, optimization and presentation separated by module boundaries, but deploy them as a small number of processes.

## 2. Proposed stack

| Layer | Proposed choice | Reason / constraint |
|---|---|---|
| Web UI | Next.js App Router + TypeScript | Strong component model, routing and responsive web experience. Verify current version and official docs before scaffolding. |
| UI styling | Tailwind CSS or existing repo styling system | Fast consistent design tokens; avoid introducing two styling systems. |
| Charts | A maintained React chart library already supported by the chosen stack | Use for time series, comparison and uncertainty intervals; select after repository inspection. |
| Map | GeoJSON-based zone layer with a replaceable map renderer | App works with a static/demo layer; map tiles require separate provider/license review. |
| API | Python FastAPI + Pydantic | Python ecosystem for ML, typed request validation and OpenAPI. |
| Data processing | Polars or pandas | Start with the simplest tool that fits; avoid loading the same large table repeatedly. |
| ML | scikit-learn + statsmodels; optional LightGBM/CatBoost | Baselines and tree models are sufficient for first experiments. No mandatory GPU. |
| Explainability | Model-native feature effects / SHAP after model choice | Explanations are descriptive, not causal. |
| Canonical DB | PostgreSQL for hosted/multi-user mode | Transactions, constraints and row-level policies when using Supabase. |
| Local MVP storage | SQLite may be used for a single-user local prototype if limitations are explicit | Keep data-access functions portable; do not claim SQLite provides PostgreSQL RLS. |
| Optional backend platform | Supabase (Postgres/Auth/Storage) | Use only if remote multi-user access is needed; free-tier availability/terms can change. |
| Testing | pytest, frontend unit tests, Playwright | Test data logic, API contracts and real user journeys. |
| Version control | Git + lockfiles + optional GitHub Actions | Reproducibility and simple CI. |

Do not freeze package versions from this document. Check current official documentation and package compatibility at implementation time. Prefer versions supported by the user's environment.

## 3. Component responsibilities

### Frontend

- Route/layout, auth shell (if hosted), filters and user preferences.
- Dashboard, earnings, demand map, planner, history and model-lab screens.
- Typed API client and loading/empty/error states.
- No model training and no secret keys in browser code.

### API backend

- Authentication/authorization boundary.
- Validate CSV imports and map platform-specific columns to canonical fields.
- Expose summary and forecast endpoints.
- Invoke model inference and recommendation service.
- Persist prediction metadata, user preferences and audit information.
- Enforce user ownership and source visibility.

### Domain layer

- Money arithmetic in integer paise.
- Time-window calculations and timezone conversion.
- Shift/online/active-time semantics.
- Expense allocation rules.
- Candidate feasibility constraints.
- Data-source and confidence labels.

### ML package

- Data cleaning/feature generation.
- Baseline and candidate training.
- Chronological evaluation/backtesting.
- Model serialization and loading.
- Prediction intervals and coverage metadata.
- Feature attribution/reporting.

### Storage layer

- Raw import batch metadata.
- Normalized worker-owned operational records.
- Aggregate zone-time observations with provenance.
- Forecast runs, outputs, model version and evaluation records.

### External context adapters

- Weather adapter: optional and cached; app still works when offline.
- Geospatial adapter: H3 cell mapping and optional OSM-derived context with correct license/attribution.
- Calendar/events adapter: optional manually curated/permissioned context; never scrape arbitrary pages as an undocumented dependency.

## 4. Data flow

1. User imports a CSV or enters records manually.
2. API validates file type, size, encoding, columns, timestamp formats, currency, ranges and duplicate keys.
3. Valid rows are normalized into canonical entities with import provenance.
4. Domain service computes historical gross/net metrics and time denominators.
5. Feature pipeline builds training/inference rows using only information available at the forecast cutoff.
6. Training job evaluates baseline and candidate models on time-ordered splits.
7. Inference service produces prediction + interval + model/data metadata.
8. Demand output is attached to H3 zone/time buckets only when a supported demand label exists.
9. Recommendation engine filters candidates by hard constraints and scores remaining alternatives.
10. UI renders estimates with uncertainty, source and freshness labels.
11. Later observations are compared with saved forecasts for backtesting and drift checks.

## 5. Runtime/deployment modes

### Mode A — Local academic demo (first target)

- Next.js dev server + FastAPI process + local database.
- Synthetic dataset loaded by an explicit demo command.
- Models stored locally under a versioned artifact directory.
- No cloud credentials required.

### Mode B — Hosted pilot (later)

- Frontend hosted on a suitable static/serverless-capable platform.
- FastAPI hosted separately where Python inference is supported.
- PostgreSQL/Supabase for data and authentication.
- Secrets held in server environment; no platform credentials.
- RLS and server-side authorization tested before any participant data is used.

Avoid a deployment topology that requires a paid service to demonstrate the core research.

## 6. Suggested repository layout

```text
repo/
├── AGENTS.md
├── README.md
├── docs/                         # this project blueprint
├── apps/
│   └── web/                      # Next.js application
├── services/
│   └── api/                      # FastAPI application
├── packages/
│   └── shared-contracts/         # OpenAPI-generated or manually typed contracts
├── ml/
│   ├── data/                     # manifests, schemas; no private raw data in Git
│   ├── features/
│   ├── models/
│   ├── evaluation/
│   ├── reports/
│   └── artifacts/                # gitignored model artifacts
├── db/
│   ├── migrations/
│   └── seeds/                    # synthetic demo seed only
├── tests/
│   ├── integration/
│   └── e2e/
├── scripts/
├── .env.example
└── .gitignore
```

Adapt to an existing repository if one is already present. Do not create duplicate apps or folders without inspecting first.

## 7. Key architecture boundaries

- The UI never decides whether a user can access a record; the API/database does.
- The frontend never receives model-training files or secret API keys.
- A forecast result is immutable with its model version, input cutoff, data coverage and horizon.
- Synthetic demo mode is isolated from real user workspace data.
- Map renderer is replaceable; H3 cell IDs and zone contracts do not depend on tile vendor.
- Platform-specific CSV mapping lives in adapters, not in the core delivery model.
- Every external data provider has a source adapter, cache, license note and graceful-fallback behaviour.

## 8. Scalability path

1. Single-user local data and models.
2. Modular API + PostgreSQL + RLS for multiple consenting users.
3. Batch training and cached forecasts.
4. Background jobs only when workload requires them.
5. Distributed feature store/model serving only after measured scale demands it.

## 9. Architecture quality attributes

| Attribute | Design response |
|---|---|
| Reproducibility | Version datasets, transformations, code and model. |
| Privacy | Minimize location; separate identity from behavioural data. |
| Performance | Pre-aggregate zone/time summaries; avoid full-table scans in UI requests. |
| Reliability | Optional data providers fail independently. |
| Maintainability | Domain services and adapters; no business rules inside React components. |
| Portability | Local-first runtime and pinned lockfiles. |
| Explainability | Store model version, feature snapshot/summary, uncertainty and reason codes. |
