# clustering-scoring

Demand clustering (embeddings) and Priority Score

Starts as a router/module in `services/api/app/` (e.g. `app/clustering_scoring/`).
Split into its own Cloud Run service here only if it needs separate scaling or runtime.

Implemented in `services/api/` as `app/pipeline/clustering.py`, `fusion.py`, `scoring.py`, `ranking.py`.
