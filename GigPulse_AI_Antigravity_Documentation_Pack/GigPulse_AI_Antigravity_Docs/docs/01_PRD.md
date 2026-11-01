# 01 — Product Requirements Document (PRD)

**Product:** GigPulse AI · **Version:** 1.0 · **Status:** Proposed baseline; validate assumptions with a small number of target users before finalizing.

## 1. Product summary

GigPulse AI helps a delivery partner understand historical performance and estimate future earning opportunities across configurable platforms and urban zones. It combines earnings analytics, short-horizon demand forecasting and a transparent recommendation engine.

The application must distinguish:

- **Earnings prediction:** estimated payout or net earnings for a worker/shift/platform/zone/time context.
- **Demand forecast:** expected count of delivery events for a zone and time bucket, requiring a defined demand label and coverage.
- **Recommendation:** ranking of feasible choices using predictions, costs, uncertainty and preferences. It is not a prediction of a guaranteed order.

## 2. User personas

### Persona A — Multi-platform delivery partner

- Uses more than one delivery app over a week.
- Wants to compare net earnings, not only gross payouts.
- May record shifts, orders, online time, expenses and zones manually or through exports.
- Needs a simple answer: “Which of my feasible options looks better for the next time window, and why?”

### Persona B — Research evaluator

- Wants to inspect data provenance, features, model baselines, metrics and limitations.
- Needs reproducible experiments and evidence that synthetic data is not passed off as real.

### Persona C — Project administrator (later hosted mode)

- Manages service configuration and model versions.
- Must not see a worker's private records unless explicitly authorized for a documented research purpose.

## 3. Primary jobs-to-be-done

- Understand how much I earned after expenses over a selected day/week/month.
- Compare platforms on a consistent time basis.
- See forecasted earning ranges for an upcoming time window.
- See which zones may have more observed/estimated demand.
- Compare a few possible platform-zone-time choices within my travel and safety preferences.
- Understand the assumptions, sample coverage and uncertainty behind each recommendation.

## 4. Functional requirements

Priority legend: **P0** required for MVP, **P1** valuable next, **P2** research extension.

| ID | Requirement | Priority | Acceptance criteria |
|---|---|---:|---|
| FR-01 | Local/demo workspace | P0 | App can run locally without a paid service; demo mode clearly labels all seeded records. |
| FR-02 | Platform profiles | P0 | User can create, edit and archive platform labels; no platform login or credentials are collected. |
| FR-03 | CSV import preview | P0 | User can upload a supported CSV, map columns, preview rows and see row-level validation errors before commit. |
| FR-04 | Data provenance | P0 | Imported rows record source type, import batch and synthetic/proxy status where applicable. |
| FR-05 | Shift and order ledger | P0 | User can filter shifts/orders by date, platform and zone; timestamps and INR values are validated. |
| FR-06 | Expense tracking | P0 | Fuel/charging, maintenance, tolls, parking and other allowed categories can be recorded; totals are visible. |
| FR-07 | Earnings analytics | P0 | Dashboard shows gross, expenses, net and clearly defined earnings-rate denominators. |
| FR-08 | Earnings forecast | P0 | Forecast endpoint returns point estimate, interval, horizon, model version and data-coverage status. |
| FR-09 | Demand forecast | P0* | With valid zone-demand labels, forecasts counts by zone/interval; otherwise show “insufficient measured demand data” or a clearly labelled proxy/demo forecast. |
| FR-10 | Zone visualization | P0 | Zone map/heatmap identifies forecast horizon, source type, cell resolution and stale/missing cells. |
| FR-11 | Recommendation preview | P0 | Ranks only candidate options meeting worker constraints; displays expected net/hour, range, travel estimate/source and reasons. |
| FR-12 | Worker preferences | P0 | User can set max travel distance/time, preferred platforms, work hours, excluded zones and risk preference. |
| FR-13 | Explainability | P0 | Each prediction/recommendation shows top contributing factors or rules, with a caveat that explanations are not causal claims. |
| FR-14 | Model evaluation view | P1 | Shows baseline vs model metrics, evaluation period, sample count and model version. |
| FR-15 | Forecast backtesting | P1 | A historical date can be replayed using only data available at that time. |
| FR-16 | Data export/delete | P1 | User can export own records and delete own data according to retention policy. |
| FR-17 | Multi-user authentication | P1 | Hosted mode uses secure authentication and enforced per-user isolation. |
| FR-18 | Weather enrichment | P1 | Weather observations/forecasts are cached, labelled by source and license; failure degrades gracefully. |
| FR-19 | Feedback capture | P2 | User can record whether a suggestion was useful and later enter observed outcomes; no location tracking by default. |
| FR-20 | Advanced spatio-temporal model | P2 | GNN/transformer or other advanced model is evaluated only after data volume and baselines justify it. |

`FR-09` is conditional by design: actual demand prediction cannot be validated without an appropriate target dataset.

## 5. Core user journeys

### Journey 1 — First run with demo data

1. User opens the app and selects “Explore demo workspace”.
2. App loads a small deterministic synthetic dataset.
3. Persistent banner says “DEMO — synthetic records; not actual platform data”.
4. User opens dashboard, platform comparison, forecast and recommendation screens.
5. Every chart and card carries the same synthetic-data label.

### Journey 2 — Import personal history

1. User chooses CSV import and downloads a template.
2. User selects the platform profile and uploads the CSV.
3. App previews the file, detects columns and validates dates, statuses, numeric values and duplicates.
4. Invalid rows are rejected with actionable row numbers; valid rows can be committed.
5. The import batch and source provenance are stored.
6. Dashboard updates; records with insufficient online-time data are excluded from hourly earnings metrics and counted in a data-quality notice.

### Journey 3 — Compare platforms

1. User selects a date range and one or more platforms.
2. App reports gross payouts, incentives, tips, expenses and net payouts.
3. App distinguishes net per completed order, net per active hour and net per online hour.
4. If online time overlaps across apps, app avoids double-counting total wall-clock time and explains platform-specific vs combined denominator.

### Journey 4 — Ask for a recommendation

1. User chooses a future time window and sets constraints.
2. App generates feasible candidate platform-zone-time combinations.
3. Forecast service returns prediction intervals and coverage metadata.
4. Recommendation engine calculates a risk-adjusted score.
5. App displays ranked alternatives, reasons, uncertainty, data age and “not a guaranteed order/income” notice.
6. User remains in control; no third-party app is automated.

## 6. Dashboard information architecture

- **Overview:** net earnings, gross, expenses, trend, data health, next forecast snapshot.
- **Earnings:** platform and time comparisons, target vs actual, income composition.
- **Demand map:** zone-time demand forecast, observation coverage and horizon selector.
- **Opportunity planner:** candidate ranking, worker constraints, scenario comparison.
- **History:** shifts, deliveries, expenses and import batches.
- **Model lab:** baselines, errors, model versions, backtest and drift (research/admin access).
- **Settings & privacy:** platform labels, preferences, exports/deletion, data sources and consent.

## 7. Non-functional requirements

| ID | Requirement | Initial target / rule |
|---|---|---|
| NFR-01 | Performance | Target dashboard interaction under 2 s on a modest laptop for the MVP demo dataset; measure, do not assume. |
| NFR-02 | Responsive | Core workflows usable at 360 px viewport width and desktop. |
| NFR-03 | Accessibility | Keyboard navigation, visible focus, semantic controls, non-colour-only chart cues and WCAG 2.2 AA-oriented review. |
| NFR-04 | Reliability | Missing enrichment service must not break core ledger/analytics. |
| NFR-05 | Reproducibility | Deterministic demo seed, pinned dependency lockfiles and logged model/data versions. |
| NFR-06 | Security | Server-side input validation, per-user authorization, no secrets in source control or logs. |
| NFR-07 | Explainability | Every estimate provides horizon, unit, timestamp, model version, coverage and uncertainty state. |
| NFR-08 | Portability | Core project can run locally; cloud deployment is optional. |
| NFR-09 | Cost | No paid API/cloud dependency for MVP. External services are optional and current terms must be checked. |
| NFR-10 | Data minimization | Exact GPS is not stored by default; aggregate to configured H3 zone when location granularity is needed. |

## 8. Business and product rules

- Currency default: INR. Store money as integer paise, not floating-point rupees.
- Timezone default for the India pilot: `Asia/Kolkata`; store timestamps in UTC and render in the selected city timezone.
- No earnings metric is valid without its denominator and time window.
- Do not mix synthetic, proxy and observed records in a chart without a visible source legend/filter.
- Demand predictions may be displayed only with target definition and coverage metadata.
- When the model is stale, has low coverage or high uncertainty, use a warning or abstain instead of confidently ranking candidates.
- User-defined safety and availability constraints are hard constraints, not merely ranking preferences.
- The user can inspect factors and override/ignore recommendations.

## 9. MVP release gates

The MVP is not complete until it has: data import validation, ledger, expense-aware analytics, baseline earnings forecast, conditional demand forecast, recommendation explanation, data provenance labels, documented limitations, automated tests and a reproducible demo.
