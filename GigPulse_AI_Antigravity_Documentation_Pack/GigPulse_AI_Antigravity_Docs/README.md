# GigPulse AI — Antigravity Project Blueprint

> Research-backed product and engineering documentation for: **AI-Driven Machine Learning for Spatio-Temporal Earnings Prediction, Demand Forecasting & Intelligent Optimization of Multi-Platform Gig Delivery Partners.**
>
> Product codename: **GigPulse AI** (working name). Documentation baseline: **01 November 2026**.

## Contents

| Path | Purpose |
|---|---|
| `docs/00_PROJECT_CHARTER.md` | Vision, problem, objectives, scope and contribution |
| `docs/01_PRD.md` | Requirements, personas, journeys and acceptance criteria |
| `docs/02_RESEARCH_METHODOLOGY.md` | Research questions, hypotheses and study design |
| `docs/03_SYSTEM_ARCHITECTURE.md` | Components, stack, data flow and deployment |
| `docs/04_ML_DESIGN.md` | Targets, features, models, validation and optimization |
| `docs/05_DATA_DICTIONARY_SCHEMA.md` | Entities, types, relationships and quality rules |
| `docs/06_API_CONTRACT.md` | REST endpoints, payloads and errors |
| `docs/07_UX_UI_DESIGN_SYSTEM.md` | Screens, visual language and accessibility |
| `docs/08_SECURITY_PRIVACY_GOVERNANCE.md` | Privacy, threat model and security requirements |
| `docs/09_TESTING_EVALUATION.md` | Software QA, ML evaluation and release gates |
| `docs/10_IMPLEMENTATION_ROADMAP.md` | Phased implementation plan |
| `docs/11_RISKS_ASSUMPTIONS_DECISIONS.md` | Risks, assumptions and ADRs |
| `docs/12_ACADEMIC_DELIVERABLES.md` | Report, presentation and viva preparation |
| `docs/13_RESEARCH_REFERENCES.md` | External research and technical references |
| `docs/14_DIAGRAM_CATALOG.md` | Diagram descriptions and Archify delivery guidance |
| `antigravity/AGENTS.md` | Persistent rules for coding agents |
| `MASTER_PROMPT.md` | Root-level copy/paste kickoff prompt |
| `source-references/` | Exact copies of the two uploaded skill-reference files |
| `antigravity/ANTIGRAVITY_MASTER_PROMPT.md` | Copy/paste project-start prompt |
| `antigravity/SKILL_ROUTING.md` | Skill mapping from the two uploaded files |
| `antigravity/WORKFLOW_AND_DEFINITION_OF_DONE.md` | Agent workflow and verification rules |
| `diagrams/*.mmd` | Mermaid architecture, data and sequence diagrams; Archify-ready |
| `data/templates/*.csv` | Header-only import contracts, not actual platform exports |
| `data/SYNTHETIC_DATA_SPEC.md` | Reproducible synthetic-data requirements |

## How to use this pack

1. Extract the ZIP and copy the folder contents into the root of a new project repository, preserving the paths.
2. Open that repository in Antigravity.
3. Read `antigravity/AGENTS.md`, then paste `antigravity/ANTIGRAVITY_MASTER_PROMPT.md` into Antigravity.
4. Start with the root `MASTER_PROMPT.md` or `antigravity/ANTIGRAVITY_MASTER_PROMPT.md`. Ask Antigravity to perform **Phase 0 — repository and environment reconnaissance only**. Do not begin feature coding before it checks the repository, installed skills, current official framework documentation, local resource limits and open decisions.
5. Implement in phases using `docs/10_IMPLEMENTATION_ROADMAP.md`. Require tests and evidence for every completion claim.

## Uploaded skill references

The originals are preserved in `source-references/`. The skill routing matrix is based on these user-supplied snapshots. Antigravity must verify each actual local skill file and current prerequisites before invoking it; the references are not proof that every skill is present or up to date.

## Product concept

GigPulse AI is a worker-centred decision-support system that estimates earnings, forecasts observed/labelled delivery demand by time and urban zone, and ranks feasible platform-zone-time choices using net earnings, travel cost, uncertainty and the worker's own constraints.

## Non-negotiable research integrity rule

A rider's completed-order history is **not** a complete measurement of all orders demanded in a zone. It is a partial, selection-biased observation of deliveries the rider received and completed. Preserve the distinction between `observed_delivery_activity`, `measured_zone_demand`, `proxy_demand` and `synthetic_demand`. Do not claim “city-wide demand prediction” unless the labels genuinely represent city-wide or sufficiently covered demand.

## Default engineering posture

- Local-first; no paid service required for the first working demo.
- Use open-source libraries and replaceable adapters.
- Start with interpretable statistical/tree-based baselines; do not begin with a large deep-learning stack.
- Modular monolith first; no microservices, Kafka, Spark, Redis or reinforcement learning in the MVP.
- No unauthorized scraping, reverse engineering, platform credential collection or private API use.
- No live order auto-acceptance, auto-decline, dispatching or control of third-party apps.
- Show estimates, uncertainty/coverage and reasons; never guarantee income.

## Title recommendation

Retain the supplied title for formal registration unless your guide approves a change. The suggested alternative title in the charter is more concise and makes the risk-aware optimization contribution explicit. Do not silently replace the official academic title.
