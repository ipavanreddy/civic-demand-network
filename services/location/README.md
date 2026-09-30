# location

Free-text location → LGD code resolution (Maps Geocoding)

Starts as a router/module in `services/api/app/` (e.g. `app/location/`).
Split into its own Cloud Run service here only if it needs separate scaling or runtime.

Implemented in `services/api/` as `app/pipeline/location.py`.
