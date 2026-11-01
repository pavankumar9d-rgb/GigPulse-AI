# Implementation Roadmap and Release Gates

## Delivery approach

Build a narrow, end-to-end vertical slice first. Do not build a large distributed system, real-time streaming stack, mobile app and deep-learning research stack simultaneously. The architecture starts as a modular monolith with independently testable Python ML modules.

## Phase 0 — Repository and environment reconnaissance

**Goal:** Understand the existing workspace before changing it.

Tasks:
- Inspect repository, current branch, git status, existing code, README, dependency files, environment variables and tests.
- Inspect runtime versions and memory/disk constraints; check whether Python, Node and database tools already exist.
- Read `AGENTS.md`, this folder and installed skill entrypoints relevant to the first task.
- Identify whether this is a new repository or an existing project; do not overwrite existing files.
- Produce `RECONNAISSANCE.md`, an implementation plan, risk list and proposed repo tree.

Gate: no product implementation changes until this report is complete and assumptions are recorded.

## Phase 1 — Research contract and data foundation

**Goal:** Lock down what can actually be measured.

Tasks:
- Confirm target units and business definitions with a small sample schema.
- Create dataset manifest and data dictionary implementation.
- Build validation for manual entry and CSV input.
- Add fictional platform labels and zone fixtures; make synthetic status visible.
- Create deterministic synthetic data generator only for UI/engineering tests, not empirical research conclusions.

Gate: every row has units, timestamp rules and source provenance; tests prevent target confusion.

## Phase 2 — Local-first vertical slice

**Goal:** Demonstrate one reliable worker journey.

Tasks:
- Minimal API and local database.
- Add session, delivery and expense records.
- Compute gross/net and online time with tests.
- Expose dashboard summary and earnings history.
- Add responsive overview and earnings screens.

Gate: end-to-end journey works with seeded fictional data and no hosted dependency.

## Phase 3 — Earnings modelling

**Goal:** Compare an honest earnings baseline with a feature-based model.

Tasks:
- Build feature pipeline using only information available at prediction time.
- Start with historical mean/median and seasonal/regularized baselines.
- Evaluate a small tree-based model if sample size supports it.
- Add rolling-origin/chronological backtests and uncertainty evaluation.
- Register model metadata and limitations.

Gate: model must beat the selected baseline on held-out chronological evaluation to be promoted; otherwise keep the baseline.

## Phase 4 — Zone/time demand forecasting

**Goal:** Forecast the exact available zone target.

Tasks:
- Inspect coverage, zone density, time granularity and target validity.
- Establish seasonal naive/statistical baseline.
- Evaluate feature-based models with time and zone features.
- Add weather/events only when reliable, licensed and cached with provenance.
- Build zone map/list visualisation with sample coverage overlay.

Gate: label is explicitly `requested_orders`, `completed_orders`, `observed_deliveries` or `proxy`; do not claim the wrong one.

## Phase 5 — Opportunity recommendation engine

**Goal:** Rank a small set of explainable choices.

Tasks:
- Define candidate set and hard eligibility filters.
- Combine expected net/hour, travel/time burden, uncertainty and worker preferences.
- Return score components and exclusion reasons.
- Test scenarios for missing data, uncertainty, tie and infeasible constraints.

Gate: deterministic, explainable, opt-in; does not accept or dispatch work.

## Phase 6 — Product polish and model transparency

**Goal:** Make the experience trustworthy and presentation-ready.

Tasks:
- Implement Model Lab and model status registry.
- Add provenance labels, freshness, uncertainty, coverage and limitations.
- Complete keyboard, responsive and accessibility checks.
- Apply UI/UX Pro Max / Impeccable direction and review all React components.

Gate: no synthetic or proxy output is shown without a clear label.

## Phase 7 — Security, privacy and deployment readiness

**Goal:** Make the selected deployment model safe.

Tasks:
- Choose local-only demo vs authenticated hosted mode.
- Add owner scoping, auth and RLS if Supabase is selected.
- Test CSV abuse, IDOR, secrets, rate limits, export/delete and logs.
- Review legal/terms and licence constraints for every external data source.
- Add backups and recovery only when there is a real persistent hosted service.

Gate: no unresolved critical/high issue for external user pilot; privacy notice and deletion process reviewed.

## Phase 8 — Research and academic submission

**Goal:** Turn implementation and evaluation into defensible evidence.

Tasks:
- Freeze dataset snapshot and experiment manifests.
- Complete related work and methodology.
- Report model results against baselines with proper test windows and uncertainty.
- Produce diagrams, architecture decision records, limitations, ethics and reproducibility appendix.
- Prepare live demo and viva walkthrough.

Gate: all quantitative claims trace to reproducible experiment evidence; no synthetic result is represented as field evidence.

## Phase 9 — Optional extensions (only after core gates)

Possible extensions:
- Graph-based spatial models if there are enough zones and consistent spatial labels.
- Temporal attention/transformer forecasting if data volume and baseline results justify complexity.
- Probabilistic or quantile models for well-calibrated uncertainty.
- Additional platform import formats where the user is authorized to export them.
- External weather/event adapters after licence, terms, latency and caching review.
- PWA/mobile client only if the web MVP reveals a real need.

## Weekly execution rhythm

1. Start with current git status and last accepted evidence.
2. Select one small vertical slice.
3. Read relevant skills/docs; do not load the entire skill catalog indiscriminately.
4. Write tests/acceptance criteria before implementation.
5. Implement the smallest correct change.
6. Run focused tests then regression tests.
7. Inspect UI in a real browser for user-facing changes.
8. Update docs/decision records and report exact commands/results.

## Release states

- `prototype`: synthetic/local only; not for real-world claims.
- `research_candidate`: real/credible dataset available, baseline and temporal evaluation underway.
- `validated_research`: result reproduced and supported by documented evaluation.
- `pilot_candidate`: privacy/security/consent operational gates reviewed.
- `released`: deployment and monitoring gates passed.

A release label must reflect evidence, not ambition.
