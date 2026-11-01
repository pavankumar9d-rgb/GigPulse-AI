# 04 — Machine-Learning and Optimization Design

## 1. Two distinct prediction problems

Do not train one opaque model to output “best earning zone”. Build and evaluate separate prediction targets, then combine their outputs in a transparent decision layer.

### A. Earnings prediction

**Proposed target:** `net_earnings_paise_per_online_hour` for a defined worker-platform-zone-time context. Also report shift-level net payout and order-level payout where available.

The target must be calculated only when its components and denominator are observed. If online minutes are unavailable, do not fabricate a per-online-hour label. Use a narrower target such as per-completed-order payout or per-observed-active-hour and label it correctly.

Definitions:

- `gross_payout_paise = base_payout + incentive + tip + other documented credits`.
- `net_payout_paise = gross_payout_paise - attributable_operating_expenses`.
- `net_per_online_hour = net_payout_paise / observed_online_hours`.
- `net_per_active_hour = net_payout_paise / observed_active_hours`.

Expense allocation (fuel, maintenance) must be explicit and consistent. For costs shared across platforms, allocate by a documented rule such as attributable distance or time; retain the original expense and allocation method. Avoid double subtraction.

### B. Zone demand forecasting

**Proposed target:** count of delivery orders/events in `zone_id × bucket_start × bucket_duration`, with source and coverage fields.

Target types (stored in `zone_demand_observations.target_type`) are `requested_orders`, `completed_orders`, `observed_deliveries` or `proxy`. The separate `target_quality` field records whether the row is `verified_aggregate`, `user_reported`, `proxy` or `synthetic`. A multi-participant aggregate may be marked `user_reported` or `verified_aggregate` only when its source and coverage are documented. Never use a target-quality label to conceal what the target actually measures.

A single worker's completed deliveries must not be treated as total zone demand.

## 2. Feature engineering

### Temporal features

- Local hour, day-of-week, weekend flag, month/season and public-holiday/event flag where correctly sourced.
- Cyclical encodings for hour and weekday if useful.
- Lagged outcomes (1, 2, 3, 6, 12, 24, 168 buckets as supported by interval/data length).
- Rolling mean/median/count and dispersion using past-only windows.
- Time since last observed activity and missingness flags.

### Spatial features

- H3 cell and resolution; neighboring cell features.
- Distance/travel-time estimates only from a validated source; otherwise label as approximate.
- Historical zone baseline and cross-zone activity summaries.
- Zone attributes derived from permitted, documented geospatial data.

### Platform and worker context

- Platform category/identifier (categorical, not a secret integration).
- Vehicle type and worker preferences only when volunteered and necessary.
- Historical worker/platform relationship and sparse-history flag.
- Shift duration and online/active time only when known at prediction time.

### External context

- Weather (temperature, precipitation, wind) with observation/forecast distinction and timestamp.
- Events/holidays with source and time validity.
- Traffic/travel time only when a permitted, documented provider is available.

Do not use sensitive personal attributes or future-known outcomes. Avoid raw exact GPS coordinates as default model features; aggregate to H3 cells.

## 3. Leakage controls

- Every training row has a `prediction_cutoff_at`.
- Feature generation uses only records with timestamps <= cutoff and data available at cutoff.
- Incentives, final payout, delivery duration, actual expense and completed status are targets/outcomes, not predictors for a forecast made before the shift.
- Weather forecast features must be the forecast that was available at prediction time, not later observed weather, when evaluating future prediction.
- Split by time before creating learned transformations. Fit encoders, scalers and imputers on training only.
- Do not calculate rolling values across train/test boundaries without a realistic past-only state mechanism.
- Deduplicate delivery and expense records before aggregation.

## 4. Baseline-first model ladder

### Earnings

1. Global median baseline.
2. Platform median baseline.
3. Platform + zone + local hour/day-of-week median baseline.
4. Regularized linear regression / ElasticNet.
5. Random Forest or HistGradientBoosting.
6. LightGBM/CatBoost after environment and package review.
7. Quantile models for Q10/Q50/Q90, or calibrated residual intervals.

### Demand

1. Last-bucket / seasonal-naive baseline.
2. Same hour previous day/week.
3. Zone-specific rolling mean/median.
4. Poisson/negative-binomial GLM where appropriate.
5. Gradient-boosted count/regression model with lag, weather and neighbour features.
6. Spatio-temporal GNN/temporal transformer only as a research extension after data volume, graph definition and compute feasibility are established.

Use the simplest model that demonstrates a stable, repeatable improvement. A complex architecture is not automatically a stronger project.

## 5. Forecast horizons and output contract

Initial horizons: next 1 hour, 3 hours and 6 hours (configurable). Do not display unsupported long-range forecasts.

Each prediction must include:

```json
{
  "target": "net_earnings_paise_per_online_hour",
  "unit": "INR/hour",
  "q10": 0,
  "q50": 0,
  "q90": 0,
  "horizon_start": "ISO-8601 timestamp",
  "horizon_end": "ISO-8601 timestamp",
  "model_version": "model-id",
  "data_cutoff_at": "ISO-8601 timestamp",
  "source_class": "observed|proxy|synthetic|mixed",
  "coverage_level": "high|medium|low|insufficient",
  "sample_count": 0,
  "generated_at": "ISO-8601 timestamp"
}
```

Values above are schema examples only, not model results.

## 6. Evaluation protocol

- Primary split: chronological train/validation/test.
- Secondary checks: worker-held-out and zone-held-out where data permits.
- Report MAE and RMSE; add pinball loss and interval coverage for quantiles.
- For zero-heavy demand, report MAE and baseline-relative error; explain limitations of percentage metrics.
- Include per-platform, per-zone, hour, weekday/weekend and sample-size breakdowns.
- Compare each model to the correct baseline on the same test dates.
- Backtest with realistic forecast cutoffs.
- Save evaluation output to machine-readable JSON/CSV and generate plots from it.

## 7. Uncertainty and abstention

Use quantile estimates or calibrated prediction intervals. Show Q10/Q50/Q90 (or another justified interval), sample count and model-data freshness. Define an abstention rule before user testing, e.g. insufficient history, unseen platform-zone segment, stale context or interval width above a calibrated threshold. An abstained forecast is preferable to a misleadingly precise number.

## 8. Recommendation/optimization engine

### Candidate representation

`candidate = (platform_id, zone_id, start_time, end_time)`.

### Hard constraints

- User-enabled platforms only.
- User-configured working hours and shift length.
- Maximum travel distance/time.
- Excluded zones and user-defined safety constraints.
- Required vehicle or platform eligibility if known.
- No candidate requiring an unsupported route, unsafe instruction or hidden platform action.

### Risk-aware score

For feasible candidates only, start with a transparent score such as:

`score = predicted_net_inr_per_hour_q50 - risk_weight × uncertainty_penalty - travel_penalty`

where:

- `uncertainty_penalty` is derived from interval width or calibrated downside risk;
- `travel_penalty` is a documented conversion of estimated travel time/cost into the same utility scale;
- all coefficients are configurable and shown as assumptions.

Do not subtract travel cost twice: if the earnings target already includes the same travel expense, the ranking must not apply it again. Do not compare estimates with different denominators.

Display score components, Q10/Q50/Q90, source coverage and reasons. A high score is an estimate, not a guarantee of order allocation or income.

### Optimization extensions

- Multi-objective Pareto ranking (earnings, travel time, uncertainty, personal preference) can be assessed with `pymoo` if the simple ranker is insufficient.
- Reinforcement learning/contextual bandits are out of MVP scope because unbiased exploration, consent, safety and logged feedback are not yet established.

## 9. Explainability

- Tree models: SHAP or model-specific feature contribution summaries after checking runtime cost.
- Baseline/rule models: direct reason codes.
- Explain “associated with the estimate”, not “causes higher demand”.
- Never expose another worker's private records to explain an individual result.

## 10. Model monitoring

Store: model ID, model code commit, training data manifest/hash, feature schema version, train/validation/test interval, evaluation metrics, generation timestamp and active status.

Monitor input feature distribution drift, missingness and out-of-range inputs, rolling forecast error once actual outcomes arrive, interval coverage and calibration, performance by zone/platform segment, abstention rate and stale-source rate.

Do not auto-promote a model solely because a single aggregate metric improved. Require the same evaluation protocol and review known failure modes.

## 11. Model card checklist

- Intended use and prohibited use.
- Target definition and unit.
- Training data source/type, dates, row count and coverage.
- Feature groups and unavailable-at-prediction-time exclusions.
- Baseline and candidate metrics.
- Interval calibration and subgroup errors.
- Known bias, missingness and failure modes.
- Version and reproducibility instructions.
- Approval/status: experimental, evaluation-ready or selected for demo.
