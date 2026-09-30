"""Live evaluation of Gemini request extraction (PRD §48) against labelled requests.

    cd services/api && uv run python -m app.eval_extraction [N]

Uses the configured Gemini (API key or Vertex AI from .env). Test set: the hand-authored golden
fixtures in ai/evaluation/fixtures/extraction plus a seeded, stratified sample of N distinct
template-labelled synthetic requests (data/sample/requests_synthetic.jsonl) in EN / HI / TE.
Reports category accuracy (internal target >= 85%), urgency agreement on the golden set, invented
beneficiary numbers (caught by the guard) and location mentions that do not appear in the text.
"""
from __future__ import annotations

import json
import os
import random
import sys
import time
from collections import defaultdict
from pathlib import Path

from app.ai import gemini
from app.config import settings
from app.pipeline import understanding
from app.pipeline.understanding import normalise


def _sample(n: int) -> list[dict]:
    path = Path(settings.data_dir) / "sample" / "requests_synthetic.jsonl"
    by_key: dict[tuple, dict[str, dict]] = defaultdict(dict)
    for line in path.read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        by_key[(r["language"], r["category"])].setdefault(r["text_original"], r)
    rng = random.Random(7)
    groups = [list(v.values()) for _, v in sorted(by_key.items())]
    for g in groups:
        rng.shuffle(g)
    out: list[dict] = []
    while len(out) < n and any(groups):
        for g in groups:
            if g and len(out) < n:
                out.append(g.pop())
    return out


def main(n: int = 40) -> int:
    if not gemini.is_configured():
        print("Gemini is not configured (.env): set GEMINI_API_KEY or GOOGLE_GENAI_USE_VERTEXAI=true + project.")
        return 2
    cases = [{"id": fx["id"], "language": fx["language"], "state": fx["state"], "text_original": fx["text_original"],
              "text_en": fx["text_en"], "category": fx["expected"]["category"], "urgency": fx["expected"]["urgency"],
              "golden": True} for fx in understanding.fixtures()]
    cases += [{"id": r["request_id"], "language": r["language"], "state": r["state"], "text_original": r["text_original"],
               "text_en": r["text_en"], "category": r["category"], "urgency": None, "golden": False} for r in _sample(n)]

    rows, t0 = [], time.time()
    delay = float(os.environ.get("EVAL_DELAY", "1.5"))  # seconds between calls, to stay under shared quota
    for c in cases:
        time.sleep(delay)
        ex, prov = understanding.extract(c["text_original"], c["text_en"], c["language"], "web", c["state"], None, [])
        blob = normalise(f"{c['text_original']} {c['text_en']}")
        invented_places = [m.text for m in ex.location_mentions if normalise(m.text) not in blob]
        rows.append({
            "id": c["id"], "lang": c["language"], "expected": c["category"], "got": ex.category,
            "ok": ex.category == c["category"],
            "urgency_ok": None if c["urgency"] is None else ex.urgency == c["urgency"],
            "number_removed": any("beneficiary count removed" in m for m in ex.missing_information),
            "invented_places": invented_places, "mode": prov.mode, "golden": c["golden"],
        })
    live = [r for r in rows if r["mode"] == "real"]
    if not live:
        print("All calls fell back to demo mode; check the Gemini configuration.")
        return 1

    def pct(xs: list[bool]) -> str:
        return f"{100 * sum(xs) / len(xs):.0f}% ({sum(xs)}/{len(xs)})" if xs else "n/a"

    print(f"Model {settings.gemini_model} · prompt extract_v1 · {len(live)}/{len(rows)} calls live "
          f"(rest fell back to demo after retries) in {time.time() - t0:.0f}s")
    print(f"Category accuracy (all):    {pct([r['ok'] for r in live])}")
    for lang in ("en", "hi", "te"):
        print(f"  {lang}:                       {pct([r['ok'] for r in live if r['lang'] == lang])}")
    print(f"Golden fixtures category:   {pct([r['ok'] for r in live if r['golden']])}")
    print(f"Golden fixtures urgency:    {pct([r['urgency_ok'] for r in live if r['urgency_ok'] is not None])}")
    print(f"Invented beneficiary count: {pct([r['number_removed'] for r in live])} (removed by the guard)")
    print(f"Place not in the text:      {pct([bool(r['invented_places']) for r in live])} "
          "(includes transliterations of local-script names)")
    for r in live:
        if not r["ok"]:
            print(f"  miss {r['id']} [{r['lang']}]: expected {r['expected']}, got {r['got']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(int(sys.argv[1]) if len(sys.argv) > 1 else 40))
