# 02 — Research Methodology and Study Design

## 1. Research framing

**Research domain:** applied machine learning, spatio-temporal forecasting, gig-work analytics and constrained decision support.

**Research objective:** design and evaluate a reproducible framework for estimating worker-level earnings, forecasting zone-time delivery activity where suitable observations exist, and ranking feasible work opportunities under cost, uncertainty and worker preferences.

## 2. Research questions

- **RQ1:** Do temporal, platform, zone and contextual features improve earnings prediction compared with simple historical/seasonal baselines?
- **RQ2:** When valid zone-level demand observations are available, do spatial-neighbour and temporal features improve short-horizon demand forecasts compared with per-zone seasonal baselines?
- **RQ3:** Does a transparent risk-aware ranking produce more useful retrospective choices than ranking by point-estimated gross payout alone?
- **RQ4:** How do missing online-time records, incomplete zone coverage, sparse platform history and source bias affect reliability?

## 3. Hypotheses (to be tested)

- **H1:** A regularized tree-based model with temporal/platform/zone features will reduce chronological test MAE versus a seasonal-naive earnings baseline, subject to sufficient data.
- **H2:** Zone-neighbour and calendar-lag features will reduce demand forecast error versus a per-zone seasonal-naive baseline where demand labels have adequate coverage.
- **H3:** Ranking by estimated net earnings with a penalty for uncertainty/travel cost will produce fewer high-risk recommendations than ranking by gross payout alone.

A hypothesis is not a result. Report it as unsupported when measured evidence does not support it.

## 4. Study setting and unit of analysis

- **Initial geography:** a configurable Indian city; Hyderabad may be selected as a demonstration setting if the project team obtains or constructs defensible zone data. Do not hardcode personal home coordinates.
- **Spatial unit:** H3 cell or documented operational zone. Record the H3 resolution and do not compare results across resolutions without adjustment.
- **Temporal unit:** start with hourly buckets; optionally compare 30-minute and 2-hour aggregation if sufficient data exists.
- **Earnings unit:** one worker-shift-platform record, or a well-defined worker-platform-time interval.
- **Demand unit:** one zone-time bucket with an explicitly measured order count and source coverage.
- **Recommendation unit:** one candidate tuple `(platform, zone, start_time, forecast_horizon)`.

## 5. Data availability and validity strategy

### Tier A — Real, permissioned worker records

- Voluntary CSV/manual exports provided by the worker.
- Store only fields necessary for the stated purpose.
- Capture consent, source, import timestamp and allowed use.
- Personal completed deliveries are valid observations of that worker's outcomes, but are not a complete city-wide demand census.

### Tier B — Aggregate zone demand labels

Preferred for demand modelling. Examples include a properly licensed dataset containing timestamped order counts by zone, research-partner data, or multi-participant records with a documented coverage fraction and safe aggregation threshold.

### Tier C — Proxy observations

Potentially useful context includes restaurant/merchant activity proxies, public events or mobility indicators. These are not automatically order-demand labels. Use a separate `proxy_demand` target and never relabel it as actual orders.

### Tier D — Synthetic data

Use for interface development, pipeline tests and demonstration. Mark every row and derived output as synthetic. Do not use synthetic-only results as evidence of real-world predictive performance.

### Crucial identifiability limitation

If the only data source is one rider's completed orders, unobserved orders, rejected offers, platform allocation logic, orders completed by other riders and orders not accepted are missing. The project can forecast **that rider's observed delivery activity** or a proxy, but cannot honestly claim to forecast total zone demand. To study city-level demand, secure suitable aggregated demand labels or redesign the claim.

## 6. Data collection protocol

1. Define exact target, units, spatial resolution and time interval before collecting data.
2. Prepare templates and a data dictionary before importing.
3. Obtain informed voluntary participation and document purpose, retention, deletion and access.
4. Pseudonymize participant IDs; keep any identity mapping separately and preferably not at all.
5. Do not collect platform passwords, OTPs, cookies or app-session data.
6. Record provenance, import batch, license and missingness.
7. Store timestamps in UTC; preserve original timezone metadata if supplied.
8. Perform quality checks before feature engineering.
9. Freeze train/validation/test date boundaries before model comparison.
10. Preserve a clean holdout set until model selection is complete.

## 7. Experimental design

### Baselines

- Earnings: global median, platform median, platform-zone-hour median, rolling/seasonal median.
- Demand: last bucket, same hour previous day, same hour previous week, zone-specific moving average.
- Ranking: gross payout per hour; net point-estimate per hour; proposed risk-adjusted score.

### Candidate models

- Earnings: regularized linear regression, Random Forest/Extra Trees, HistGradientBoosting, LightGBM or CatBoost after compatibility/size review.
- Demand: seasonal baselines, Poisson/negative-binomial regression where count assumptions fit, gradient-boosted trees with lag/neighbor features.
- Advanced research: graph neural network plus temporal encoder, Temporal Fusion Transformer or a comparable model only when data size, spatial graph and compute budget justify it.

### Splitting strategy

- Use a chronological split, never random row splitting as the primary reported evaluation.
- Example design: earliest 70% dates for training, next 15% for validation, latest 15% for final test. Adjust only before seeing final test results and record why.
- If multiple workers contribute, add a worker-held-out evaluation to test generalization to unseen workers.
- Add a zone-held-out stress test if deployment must work in new zones.
- Build lags and rolling features using past values only. Fit imputers, encoders and scalers on training data only.

### Ablation studies

Compare: (a) temporal only; (b) temporal + platform; (c) + zone; (d) + weather/calendar; (e) + neighbour features. Add one feature group at a time and report changes on the same test window.

## 8. Outcome measures

### Earnings

- MAE in INR/hour or INR/shift (state which).
- RMSE in the same unit.
- Median absolute error for robustness to outliers.
- WAPE only when the denominator (sum of actual absolute values) is non-zero and interpretation is appropriate.
- Quantile pinball loss for Q10/Q50/Q90.
- Prediction-interval coverage and interval width.

### Demand

- MAE/RMSE in orders per zone per bucket.
- WAPE where meaningful; use caution for sparse/zero-heavy zones.
- Pinball loss for count quantiles.
- Error by zone, hour, weekday/weekend and coverage tier.
- Baseline-relative improvement.

### Recommendation engine

Offline replay is not a causal field experiment. Report ranking stability, constraint satisfaction, low-confidence abstention rate and retrospective utility proxy. Do not claim that recommendations increase actual income unless a prospective, appropriately designed study measures that outcome.

## 9. Bias, confounding and limitations

- Completed deliveries are selected by platform allocation and worker acceptance behaviour.
- Incentives, payout rules and platform policies can change abruptly.
- One worker's travel radius and shifts may not generalize to others.
- Weather and events can correlate with demand but not prove causation.
- Device clock errors, missing online minutes and delayed payouts distort hourly estimates.
- Demand labels may have uneven coverage across zones and time.
- A high-activity zone may also have more competing riders, longer queues or worse traffic.
- External map/weather data can be stale, licensed differently or unavailable.

## 10. Reproducibility checklist

- [ ] Dataset manifest with source/license, extraction date, row count and synthetic/proxy/observed label.
- [ ] Data-quality report and exclusion log.
- [ ] Fixed random seeds and dependency lockfiles.
- [ ] Frozen time-based split boundaries.
- [ ] Baseline results before advanced models.
- [ ] Model parameters and feature list recorded.
- [ ] Per-segment results, not only one aggregate metric.
- [ ] Model card with intended use, limits and known failure modes.
- [ ] Results generated from scripts, not manually typed into the report.

## 11. Defensible claims

Allowed: “On this dataset and chronological test interval, model X achieved metric Y and exceeded baseline Z by N%.”

Not allowed without evidence: “The system predicts all delivery demand in Hyderabad”, “the AI guarantees the highest income”, “the model increases rider income by 30%”, or “the system knows live platform order volume”.
