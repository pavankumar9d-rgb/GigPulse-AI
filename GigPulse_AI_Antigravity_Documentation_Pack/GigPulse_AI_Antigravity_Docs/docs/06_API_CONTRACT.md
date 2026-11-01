# API Contract (Proposed v1)

**Status:** Contract proposal. The implementation and generated OpenAPI document must be treated as authoritative after they exist.

## 1. API conventions

- Base path: `/api/v1`.
- JSON request and response bodies; UTF-8.
- Timestamps are ISO 8601 with timezone offsets; persist UTC.
- Money is represented as integer minor units with currency code, not decimal floats.
- Every prediction returns its target definition, unit, horizon, model version, training data reference/quality summary, and uncertainty fields when supported.
- Pagination uses `limit` and opaque `cursor`; impose a safe maximum.
- Use stable machine-readable `code` values in errors; human `message` is explanatory only.
- Validate all request inputs. Use parameterized SQL. Apply rate limits and payload/file-size limits.
- Private resources require authentication and ownership checks. Local demo mode may use a clearly labelled local profile.

## 2. Standard error shape

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The interval end must be after the start.",
    "request_id": "req_example",
    "details": [{"field": "ended_at", "reason": "must_be_after_started_at"}]
  }
}
```

Never return stack traces, SQL text, secrets, internal paths, or raw uploaded records in errors.

## 3. Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Liveness/readiness status, no secrets |
| GET | `/dashboard/summary` | Aggregated worker summary for a selected time range |
| GET/POST | `/platforms` | List and add platform labels |
| GET/POST | `/sessions` | Read/create declared work sessions |
| GET/POST | `/deliveries` | Read/create delivery records |
| GET/POST | `/expenses` | Read/create expense records |
| POST | `/imports/validate` | Upload CSV for validation; no rows committed |
| POST | `/imports/{id}/commit` | Commit accepted rows after user review and explicit action |
| GET | `/imports/{id}/report` | Retrieve validation/commit report |
| GET | `/earnings/history` | Historical gross/net aggregation |
| POST | `/forecasts/earnings` | Earnings prediction for a worker/time window |
| POST | `/forecasts/demand` | Zone-level demand/proxy forecast |
| POST | `/recommendations/preview` | Rank candidate platform-zone-time choices |
| GET | `/models` | Model registry and evaluation summaries |
| GET | `/models/{id}` | Model details, limitations and metrics |
| POST | `/data/export` | Build an owner-scoped export |
| DELETE | `/account/data` | Delete data owned by the authenticated user, subject to explicit confirmation/workflow |

## 4. Request examples

### Earnings forecast

```json
{
  "worker_id": "uuid",
  "platform_id": "uuid",
  "zone_id": "uuid",
  "start_at": "2026-11-02T08:00:00+05:30",
  "end_at": "2026-11-02T12:00:00+05:30",
  "prediction_unit": "INR_PER_ONLINE_HOUR",
  "include_interval": true
}
```

### Demand forecast

```json
{
  "zone_ids": ["uuid-a", "uuid-b"],
  "forecast_from": "2026-11-02T08:00:00+05:30",
  "steps": 8,
  "interval_minutes": 30,
  "target_type": "observed_deliveries",
  "include_interval": true
}
```

The target type must be one the selected dataset and model were trained to predict. Do not allow a model trained on `observed_deliveries` to be described as predicting total `requested_orders`.

### Recommendation preview

```json
{
  "worker_id": "uuid",
  "candidate_zone_ids": ["uuid-a", "uuid-b"],
  "candidate_platform_ids": ["uuid-x", "uuid-y"],
  "time_window": {
    "start_at": "2026-11-02T18:00:00+05:30",
    "end_at": "2026-11-02T21:00:00+05:30"
  },
  "preferences": {
    "min_net_earnings_paise_per_hour": 0,
    "max_travel_distance_m": 5000,
    "risk_tolerance": "balanced",
    "exclude_platform_ids": []
  }
}
```

## 5. Prediction response envelope

```json
{
  "run_id": "uuid",
  "target": {
    "name": "net_earnings_per_online_hour",
    "unit": "INR/hour",
    "definition_version": "1.0",
    "source_quality": "user_reported_and_synthetic_demo"
  },
  "forecast": {
    "point": 118.5,
    "lower": 91.0,
    "upper": 143.0,
    "interval_level": 0.8
  },
  "horizon": {
    "start_at": "2026-11-02T18:00:00+05:30",
    "end_at": "2026-11-02T21:00:00+05:30"
  },
  "model": {
    "name": "baseline_hurdle_ridge",
    "version": "0.1.0",
    "status": "experimental"
  },
  "evidence": {
    "training_rows": 0,
    "last_training_at": null,
    "backtest_mae": null,
    "coverage_note": "Illustrative response only; no measured model performance is asserted."
  },
  "limitations": ["Demo values must be replaced by a valid trained model output."]
}
```

The numeric values above are example placeholders, not expected performance or a real prediction.

## 6. Import validation contract

`POST /imports/validate` should return:
- detected file type, mapped columns and mapping confidence;
- total, accepted, rejected and duplicate candidate row counts;
- per-column parse errors and row-level error samples (redacted);
- warnings for missing timestamps, timezones, units, zone identifiers, payout definition and source provenance;
- an explicit statement that nothing is committed yet.

The commit endpoint must be idempotent or guarded by a one-time commit token, require authenticated ownership, and record the transform version and source hash.

## 7. Recommendation response requirements

For every candidate return:
- eligibility and exclusion reasons;
- predicted gross/net earnings, cost estimate and uncertainty where available;
- demand target/source quality and forecast horizon;
- estimated travel distance/time and source;
- component scores and scoring version;
- a warning when any key input is missing, stale or proxy-derived.

Never claim “best platform” as a universal fact. Phrase the output as “highest estimated score under the selected constraints”. User remains in control.

## 8. Contract tests

- Validate schema, units, timezones, ranges, ownership, pagination and stable error codes.
- Verify that importing the same file twice does not duplicate committed records.
- Verify that a proxy-trained model cannot return a requested-orders target label.
- Verify forecast output is reproducible for a pinned model and feature snapshot.
- Generate an OpenAPI spec and fail CI on unreviewed breaking contract changes.
