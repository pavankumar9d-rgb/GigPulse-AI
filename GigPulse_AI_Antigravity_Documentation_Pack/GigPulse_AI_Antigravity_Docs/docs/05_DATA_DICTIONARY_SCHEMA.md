# Data Dictionary and Database Schema

**Status:** Proposed v1; confirm against the implemented migrations before claiming it exists.

## 1. Data conventions

- Store money as integer minor units: INR paise (`amount_paise`). Convert to rupees only for display (`₹{paise / 100}`). Never use binary floating point for authoritative money arithmetic.
- Store instants as UTC timestamps (`timestamptz` in PostgreSQL); retain the source timezone and original local date where necessary. Render in `Asia/Kolkata` by default for the India pilot.
- Store durations in integer seconds or minutes with an explicit field name.
- Use opaque UUID primary keys. Never use phone number, email, platform account ID, or exact GPS coordinates as primary keys.
- Every imported/derived record must carry provenance: `source_type`, `source_ref`, `import_batch_id`, `created_at`, and, where relevant, `target_quality`.
- A geographical observation should use an agreed zone identifier (initially H3 cell ID or explicitly defined study zone). Avoid retaining raw latitude/longitude by default.
- Keep `recorded_at` (when the system observed a value) distinct from `event_start_at`/`event_end_at` (when the event happened).
- All derived data must be reproducible from a versioned transform and input snapshot reference.

## 2. Core entities

### `worker_profiles`
| Field | Type | Rule |
|---|---|---|
| id | UUID | PK |
| owner_user_id | UUID nullable | Auth owner; required for private hosted data |
| display_name | text nullable | Optional pseudonym |
| home_zone_id | UUID nullable | Coarse zone only; user supplied |
| preferred_currency | char(3) | Default `INR` |
| created_at, updated_at | timestamptz | Audit |

Do not collect age, gender, caste, religion, disability, or other sensitive attributes for the MVP. Do not infer them.

### `platforms`
| Field | Type | Rule |
|---|---|---|
| id | UUID | PK |
| code | text | Unique stable code, e.g. `platform_a` |
| display_name | text | Display label; avoid implying partnership |
| active | boolean | Soft availability flag |
| created_at | timestamptz | Audit |

Platform names in the demo must be fictional unless the project has a legitimate reason and documented permission to use real names/logos.

### `zones`
| Field | Type | Rule |
|---|---|---|
| id | UUID | PK |
| zone_system | text | e.g. `h3`, `study_area`, `ward` |
| zone_code | text | Unique within zone system and resolution |
| resolution | integer nullable | Required for H3 |
| display_name | text nullable | Human-readable, non-sensitive |
| centroid_lat/lon | numeric nullable | Only coarse public centroid, never worker trace |
| boundary_ref | text nullable | Versioned geometry reference |

### `work_sessions`
Represents a declared working interval for one worker and one platform. It does **not** by itself imply the worker was accepting orders continuously.

| Field | Type | Rule |
|---|---|---|
| id | UUID | PK |
| worker_id | UUID FK | Required |
| platform_id | UUID FK | Required |
| started_at, ended_at | timestamptz | ended_at > started_at |
| status | enum | `completed`, `in_progress`, `cancelled` |
| source_type | enum/text | `manual`, `csv_import`, `synthetic`, `authorized_api` |
| import_batch_id | UUID nullable | FK |
| created_at | timestamptz | Audit |

### `deliveries`
One completed/recorded delivery event. Do not scrape or reverse-engineer platform apps. Fields may be entered manually or imported from a user-authorized export.

| Field | Type | Rule |
|---|---|---|
| id | UUID | PK |
| worker_id | UUID FK | Required |
| platform_id | UUID FK | Required |
| session_id | UUID nullable FK | Optional relation |
| external_ref_hash | text nullable | HMAC/hash if deduplication needed; never store raw order ID by default |
| accepted_at | timestamptz nullable | Source timestamp |
| completed_at | timestamptz | Required if completed |
| pickup_zone_id, drop_zone_id | UUID nullable FK | Coarse zones only |
| payout_paise | bigint nullable | Gross delivery payout as reported; define inclusions |
| incentive_paise | bigint nullable | Separate from payout |
| tip_paise | bigint nullable | Separate from payout |
| distance_m | integer nullable | Reported/estimated distance; provenance required |
| duration_seconds | integer nullable | Duration definition required |
| status | enum | `completed`, `cancelled`, `unknown` |
| target_quality | enum | `verified`, `user_reported`, `proxy`, `synthetic` |
| source_type | text | Required |
| import_batch_id | UUID nullable | FK |

### `expenses`
| Field | Type | Rule |
|---|---|---|
| id | UUID | PK |
| worker_id | UUID FK | Required |
| session_id | UUID nullable FK | Optional |
| occurred_at | timestamptz | Required |
| category | enum/text | `fuel`, `charging`, `maintenance`, `parking`, `mobile_data`, `other` |
| amount_paise | bigint | Non-negative |
| notes | text nullable | Warn users not to include sensitive details |
| source_type | text | Required |

### `zone_demand_observations`
This table contains **demand labels or explicit proxies**, never silently conflated.

| Field | Type | Rule |
|---|---|---|
| id | UUID | PK |
| zone_id | UUID FK | Required |
| interval_start | timestamptz | Bucket start |
| interval_minutes | smallint | e.g. 15, 30, 60 |
| orders_requested | integer nullable | True requested orders, only with valid source |
| orders_completed | integer nullable | Fulfilled orders; not equivalent to requested demand |
| deliveries_observed | integer nullable | Worker sample activity; label as sample activity |
| demand_proxy_value | numeric nullable | Proxy value; include definition |
| target_type | enum | `requested_orders`, `completed_orders`, `observed_deliveries`, `proxy` |
| coverage_fraction | numeric nullable | 0..1 with calculation documented |
| source_type | text | Required |
| target_quality | enum | `verified_aggregate`, `user_reported`, `proxy`, `synthetic` |
| import_batch_id | UUID nullable | FK |

### `context_observations`
| Field | Type | Rule |
|---|---|---|
| id | UUID | PK |
| zone_id | UUID nullable FK | Null for city-wide signal |
| observed_at | timestamptz | Observation time |
| valid_from, valid_to | timestamptz nullable | Forecast validity window when applicable |
| weather_code | text nullable | Source-specific code |
| temperature_c | numeric nullable | Unit explicit |
| precipitation_mm | numeric nullable | Unit explicit |
| wind_speed_kmh | numeric nullable | Unit explicit |
| event_type | text nullable | Only from lawful/credible source |
| source_name, source_version | text | Provenance |

### `import_batches`
Tracks data upload and validation.

| Field | Type | Rule |
|---|---|---|
| id | UUID | PK |
| owner_user_id | UUID nullable | Owner |
| filename_safe | text | Sanitized basename only |
| file_hash | text | Integrity/deduplication |
| detected_format | text | CSV initially |
| status | enum | `uploaded`, `validated`, `rejected`, `committed` |
| row_count, accepted_count, rejected_count | integer | Counts |
| validation_report_json | JSONB | No secrets or raw sensitive values |
| created_at | timestamptz | Audit |

### `forecast_runs`
| Field | Type | Rule |
|---|---|---|
| id | UUID | PK |
| model_version_id | UUID FK | Required |
| target_type | text | Earnings, requested demand, proxy, etc. |
| zone_id | UUID nullable FK | Required for zone forecast |
| worker_id | UUID nullable FK | Required for worker earnings prediction |
| horizon_start, horizon_end | timestamptz | Forecast window |
| point_prediction | numeric nullable | Target-specific unit |
| lower_prediction, upper_prediction | numeric nullable | Calibrated interval if available |
| unit | text | Explicit, e.g. `INR/hour`, `orders/30min` |
| input_snapshot_ref | text | Versioned immutable snapshot |
| created_at | timestamptz | Audit |

### `recommendation_runs`
Stores candidate ranking evidence, not an automatic instruction.

| Field | Type | Rule |
|---|---|---|
| id | UUID | PK |
| worker_id | UUID nullable FK | Optional demo identity |
| created_at | timestamptz | Audit |
| constraints_json | JSONB | User preferences and selected limits |
| scoring_version | text | Exact algorithm version |
| candidates_json | JSONB | Candidate features, score components, eligibility |
| selected_candidate_id | text nullable | User selection only; not an algorithmic assumption |

### `model_versions`
| Field | Type | Rule |
|---|---|---|
| id | UUID | PK |
| model_name | text | Stable name |
| version | text | Semver or immutable artifact version |
| target_definition | text | Exact target |
| training_data_ref | text | Manifest/snapshot |
| feature_schema_version | text | Feature contract |
| evaluation_json | JSONB | Metrics by temporal test window/segment |
| limitations | text | Required |
| status | enum | `experimental`, `candidate`, `approved`, `retired` |
| created_at | timestamptz | Audit |

## 3. Relationships and indexes

- `worker_profiles 1—N work_sessions`, `deliveries`, `expenses`.
- `platforms 1—N work_sessions`, `deliveries`.
- `zones 1—N zone_demand_observations`, `context_observations`, and optional delivery zone references.
- `import_batches 1—N imported records`.
- `model_versions 1—N forecast_runs`.
- Add composite indexes on `(zone_id, interval_start)`, `(worker_id, completed_at)`, `(platform_id, completed_at)`, `(owner_user_id, created_at)` for import batches, and foreign-key columns used in filters.
- Enforce uniqueness for `(zone_system, resolution, zone_code)` and for deduplication keys where a verified idempotency strategy exists.
- Enforce non-negative monetary fields, positive durations, valid time ranges, valid coverage range, and enumerated target types at database/API boundaries.

## 4. Derived metrics (definitions must stay consistent)

- **Gross earnings:** defined set of delivery payouts + incentives + tips within a time window. State whether reimbursements are included.
- **Net earnings:** gross earnings minus recorded worker expenses within the same accounting window. This is an estimate when expense capture is incomplete.
- **Online time:** duration from declared session start to end. For overlapping sessions, calculate the union of time intervals before summing total worker online time.
- **Active time:** time actively performing deliveries, only if it can be measured credibly. Do not substitute online time.
- **Earnings/hour:** net earnings divided by the explicitly named denominator; label `per online hour` or `per active hour`.
- **Demand rate:** target count divided by interval length, with target source and geography in the label.
- **Platform share:** platform-specific observed earnings divided by total observed earnings for the same scope. It is not market share.

## 5. Migrations and schema governance

- Treat this document as design intent. SQL migrations are the executable source of truth once created.
- Add migrations forward-only; test against a clean local database and a representative existing database.
- Turn on RLS for every exposed user-owned table if Supabase is used. Write negative tests proving one user cannot read or mutate another user's rows.
- Do not place service-role secrets in browser code.
- Changes to target definitions require a schema/feature version bump and a note in `docs/11_RISKS_ASSUMPTIONS_DECISIONS.md`.
