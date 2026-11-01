# Academic Research and Demonstration Deliverables

## 1. Proposed academic framing

**Working title:** AI-Driven Machine Learning for Spatio-Temporal Earnings Prediction, Demand Forecasting & Intelligent Optimization of Multi-Platform Gig Delivery Partners.

**Research framing:** A data-driven decision-support framework that studies worker-level earning outcomes and zone/time delivery activity separately, then combines their valid predictions with travel-cost and worker-preference constraints for transparent opportunity ranking.

## 2. Research questions

- RQ1: How accurately can worker earnings be estimated across platform, time and zone contexts from available historical work records?
- RQ2: How well can delivery activity or demand be forecast across zones and time intervals, given the actual label and coverage available?
- RQ3: Does a preference-aware, risk-aware ranking method improve the quality of candidate work options compared with a simple earnings-only ranking under the same constraints?
- RQ4: How do missing data, coverage and temporal drift affect forecast reliability and recommendation quality?

RQ2 must be renamed to observed delivery-activity forecasting if true requested-order labels are unavailable.

## 3. Hypotheses (testable, not assumed true)

- H1: A feature-based earnings model may outperform a historical/seasonal baseline on a held-out chronological test window.
- H2: Zone/time features may improve delivery-activity forecasting over a global or seasonal naive baseline when data coverage is adequate.
- H3: A multi-objective recommendation score may produce more suitable options under explicit worker constraints than an earnings-only ranking; suitability must be operationalized and evaluated, not asserted.

## 4. Suggested report structure

1. Abstract and keywords.
2. Introduction: platform gig work, decision problem, scope and objectives.
3. Related work: gig economy, spatio-temporal forecasting, earnings estimation, recommendation/routing.
4. Problem formulation: independent targets, units, entities, constraints and assumptions.
5. Dataset and preprocessing: source, consent/licence, schema, missingness, coverage, privacy and synthetic/empirical split.
6. Methodology: baseline, model candidates, features, spatial representation, temporal split, metrics and uncertainty.
7. System design: architecture, modules, database, API and security.
8. Implementation: screens, workflows, stack and reproducible setup.
9. Results: baseline comparison, rolling-window analysis, error by segment, interval calibration.
10. Discussion: interpretation, limitations, bias, practical implications.
11. Conclusion and future work.
12. References and appendices: data dictionary, API, experiment manifests, tests, sample outputs.

## 5. Demonstration script (5–7 minutes)

1. Introduce the problem and explain the difference between earnings and zone demand.
2. Open the seeded demo and point out the permanent synthetic-data label.
3. Add a work session, delivery and expense; explain paise and the net-earnings formula.
4. Show history versus forecast and identify the model, unit, time horizon and uncertainty.
5. Open the demand map; identify whether the chosen target is observed deliveries or requested orders.
6. Compare opportunity candidates; reveal travel cost, uncertainty, data coverage and score components.
7. Open Model Lab and show chronological evaluation against a baseline.
8. Close with limitations and next research steps—no guarantee of future earnings.

## 6. Viva questions to prepare

- What is spatio-temporal data in this project?
- Why are earnings forecasting and demand forecasting separate tasks?
- Why are completed orders not the same as requested demand?
- Why is random train/test splitting unsuitable for future forecasting claims?
- What is data leakage? Give one concrete example from this system.
- Why do you need a baseline? Which metric did you choose and why?
- How do you estimate net earnings when expenses are incomplete?
- What is H3 and why might a hexagonal zone system be useful?
- How do you prevent privacy leakage from location data?
- What happens when the model is uncertain or the zone has little data?
- What evidence supports the system's claims, and what is still synthetic?

## 7. Figures and tables to include

- System context and component architecture.
- ML data lifecycle and point-in-time feature flow.
- Entity relationship diagram.
- Sequence diagram for a forecast/recommendation request.
- Dataset profile and target-quality table.
- Baseline vs candidate metric table by test window.
- Residual/error plots and interval coverage plots.
- Demand coverage map with legend and target definition.
- Recommendation component breakdown.

## 8. Claim discipline

Clearly separate:
- **Implemented:** verified in code and tested.
- **Demonstrated:** shown with synthetic or sample data.
- **Experimentally supported:** result reproduced on held-out empirical data.
- **Proposed/future:** not implemented or not yet validated.

Do not turn a working demo into a claim that worker earnings increased or platform demand is accurately known.
