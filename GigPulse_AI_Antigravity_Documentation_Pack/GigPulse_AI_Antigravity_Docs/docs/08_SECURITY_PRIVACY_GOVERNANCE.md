# Security, Privacy and Responsible AI Governance

## 1. Operating principles

- Collect only what is necessary to estimate a user's earnings or show an opt-in zone/time analysis.
- Default to manual entry and user-authorized CSV exports. Do not scrape delivery apps, bypass controls, automate logins or collect platform credentials.
- Do not collect continuous background GPS in the MVP. Coarse zones are sufficient for the first research prototype.
- Do not infer sensitive personal characteristics or use them for predictions or ranking.
- Predictions are estimates for decision support, not guaranteed earnings, employment advice or automatic work allocation.
- Provide user control, clear explanations, correction, export and deletion pathways.

## 2. Threat model

| Asset | Threat | Baseline control |
|---|---|---|
| Earnings and work history | Cross-user disclosure | Authentication, ownership checks, RLS if Supabase |
| CSV uploads | Formula injection, parser abuse, malicious payload | Size/row/column limits, strict schemas, no formula evaluation, safe export escaping |
| Credentials and secrets | Accidental commit or browser exposure | Environment variables, `.env*` ignore rules, secret scanning, no service secrets in frontend |
| API | Injection, IDOR, abusive requests | Parameterized SQL, authorization on every object, rate limits, validation |
| Model features | Leakage, target mislabelling | Feature cutoff rules, target metadata, temporal evaluation |
| Map data | Re-identification through fine-grain traces | Coarse zones, minimum aggregation thresholds, no raw trace storage by default |
| Model output | Misleading confidence or unfair recommendations | Backtesting, uncertainty calibration, segment checks, explanation and override |
| Third-party data | Licence/terms violation or stale feed | Source registry, licence/terms review, cache/freshness metadata |

## 3. Authentication and authorization

- Local single-user prototype may run without cloud authentication only if it binds to localhost and stores no shared user data.
- Hosted mode must use a maintained auth mechanism; each user-owned row must be owner-scoped.
- If Supabase is selected: enable RLS on every exposed table; test both permitted and denied access; authorization decisions must not rely on mutable user metadata; keep service-role keys server-side.
- Verify object ownership on every read, update, delete, export and prediction request.

## 4. Data handling lifecycle

1. Explain what fields the import expects and why.
2. Validate in a temporary area; do not commit by default.
3. Display parsed mapping and warnings; redact sample values in diagnostics.
4. Commit only after user review and explicit action.
5. Retain only normalized fields needed by the product; avoid retaining raw source files longer than required.
6. Provide owner-scoped export and deletion; deletion should cover raw imports, normalized rows, cached feature tables and generated user-specific artifacts where feasible.
7. Log access and administrative actions without writing raw payout details or secrets to logs.

Document retention/deletion behavior and backup limitations in the UI and project report.

## 5. Privacy-preserving location design

- Use H3/administrative zones at a resolution chosen by the research unit and population density; document the selected resolution.
- Aggregate before display and suppress small counts where an individual could be inferred.
- Avoid exact home/work pins and exact timestamp-plus-location combinations in shared demo datasets.
- If public map tiles are used, review provider usage policy and attribution. OpenStreetMap-derived databases require careful ODbL review; do not assume all source data has the same licence.
- Never send exact location histories to third-party AI services.

## 6. Responsible ML controls

- Publish intended use, excluded use, target definition, data coverage and known limitations with each model.
- Compare performance across time windows, zones, platforms and available non-sensitive operational segments.
- Do not rank workers or expose one worker's performance to another.
- Avoid optimizing solely for platform utilization or order throughput; include worker preferences, travel burden, costs and uncertainty.
- Provide candidate reasons, not opaque scores only. Allow users to ignore recommendations.
- Detect out-of-distribution data and missing/low coverage; fall back to baseline or show “insufficient data”.
- Never present a prediction as a guaranteed outcome.

## 7. Regulatory and policy research notes

This project may process personal data in India. Before any real-user pilot, review the Digital Personal Data Protection Act, 2023, the Digital Personal Data Protection Rules, 2025, their current commencement/transition notifications, and any other applicable laws and contractual duties. The implementation must be reviewed against the law actually in force at the time of deployment. This document is engineering guidance, not legal advice or a claim of compliance certification.

## 8. Security acceptance checklist

- No secrets in repository, bundles, logs or generated docs.
- All private endpoints enforce authentication and row/object ownership.
- SQL is parameterized; uploaded CSV is treated as untrusted input.
- File size, row count, parser time and request frequency are bounded.
- CORS, cookies, CSRF/session controls and security headers are configured for the chosen deployment.
- Dependency and secret scans are run; high-risk findings are resolved or documented.
- Data export/delete are tested against all owned datasets.
- A threat-model review is completed before external beta.
