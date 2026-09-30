# AI evaluation

`fixtures/extraction/*.json`: hand-authored golden cases for request extraction (PRD §48).
They are **not recorded Gemini outputs**. In demo mode (no Gemini key) the API returns the fixture's
`expected` block for an exact text match, which makes the scripted demo scenarios (A: Bihar/Hindi
bridge, B: Andhra Pradesh/Telugu water, C: Pune/English transport, D: ambiguous "Rampur") reproducible.

With a key, `services/api/tests/test_eval_extraction.py::test_live_gemini_matches_fixtures` (skipped
without `GEMINI_API_KEY`) compares live Gemini output against the category / location / urgency here.
