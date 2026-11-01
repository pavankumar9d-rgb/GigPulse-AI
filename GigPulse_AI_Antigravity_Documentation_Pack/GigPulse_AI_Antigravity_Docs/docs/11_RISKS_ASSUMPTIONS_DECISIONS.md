# Risks, Assumptions, Open Questions and Architecture Decisions

## 1. Assumptions to validate

| ID | Assumption | Risk if false | Validation |
|---|---|---|---|
| A-01 | A worker can access and lawfully share a usable history export or manually enter a representative sample | Sparse or biased training data | Inspect real sample with consent; document source and omissions |
| A-02 | Platform labels can be normalized across differing payout schemas | Invalid comparison | Define per-platform mapping and reconcile a sample |
| A-03 | Expenses can be collected sufficiently to estimate net earnings | Net values are incomplete | Measure expense completeness; call result estimated net |
| A-04 | Zone/time observations are available at meaningful coverage | Demand forecast is not identifiable | Obtain aggregate data or narrow the target to a labelled proxy |
| A-05 | A web dashboard is suitable for first prototype | Mobile field use may be poor | Test at phone widths and with representative users |
| A-06 | The user can operate a local Python/Node stack | Environment may be constrained | Phase 0 environment check; use lightweight dependencies |
| A-07 | India/Hyderabad can be an initial example study context | Not all geography/data sources apply | Treat location as configurable, not hard-coded |

## 2. Primary risks

### R-01: Demand label ambiguity
**Risk:** Completed deliveries, observed deliveries and requested orders are different variables. A model trained on one cannot be marketed as predicting another.

**Mitigation:** `target_type` and `target_quality` are mandatory. UI and API return exact target labels. Obtain aggregate requested-order labels or explicitly narrow the claim.

### R-02: Selection and coverage bias
**Risk:** Participating workers/platform exports may omit unaccepted orders, idle periods, unavailable workers and non-participant zones.

**Mitigation:** Report coverage and sampling limitations; do not extrapolate to all platform demand without evidence.

### R-03: Sparse data and overfitting
**Risk:** Complex temporal/graph models may look impressive but generalize poorly.

**Mitigation:** Establish baselines, limit model complexity, use chronological validation, and retain a simpler model if it performs better.

### R-04: Earnings definition mismatch
**Risk:** Incentives, tips, refunds, reimbursements, fuel and overlapping sessions may be inconsistently reported.

**Mitigation:** Version metric definitions; display completeness; use integer paise and interval unions.

### R-05: Location privacy
**Risk:** Fine-grain time/location histories can expose home, routine or identity.

**Mitigation:** coarse zones, no live GPS in MVP, aggregation thresholds, access controls and deletion.

### R-06: Platform terms and data rights
**Risk:** Automated collection or misuse of platform exports violates terms or rights.

**Mitigation:** user-authorized exports/manual records only; review each platform's current terms before any connector.

### R-07: Misleading recommendations
**Risk:** User may treat estimates as guaranteed income or ignore costs/travel.

**Mitigation:** intervals, caveats, preference constraints, net estimate, explanation and opt-in user decision.

### R-08: External provider/licence changes
**Risk:** Weather/map APIs, hosting free tiers or model endpoints may alter quotas and terms.

**Mitigation:** optional adapters, caching, source registry, graceful disable path and re-check terms before release.

### R-09: Scope and hardware overload
**Risk:** Multiple frameworks, heavy model dependencies and advanced visuals overwhelm build and runtime.

**Mitigation:** modular monolith, small dependency set, no GPU assumption, model training as offline process, progressive enhancement.

## 3. Open questions (do not block Phase 0)

1. Will the first empirical dataset be from one worker, multiple volunteers, a public aggregate source, or a combination?
2. Which exact payout fields are included in gross earnings for each platform format?
3. Is requested-order demand label data obtainable, or will the first research target explicitly be observed/completed delivery activity?
4. Which zones and granularity can be ethically and statistically supported?
5. Is the deliverable only a local research demo, or will it be piloted with real users?
6. Which deployment is desired after the local demo: local-only, free-tier hosted, or institution-provided?

## 4. Architecture Decision Records

### ADR-001 — Modular monolith before microservices
**Status:** Accepted for MVP.

**Decision:** One web frontend, one API service and a modular Python ML package. Keep module boundaries clean; do not split into independently deployed services initially.

**Rationale:** Lower operational complexity, easier local execution, faster testing and sufficient scale for a student research prototype.

**Revisit when:** measured throughput, team boundaries or deployment needs justify service separation.

### ADR-002 — Separate earnings and demand tasks
**Status:** Accepted.

**Decision:** Different target definitions, feature contracts, models, metrics and output labels.

**Rationale:** Worker earnings and zone-level order demand are related but not interchangeable supervised-learning targets.

### ADR-003 — Local-first data store
**Status:** Accepted for prototype.

**Decision:** SQLite for a single-user local MVP; PostgreSQL for concurrent/hosted usage; Supabase is an optional managed Postgres/Auth choice, not a required dependency.

**Rationale:** Minimizes setup and cost while preserving a migration path.

### ADR-004 — No platform scraping
**Status:** Accepted.

**Decision:** Manual entry, user-authorized exports, open/public aggregate datasets with clear licensing, or explicitly synthetic examples only.

**Rationale:** Privacy, terms, legal and reliability constraints.

### ADR-005 — Baseline-first ML
**Status:** Accepted.

**Decision:** Seasonal naive/statistical and simple ML baselines precede GNN/transformer models.

**Rationale:** Advanced architecture is justified only by measurable improvement on credible chronological evaluation.

### ADR-006 — No automated work allocation
**Status:** Accepted.

**Decision:** Recommendation outputs are advisory, explainable and user-controlled. No automatic order acceptance, rejection or platform interaction.

**Rationale:** Preserves worker autonomy and bounds product risk.

### ADR-007 — Explicit synthetic-data separation
**Status:** Accepted.

**Decision:** Synthetic dataset has a distinct generator, manifest, banner and `source_type`; do not mix with empirical evaluation unless clearly isolated and labelled.

**Rationale:** Prevents demo convenience from contaminating research claims.
