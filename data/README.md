# Data

Every dataset (file or table) must carry: `source`, `reference_timestamp`, `dataset_version`,
`geographic_scope`, and `is_sample` / `is_synthetic`. Labelled in the UI as well.

- `schemas/`: canonical schema (PRD §21) as JSON Schema, generated from `services/api/app/models.py`
  (`cd services/api && uv run python -m app.export_schemas`).
- `adapters/`: one JSON config per state (`BR`, `AP`, `MH`) mapping that state's raw files to the
  canonical schema: field paths, value maps, unit multipliers (lakh/crore → INR, households → people),
  category and status maps. Applied by `services/api/app/interop/adapters.py`.
- `sample/`: **synthetic** demo data + `manifest.json` (source, timestamp, version, scope, flags).
  Raw state files are deliberately in different formats to exercise the adapters.
- `transformations/generate_sample.py`: deterministic generator for everything in `sample/`
  (`python3 data/transformations/generate_sample.py`). No AI is used.
