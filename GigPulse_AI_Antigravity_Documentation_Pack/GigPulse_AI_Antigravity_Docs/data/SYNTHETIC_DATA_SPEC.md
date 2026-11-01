# Synthetic Data Specification

Synthetic data supports deterministic development demos and automated tests. It is not empirical evidence about actual gig workers, platform demand or earnings.

## Required rules

- Every generated row uses `source_type=synthetic` and `target_quality=synthetic`.
- Include a `dataset_manifest.json` with generator version, seed, row counts, time range, assumptions and a clear statement: `synthetic=true`.
- Use fictional platform names and fictional zone names/IDs. Do not imitate a real platform's unpublished payout formula.
- Generate patterns that exercise edge cases: weekend effects, lunch/evening peaks, low-activity zones, missing context, variable distance/time, occasional bonuses, expenses and overlapping multi-platform sessions.
- Make patterns configurable and deterministic by seed.
- Do not tune the generator solely to make a candidate model look good.
- Store no real person's identifiers or coordinates.
- The UI must show a persistent “Synthetic demonstration data” label whenever a view includes these rows.

## Suggested starter scale

For low-resource local development, start with:
- 3 fictional platforms;
- 12–25 coarse fictional zones;
- 1–5 fictional worker profiles;
- 8–12 weeks of timestamped records;
- 0–15 delivery events per worker/platform/session/day (randomized, not guaranteed);
- 30-minute zone/time observations;
- some missing values and sparse zones;
- separate datasets for requested-order counts, completed-order counts, observed deliveries and proxy signals so the target distinction can be demonstrated.

Keep generated data compact (a few thousand rows at first). Scale only after the local environment is profiled.

## Suggested CSV templates

See `templates/`. Templates are header-only and are not production imports until validation/mapping is implemented.
