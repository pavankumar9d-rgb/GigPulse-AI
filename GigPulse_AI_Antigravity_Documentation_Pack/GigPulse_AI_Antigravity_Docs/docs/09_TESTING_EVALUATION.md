# Testing, Validation and Evaluation Plan

## 1. Quality strategy

Test the data contract, business calculations, ML validity, API, UI, security and research claims independently. Passing a frontend demo is not evidence that a model works. Passing a model notebook is not evidence that the product handles user data safely.

## 2. Test layers

### Unit tests
- Money calculations use integer paise and handle rounding/display explicitly.
- Gross/net definitions and included payout components are consistent.
- Overlapping work-session intervals are unioned before total online time is computed.
- Timezone conversions, daylight/time boundaries and interval bucketing are correct.
- Zone mapping and H3 resolution checks are deterministic.
- Demand target type and source quality are preserved end-to-end.
- Recommendation score components and hard constraints are independently tested.

### Data tests
- Required columns, allowed values, ranges, null rules and uniqueness.
- Duplicate imports, malformed timestamps, timezone-naive values, impossible durations and negative amounts.
- Target-source consistency: requested-order labels cannot be manufactured from completed deliveries.
- Missingness, coverage and sample composition reports.
- Train/test temporal boundaries and feature availability timestamps.

### ML tests
- Baseline is trained and evaluated before complex models.
- Chronological backtest with a holdout period never used for model or feature selection.
- No random row split for primary time-series claim.
- Leakage tests: features timestamped after forecast origin must be rejected.
- Compare against naive seasonal and simple statistical baselines.
- Earnings: MAE, RMSE, WAPE or MASE where denominator is valid; R² only as secondary context.
- Demand counts: MAE/RMSE, WAPE where valid, Poisson deviance for count models where appropriate; zero-heavy and low-coverage segments reported.
- Prediction intervals: empirical coverage and interval width by horizon/segment.
- Calibration and error drift assessed across rolling temporal windows.
- Model artifact, code revision, feature schema, seed and dataset manifest recorded.

### API/integration tests
- Request/response schema, auth, object ownership, error codes and pagination.
- CSV validation does not write committed rows; commit is explicit and idempotent.
- A user cannot read another user's sessions, records, forecast or exports.
- Forecast endpoint response includes model version, target type, unit and data-quality metadata.
- Missing model/data returns a controlled “insufficient data” response, not a fabricated prediction.

### UI/E2E tests
- Primary flows: demo login/profile, add history manually, CSV validate, preview, commit, view metrics, inspect forecast, compare options, export/delete.
- Check loading, empty, error, stale-data and synthetic-demo states.
- Verify chart tooltips, table alternative, responsive layouts and keyboard navigation.
- Verify demo banner persists on all views using synthetic data.

### Security tests
- IDOR and RLS negative tests.
- SQL injection and CSV formula-injection cases.
- Oversized file, malformed CSV and invalid JSON payloads.
- Secret scanning and dependency scan.
- Export and deletion authorization tests.

## 3. Research evaluation protocol

1. Freeze target definitions and dataset version before model comparison.
2. Choose chronological train/validation/test windows (for example, earlier weeks for train, later weeks for validation, final weeks for test; choose actual windows after data inspection).
3. Perform all preprocessing fit steps on training data only.
4. Tune on validation only; do not repeatedly inspect final test results.
5. Compare baseline, feature-based ML and any advanced model on the identical test windows.
6. Report metric values with sample size, target, unit, time horizon, aggregation and segment.
7. Report confidence intervals or bootstrap variability where feasible.
8. Record failed experiments and negative findings.
9. Repeat key results with a pinned environment and saved data manifest.

## 4. Suggested minimum acceptance gates

These are project gates, not guaranteed outcomes:

- Data: all target rows have valid timestamps, units and provenance; invalid or proxy targets are not silently relabelled.
- Baseline: a reproducible baseline exists for each forecast target before a complex model is accepted.
- Model: proposed model beats an appropriate baseline on a held-out chronological test for the primary metric, without materially worsening critical segments; if it does not, retain baseline and report the negative result.
- Uncertainty: interval coverage is measured before displaying prediction intervals as meaningful.
- Product: every displayed forecast exposes target, unit, horizon, model status and source quality.
- Security: no unresolved critical/high severity issue before external user testing.
- Accessibility: no known blocking keyboard or screen-reader issue in core user journeys.
- Reproducibility: each reported metric maps to code revision, dataset manifest and model artifact.

## 5. Experiment record template

```yaml
experiment_id: EXP-0001
question: "Does model B improve zone-level demand forecasting over seasonal naive?"
target: observed_deliveries
unit: deliveries_per_30min
zone_resolution: "document chosen resolution"
data_manifest: "sha256-or-versioned-reference"
feature_schema: "v1"
train_window: "TBD after dataset inspection"
validation_window: "TBD after dataset inspection"
test_window: "TBD after dataset inspection"
baseline: seasonal_naive
candidate: gradient_boosting
metrics: [MAE, RMSE, WAPE_if_valid]
seed: 42
code_revision: "git commit"
result: pending
limitations: []
```

## 6. Reporting rule

Never write “high accuracy”, “real-time accurate”, “improves earnings” or any percentage improvement unless the experiment record and held-out evidence support that exact claim. In the absence of credible data, report software functionality and synthetic demonstration separately from research performance.
