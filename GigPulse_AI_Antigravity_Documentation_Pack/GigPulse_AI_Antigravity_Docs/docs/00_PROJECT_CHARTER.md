# 00 — Project Charter

## 1. Identity

**Official title supplied by the student**

> AI-Driven Machine Learning for Spatio-Temporal Earnings Prediction, Demand Forecasting & Intelligent Optimization of Multi-Platform Gig Delivery Partners.

**Working product name:** GigPulse AI  
**Suggested academic title (optional; obtain guide approval):** *AI-Driven Spatio-Temporal Earnings Prediction, Demand Forecasting, and Risk-Aware Optimization for Multi-Platform Gig Delivery Partners.*

The phrase *risk-aware* is useful because a recommendation should not rank an uncertain high estimate as though it were guaranteed income.

## 2. Vision

Give an independent delivery partner a clearer, evidence-based view of **when**, **where** and **on which enabled platform** their time may be most productive, while showing uncertainty, expenses and personal constraints. This is a worker-centred decision-support tool; it does not represent, control or make decisions on behalf of a delivery platform.

## 3. Problem statement

Multi-platform delivery partners may work across different apps, zones and time windows. Their realised earnings can vary with order volume, payouts, incentives, tips, travel distance, waiting time, weather, day-of-week effects and expenses. Information is fragmented across platform histories and personal records. A worker may therefore find it difficult to compare net earning opportunities across platforms and locations before choosing where to spend time.

The project investigates whether historical, appropriately permissioned delivery and contextual data can support:

1. short-horizon earnings estimation;
2. zone-and-time demand forecasting where valid demand labels exist; and
3. transparent ranking of feasible platform-zone-time alternatives.

The model cannot infer unavailable platform internals, unobserved competing orders or a worker's future guaranteed income.

## 4. Core proposition

**Predict → Explain → Compare → Recommend → Learn from verified outcomes.**

- Predict earnings and demand at a defined horizon and geographical resolution.
- Explain the main factors, data coverage and uncertainty.
- Compare alternatives on a consistent net-earnings basis.
- Recommend only options that satisfy user-set constraints.
- Compare forecasts with later observed results to identify model weaknesses.

## 5. Objectives

### Primary objectives

- Build a normalized, auditable data model for multiple delivery platforms.
- Estimate gross payout, net payout and earnings rates with clear time denominators.
- Forecast delivery demand at a documented zone/time interval when valid zone-demand labels are available.
- Combine predictions with travel/operating costs and worker constraints in a deterministic recommendation engine.
- Provide a clear, responsive dashboard with maps, time-series charts and model explanations.
- Evaluate all models against simple baselines using chronological holdouts.

### Secondary objectives

- Support CSV/manual import and a reproducible synthetic-data demo.
- Incorporate non-sensitive contextual features such as calendar and weather where legally and technically appropriate.
- Track model versions, training windows, source provenance and data quality.
- Provide privacy, export and deletion controls appropriate to the deployment mode.

## 6. Research contribution to test—not assume

The proposed contribution is an integrated, worker-oriented pipeline that combines (a) multi-platform net-earnings estimation, (b) zone-time demand estimates with explicit label provenance and (c) risk-aware recommendation ranking under worker-defined constraints. Whether this improves over simpler alternatives is an empirical question. The project must not claim novelty merely because it combines existing algorithms.

## 7. Intended users

- **Primary:** individual gig delivery partners who can voluntarily provide their own historical shift/order/expense records.
- **Secondary:** academic evaluators, researchers and project administrators using synthetic or properly consented aggregate data.

Not intended for employer surveillance, platform worker scoring, automatic dispatch, credit assessment, insurance underwriting or worker discipline.

## 8. Success criteria

The project is successful when it can demonstrate, with reproducible evidence:

- valid import and normalization of records from at least two configurable platform profiles (manual/CSV profiles, not private integrations);
- correct gross-to-net calculations with documented expense allocation;
- earnings predictions evaluated on a chronological test period against a naive baseline;
- zone-demand forecasting evaluated only on defensible observed labels, or a clearly labelled proxy/synthetic experiment;
- transparent recommendations that satisfy worker constraints and expose uncertainty;
- end-to-end tests for the major user journeys;
- a research report that distinguishes measured results, synthetic demonstrations and limitations.

No numeric accuracy or income-uplift target is promised before the dataset is inspected. Establish baseline performance first, then set a justified acceptance threshold.

## 9. Scope

### MVP

- Local-first web application.
- CSV import validation and manual entry.
- Multiple platform names/profiles.
- Shift, delivery, expense and zone records.
- Earnings summary and net earnings estimator.
- Demand forecast for zones/time buckets when data supports it.
- Risk-aware recommendation ranking.
- Explainability, confidence/coverage and data-quality labels.
- Synthetic demo data with visible `SYNTHETIC` markings.
- Model evaluation report and audit metadata.

### Later extensions

- Secure multi-user authentication and hosted PostgreSQL/Supabase deployment.
- Additional city-level contextual sources and official integrations where permitted.
- Hierarchical or graph-based spatio-temporal forecasting when volume and coverage justify it.
- Carefully designed prospective evaluation with participant consent.

### Explicitly out of scope

- Scraping logged-in platform apps or reverse engineering private endpoints.
- Asking users to enter platform passwords, OTPs, session cookies or API secrets.
- Accepting/declining orders, dispatching jobs or controlling another app.
- Guaranteeing future income or claiming access to total live market demand without a valid source.
- Financial, legal, employment or safety advice presented as professional advice.
- Reinforcement learning or automated worker control in the first release.

## 10. Guiding principles

1. **Worker agency:** the user decides; recommendations are advisory.
2. **Honest uncertainty:** show ranges, sample counts and stale-data notices.
3. **Data provenance:** every metric has a source and measurement definition.
4. **Privacy by default:** minimize exact location and identity data.
5. **Explainability:** show why a zone/platform ranks highly.
6. **Simple before complex:** establish baselines before advanced architectures.
7. **Reproducibility:** fixed seeds, versioned datasets, code and evaluation windows.
8. **No false claims:** no model, integration, deployment or metric is marked complete without evidence.
