# Diagram Catalogue

The Mermaid files under `diagrams/` are source diagrams. They can be rendered in Markdown-compatible tools or passed to the installed Archify skill for a polished interactive architecture artefact.

| File | View | Notes |
|---|---|---|
| `01_system_context.mmd` | System context | Users, GigPulse modules and optional external sources |
| `02_container_architecture.mmd` | Container/component architecture | UI, modular API, ML package, database and artifacts |
| `03_ml_data_pipeline.mmd` | ML data pipeline | Provenance, target quality, chronological split and model registry |
| `04_prediction_recommendation_sequence.mmd` | Sequence | User request through prediction and candidate ranking |
| `05_entity_relationships.mmd` | ER diagram | Core domain entities and data relationships |

When using Archify, read its `SKILL.md` and bundled authoring/delivery contracts. Validate the diagram, deliver the viewer/artifact, then inspect the rendered output for coverage, legibility and correct relationships. Preserve the Mermaid source alongside any generated visual output.
