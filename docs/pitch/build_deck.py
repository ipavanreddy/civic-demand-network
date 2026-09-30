"""Build the JanVaani pitch deck (docs/pitch/JanVaani_pitch.pptx).

    uv run --with python-pptx python docs/pitch/build_deck.py

11 slides, 16:9, structured around the hackathon evaluation criteria (PRD §55) plus
cross-border / BRICS portability. All figures come from the prototype and its synthetic sample data.
"""
from __future__ import annotations

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Inches, Pt

OUT = Path(__file__).with_name("JanVaani_pitch.pptx")

INK = RGBColor(0x1F, 0x23, 0x2B)
MUTED = RGBColor(0x5B, 0x63, 0x70)
LINE = RGBColor(0xDD, 0xE1, 0xE6)
BG_SOFT = RGBColor(0xF5, 0xF6, 0xF8)
BRAND = RGBColor(0x1D, 0x4E, 0x89)      # deep blue
ACCENT = RGBColor(0xE8, 0x7A, 0x1E)     # saffron
GREEN = RGBColor(0x2E, 0x7D, 0x4F)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
FONT = "Calibri"

W, H = Inches(13.333), Inches(7.5)
MARGIN = Inches(0.6)


def _text(tf, text: str, size: int, color=INK, bold=False, align=PP_ALIGN.LEFT, first=True):
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    p.alignment = align
    r = p.add_run()
    r.text = text
    r.font.size, r.font.bold, r.font.name = Pt(size), bold, FONT
    r.font.color.rgb = color
    return p


def textbox(slide, x, y, w, h, text: str | list[str], size=18, color=INK, bold=False,
            align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, spacing=6):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = Inches(0.05)
    lines = text if isinstance(text, list) else [text]
    for i, line in enumerate(lines):
        p = _text(tf, line, size, color, bold, align, first=i == 0)
        p.space_after = Pt(spacing)
    return tb


def bullets(slide, x, y, w, h, items: list[str], size=18, color=INK, marker="•"):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(8)
        m = p.add_run()
        m.text = f"{marker}  "
        m.font.size, m.font.name, m.font.bold = Pt(size), FONT, True
        m.font.color.rgb = ACCENT
        head, _, tail = item.partition("|")
        r = p.add_run()
        r.text = head
        r.font.size, r.font.name, r.font.bold = Pt(size), FONT, bool(tail)
        r.font.color.rgb = color
        if tail:
            r2 = p.add_run()
            r2.text = tail
            r2.font.size, r2.font.name = Pt(size), FONT
            r2.font.color.rgb = MUTED
    return tb


def box(slide, x, y, w, h, fill=BG_SOFT, line=None, shape=MSO_SHAPE.ROUNDED_RECTANGLE):
    s = slide.shapes.add_shape(shape, x, y, w, h)
    s.fill.solid()
    s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line
        s.line.width = Pt(1)
    s.shadow.inherit = False
    if shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        s.adjustments[0] = 0.08
    return s


def card(slide, x, y, w, h, title: str, body: list[str] | str, fill=BG_SOFT, title_color=BRAND, size=15):
    box(slide, x, y, w, h, fill)
    textbox(slide, x + Inches(0.2), y + Inches(0.15), w - Inches(0.4), Inches(0.5), title, 18, title_color, True)
    body_lines = body if isinstance(body, list) else [body]
    textbox(slide, x + Inches(0.2), y + Inches(0.65), w - Inches(0.4), h - Inches(0.8), body_lines, size, INK, spacing=4)


def pill(slide, x, y, w, h, text: str, fill=BRAND, color=WHITE, size=14, bold=True):
    s = box(slide, x, y, w, h, fill)
    s.adjustments[0] = 0.5
    tf = s.text_frame
    tf.margin_left = tf.margin_right = Inches(0.05)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    _text(tf, text, size, color, bold, PP_ALIGN.CENTER)
    return s


def arrow(slide, x1, y1, x2, y2, color=MUTED):
    c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, x1, y1, x2, y2)
    c.line.color.rgb = color
    c.line.width = Pt(2)
    ln = c.line._get_or_add_ln()
    tail = ln.makeelement("{http://schemas.openxmlformats.org/drawingml/2006/main}tailEnd", {"type": "triangle"})
    ln.append(tail)
    return c


def base(prs, title: str, kicker: str | None = None, page: int | None = None):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    bg = s.background.fill
    bg.solid()
    bg.fore_color.rgb = WHITE
    box(s, 0, 0, W, Inches(0.12), BRAND, shape=MSO_SHAPE.RECTANGLE)
    if kicker:
        textbox(s, MARGIN, Inches(0.35), Inches(9), Inches(0.4), kicker.upper(), 13, ACCENT, True)
    textbox(s, MARGIN, Inches(0.65), W - 2 * MARGIN, Inches(0.9), title, 32, INK, True)
    footer = "JanVaani · Build with AI · Track 1"
    textbox(s, MARGIN, H - Inches(0.5), Inches(6), Inches(0.3), footer, 11, MUTED)
    if page:
        textbox(s, W - MARGIN - Inches(1), H - Inches(0.5), Inches(1), Inches(0.3), str(page), 11, MUTED,
                align=PP_ALIGN.RIGHT)
    return s


def notes(slide, text: str):
    slide.notes_slide.notes_text_frame.text = text


# ----------------------------------------------------------------------------------------- slides
def slide_title(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = BRAND
    box(s, 0, H - Inches(0.25), W, Inches(0.25), ACCENT, shape=MSO_SHAPE.RECTANGLE)
    textbox(s, MARGIN, Inches(1.6), Inches(12), Inches(1.2), "JanVaani", 66, WHITE, True)
    textbox(s, MARGIN, Inches(2.75), Inches(12), Inches(0.8), "जनवाणी · జనవాణి · the people's voice", 26,
            RGBColor(0xC9, 0xD8, 0xEE))
    textbox(s, MARGIN, Inches(3.8), Inches(11.5), Inches(1.4),
            ["Every citizen's request, in any language, becomes evidence for",
             "where India builds its next bridge, pipeline or bus route."], 26, WHITE)
    textbox(s, MARGIN, Inches(5.6), Inches(12), Inches(0.5),
            "Build with AI (Google) · Track 1 · Gemini on Vertex AI · Speech · Translation · Maps · BigQuery · Cloud Run",
            15, RGBColor(0xC9, 0xD8, 0xEE))
    notes(s, "One sentence: JanVaani turns multilingual citizen requests into ranked, evidence-backed "
             "infrastructure recommendations, with a human making every decision.")


def slide_problem(prs):
    s = base(prs, "Citizens ask. Planners can't hear them at scale.", "Problem-solution fit · 20%", 2)
    cards = [
        ("Fragmented", ["Requests arrive by letter, gram sabha, grievance portal, WhatsApp, and are never added up."]),
        ("Multilingual", ["22 scheduled languages; many citizens speak rather than type. English-only forms exclude them."]),
        ("Misaligned spending", ["Budgets follow the loudest voice or last year's plan, not measured unmet need."]),
        ("No feedback loop", ["Citizens never hear back, so they stop asking; demand stays invisible."]),
    ]
    cw = (W - 2 * MARGIN - Inches(0.3) * 3) / 4
    for i, (t, b) in enumerate(cards):
        card(s, MARGIN + i * (cw + Inches(0.3)), Inches(1.9), cw, Inches(2.6), t, b, size=16)
    box(s, MARGIN, Inches(4.9), W - 2 * MARGIN, Inches(1.5), RGBColor(0xFD, 0xF1, 0xE6))
    textbox(s, MARGIN + Inches(0.3), Inches(5.05), W - 2 * MARGIN - Inches(0.6), Inches(1.3),
            ["Our answer: one pipeline from a parent's voice note in Gaya to a planning officer's decision, "
             "and back to the parent, in her language.",
             "Citizen (voice / text / chat) → Gemini understanding → location → demand cluster → data fusion → "
             "Priority Score → evidence brief → human decision → status update."], 17, INK, spacing=6)
    notes(s, "Frame the persona: a parent in a village in Gaya whose children cannot reach school every monsoon.")


def slide_journey(prs):
    s = base(prs, "One continuous journey, live on Google Cloud", "The solution", 3)
    steps = [("Speak", "Hindi voice note\nCloud STT"), ("Understand", "Gemini JSON\ncategory, urgency"),
             ("Locate", "LGD code\n+ H3 cell"), ("Cluster", "Gemini\nembeddings"),
             ("Fuse & score", "Demographics, gap,\ninvestment"), ("Brief", "Gemini, every\nnumber checked"),
             ("Decide", "Officer approves;\ncitizen notified")]
    n = len(steps)
    gap = Inches(0.25)
    bw = (W - 2 * MARGIN - gap * (n - 1)) / n
    y = Inches(2.2)
    for i, (t, sub) in enumerate(steps):
        x = MARGIN + i * (bw + gap)
        b = box(s, x, y, bw, Inches(1.9), BRAND if i in (1, 5) else BG_SOFT)
        light = i in (1, 5)
        textbox(s, x + Inches(0.1), y + Inches(0.2), bw - Inches(0.2), Inches(0.5), t, 18,
                WHITE if light else BRAND, True, PP_ALIGN.CENTER)
        textbox(s, x + Inches(0.1), y + Inches(0.8), bw - Inches(0.2), Inches(1), sub.split("\n"), 13,
                WHITE if light else INK, align=PP_ALIGN.CENTER, spacing=0)
        del b
        if i < n - 1:
            arrow(s, x + bw + Emu(20000), y + Inches(0.95), x + bw + gap - Emu(20000), y + Inches(0.95), ACCENT)
    bullets(s, MARGIN, Inches(4.5), Inches(6), Inches(2.3), [
        "Voice to confirmation in ~6 s |(STT + Translation + Gemini + TTS)",
        "Joins a cluster of 147 requests / 133 unique citizens |(sample data)",
        "Evidence brief in ~5 s |with an automated number check",
    ], 16)
    bullets(s, Inches(7), Inches(4.5), Inches(5.7), Inches(2.3), [
        "Citizen app |EN / हिन्दी / తెలుగు · text, voice, chat bot",
        "Officer dashboard |map, ranking, policy lens, briefs",
        "Status closes the loop |अनुशंसित (Recommended) in Hindi",
    ], 16)
    notes(s, "Timings measured on 2026-09-30 against real Google APIs from the Cloud Run image.")


def slide_ai(prs):
    s = base(prs, "Google AI does the understanding. Rules keep it honest.", "AI / technical execution · 25%", 4)
    rows = [
        ("Gemini 2.5 Flash (Vertex AI)", "Schema-validated extraction: fixed taxonomy, urgency, vulnerable groups, "
                                         "confidence, missing info, one clarification question"),
        ("Gemini embeddings", "Semantic match of a new request to nearby demand clusters"),
        ("Speech-to-Text · Translation · TTS", "Hindi / Telugu / English voice in, original kept, spoken confirmation out"),
        ("Gemini evidence brief", "Written only from structured data; every number verified against the input"),
        ("Deterministic Priority Score", "Transparent formula; AI never sets the rank"),
        ("Maps Geocoding + JS API · BigQuery · Cloud Storage", "Location fallback, hotspot map, analytics sink, voice notes"),
    ]
    y = Inches(1.8)
    for name, what in rows:
        box(s, MARGIN, y, Inches(4.3), Inches(0.66), BRAND)
        textbox(s, MARGIN + Inches(0.15), y, Inches(4.0), Inches(0.66), name, 15, WHITE, True, anchor=MSO_ANCHOR.MIDDLE)
        box(s, MARGIN + Inches(4.4), y, W - 2 * MARGIN - Inches(4.4), Inches(0.66), BG_SOFT)
        textbox(s, MARGIN + Inches(4.6), y, W - 2 * MARGIN - Inches(4.8), Inches(0.66), what, 15, INK,
                anchor=MSO_ANCHOR.MIDDLE)
        y += Inches(0.76)
    textbox(s, MARGIN, Inches(6.45), W - 2 * MARGIN, Inches(0.5),
            "Live eval (gemini-2.5-flash, extract_v1): 100% category accuracy on 39 EN/HI/TE requests · "
            "0 invented numbers · 0 invented places.  Template-labelled sample, a sanity check, not a field result.",
            13, MUTED)
    notes(s, "Stress separation: observed data -> AI interpretation -> recommendation. Every AI record stores "
             "model_name, model_version, prompt_version.")


def slide_trust(prs):
    s = base(prs, "Built to be trusted by a district officer", "Responsible AI", 5)
    items = [
        ("No invented facts", ["Numbers the citizen did not say are removed.", "Brief numbers are checked against the input data."]),
        ("Provenance everywhere", ["model_name / model_version / prompt_version on every AI record.", "Source + year on every data value."]),
        ("Human in the loop", ["Approve for field verification / defer / reject.", "Weight changes are logged for audit."]),
        ("Honest about data", ["Synthetic sample data is labelled in files, API and UI.", "Badge shows live / demo / fallback per integration."]),
        ("Fairness", ["Unique citizens per 10k people: repeat messages and big villages don't dominate.", "Vulnerability weight (SC/ST, slum share, literacy)."]),
        ("Graceful degradation", ["Every Google service has a labelled fallback,", "so the journey never breaks during an outage or quota spike."]),
    ]
    cw = (W - 2 * MARGIN - Inches(0.3) * 2) / 3
    for i, (t, b) in enumerate(items):
        r, c = divmod(i, 3)
        card(s, MARGIN + c * (cw + Inches(0.3)), Inches(1.8) + r * Inches(2.45), cw, Inches(2.2), t, b, size=15)


def slide_score(prs):
    s = base(prs, "A Priority Score officers can explain in a meeting", "Problem-solution fit · Officer view", 6)
    box(s, MARGIN, Inches(1.8), W - 2 * MARGIN, Inches(1.0), RGBColor(0xE8, 0xEF, 0xF8))
    textbox(s, MARGIN + Inches(0.3), Inches(1.8), W - 2 * MARGIN - Inches(0.6), Inches(1.0),
            "Score = 100 × (Demand·30 + Infra gap·30 + Vulnerability·20 + Trend·10 − Investment coverage·10) / 90",
            18, BRAND, True, anchor=MSO_ANCHOR.MIDDLE)
    factors = [("Demand", "recency-weighted unique citizens per 10k people"),
               ("Infra gap", "category-specific indicator (e.g. tap-water coverage)"),
               ("Vulnerability", "SC/ST or slum share, literacy, aspirational district"),
               ("Trend", "last 30 days vs the 30 before"),
               ("− Investment", "population already covered by sanctioned works")]
    cw = (W - 2 * MARGIN - Inches(0.2) * 4) / 5
    for i, (t, d) in enumerate(factors):
        card(s, MARGIN + i * (cw + Inches(0.2)), Inches(3.05), cw, Inches(1.75), t, d, size=14,
             title_color=ACCENT if t.startswith("−") else BRAND)
    bullets(s, MARGIN, Inches(5.05), W - 2 * MARGIN, Inches(1.8), [
        "Policy lens: |officers move the weights, the ranking updates instantly, the change is logged (and sent to BigQuery).",
        "Example: |Sonbarsa bridge cluster, Gaya: 85.6 / 100, rank 1 of 7 in Bihar (synthetic sample data).",
        "Missing data is visible: |a missing gap indicator scores a neutral 0.5 and is flagged in the brief.",
    ], 16)


def slide_reach(prs):
    s = base(prs, "Depth and reach: languages, channels, states", "Depth & reach across India · 20%", 7)
    cols = [
        ("3 languages", ["English, हिन्दी, తెలుగు in UI, speech, translation and confirmations",
                         "Adding a language = BCP-47 code + UI strings"]),
        ("3 channels", ["Web text", "Web voice notes", "Chat bot (Telegram webhook)", "Roadmap: WhatsApp, IVR, assisted capture"]),
        ("3 states, 3 data shapes", ["Bihar · villages · bridges & roads",
                                     "Andhra Pradesh · habitations · drinking water",
                                     "Maharashtra · Pune wards · public transport"]),
    ]
    cw = (W - 2 * MARGIN - Inches(0.3) * 2) / 3
    for i, (t, b) in enumerate(cols):
        card(s, MARGIN + i * (cw + Inches(0.3)), Inches(1.8), cw, Inches(3.0), t, b, size=16)
    textbox(s, MARGIN, Inches(5.1), W - 2 * MARGIN, Inches(1.4),
            ["Rural and urban, three language families, three sectors: one platform, one canonical schema, "
             "the same AI services and APIs.",
             "Reach target: every Gram Panchayat (≈2.5 lakh) and urban ward."], 18, INK)


def slide_interop(prs):
    s = base(prs, "A new state is configuration, not code", "Interoperability · state onboarding", 8)
    states = [("Bihar", "BR", "Hindi-transliterated CSV\n(yojana suchi)"),
              ("Andhra Pradesh", "AP", "Nested JSON,\nSC + ST columns"),
              ("Maharashtra", "MH", "Ward CSV,\nslum share")]
    y = Inches(1.9)
    for i, (n, code, d) in enumerate(states):
        yy = y + i * Inches(1.45)
        card(s, MARGIN, yy, Inches(3.2), Inches(1.25), n, d.split("\n"), size=13)
        arrow(s, MARGIN + Inches(3.25), yy + Inches(0.62), MARGIN + Inches(4.05), yy + Inches(0.62), ACCENT)
        pill(s, MARGIN + Inches(4.1), yy + Inches(0.3), Inches(2.0), Inches(0.65), f"{code}.json adapter",
             BG_SOFT, BRAND, 14)
        arrow(s, MARGIN + Inches(6.15), yy + Inches(0.62), MARGIN + Inches(6.95), Inches(3.55), ACCENT)
    box(s, MARGIN + Inches(7.0), Inches(2.4), Inches(2.4), Inches(2.3), BRAND)
    textbox(s, MARGIN + Inches(7.1), Inches(2.5), Inches(2.2), Inches(2.1),
            ["Canonical schema", "admin unit · indicator · investment · request · cluster"], 16, WHITE, True,
            PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
    arrow(s, MARGIN + Inches(9.45), Inches(3.55), MARGIN + Inches(10.05), Inches(3.55), ACCENT)
    card(s, MARGIN + Inches(10.1), Inches(2.4), Inches(2.0), Inches(2.3), "Shared", ["AI services", "Scoring", "Briefs", "APIs"], size=14)
    textbox(s, MARGIN, Inches(6.3), W - 2 * MARGIN, Inches(0.6),
            "Onboarding (PRD §40): register state → languages → LGD codes → data sources → field mapping → validate "
            "(tests check every adapter) → enable channels.", 14, MUTED)


def slide_deploy(prs):
    s = base(prs, "Deployable today, scalable by design", "Deployability & scalability · 20%", 9)
    layers = [
        ("Frontends", "Next.js citizen app + officer dashboard on Vercel (one project per app)", BG_SOFT),
        ("API", "FastAPI container on Cloud Run, asia-south1 · service account · keys in Secret Manager", BG_SOFT),
        ("AI", "Gemini 2.5 Flash + embeddings on Vertex AI · Speech-to-Text · Translation · Text-to-Speech", RGBColor(0xE8, 0xEF, 0xF8)),
        ("Data", "BigQuery analytics sink · Cloud Storage voice notes · Maps Geocoding / JS API", BG_SOFT),
    ]
    y = Inches(1.8)
    for name, what, fill in layers:
        box(s, MARGIN, y, Inches(2.2), Inches(0.8), BRAND)
        textbox(s, MARGIN, y, Inches(2.2), Inches(0.8), name, 17, WHITE, True, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
        box(s, MARGIN + Inches(2.3), y, W - 2 * MARGIN - Inches(2.3), Inches(0.8), fill)
        textbox(s, MARGIN + Inches(2.5), y, W - 2 * MARGIN - Inches(2.7), Inches(0.8), what, 16, INK,
                anchor=MSO_ANCHOR.MIDDLE)
        y += Inches(0.92)
    bullets(s, MARGIN, Inches(5.6), Inches(6), Inches(1.4), [
        "One command |deploy.sh api · Cloud Build image",
        "Config, not forks |states, models, weights, CORS from env",
    ], 15)
    bullets(s, Inches(7), Inches(5.6), Inches(5.7), Inches(1.4), [
        "Scale path |BigQuery for millions of requests, Cloud Run autoscaling",
        "Next |Firestore serving store, Firebase auth, RBAC",
    ], 15)


def slide_impact(prs):
    s = base(prs, "Impact: spending follows measured need", "Impact potential · 15%", 10)
    phases = [("Hackathon", "3 states · 3 languages · 3 channels"), ("District pilot", "1 aspirational district · WhatsApp · CSC-assisted capture"),
              ("State", "Grievance-system integration · more languages · IVR"), ("National", "Shared data contracts · de-identified exchange")]
    cw = (W - 2 * MARGIN - Inches(0.35) * 3) / 4
    for i, (t, d) in enumerate(phases):
        x = MARGIN + i * (cw + Inches(0.35))
        card(s, x, Inches(1.9), cw, Inches(1.8), t, d, fill=BG_SOFT if i else RGBColor(0xE8, 0xEF, 0xF8), size=15)
        if i < 3:
            arrow(s, x + cw + Emu(20000), Inches(2.8), x + cw + Inches(0.35) - Emu(20000), Inches(2.8), ACCENT)
    bullets(s, MARGIN, Inches(4.1), W - 2 * MARGIN, Inches(2.6), [
        "Citizens: |a voice in their own language, and a status update instead of silence.",
        "Officers: |a defensible, auditable ranking with evidence, in minutes instead of weeks.",
        "Governments: |share of capital spending aligned with measured demand; fewer unaddressed high-priority gaps.",
        "Measured by: |requests captured, citizens receiving updates, recommendations adopted into district plans.",
    ], 17)


def slide_brics(prs):
    s = base(prs, "Built for India, portable across borders", "Cross-border / BRICS portability", 11)
    swaps = [("Admin units", "LGD codes → any national registry (e.g. IBGE municipalities, OKTMO, Stats SA wards)"),
             ("Languages", "Add a BCP-47 code: Speech, Translation and Gemini already cover Portuguese, Russian, "
                           "Chinese, isiZulu, Arabic…"),
             ("Data sources", "A new adapter JSON per ministry or province: no code changes"),
             ("Channels", "Webhook pattern fits WhatsApp, Telegram, WeChat-style bots or IVR"),
             ("Governance", "Human approval, provenance and number-grounding are built into the pipeline, not bolted on")]
    y = Inches(1.8)
    for k, v in swaps:
        pill(s, MARGIN, y + Inches(0.08), Inches(2.4), Inches(0.6), k, BRAND, WHITE, 15)
        textbox(s, MARGIN + Inches(2.7), y, W - 2 * MARGIN - Inches(2.7), Inches(0.8), v, 17, INK,
                anchor=MSO_ANCHOR.MIDDLE)
        y += Inches(0.88)
    textbox(s, MARGIN, Inches(6.3), W - 2 * MARGIN, Inches(0.6),
            "Open schemas and APIs make JanVaani a candidate digital public good for any country's local planning.",
            16, BRAND, True)


def slide_status(prs):
    s = base(prs, "What is live today, and what we need next", "Status", 12)
    card(s, MARGIN, Inches(1.8), Inches(5.9), Inches(4.6), "Live now", [
        "Gemini 2.5 Flash + embeddings on Vertex AI",
        "Cloud Speech-to-Text, Translation, Text-to-Speech",
        "Maps Geocoding + Maps JavaScript API",
        "BigQuery sink · Cloud Storage voice notes",
        "API on Cloud Run · apps on Vercel",
        "3 states · 3 languages · text, voice, chat bot",
        "Public repo · README · tests · live eval script",
    ], fill=RGBColor(0xE9, 0xF5, 0xEE), title_color=GREEN, size=16)
    card(s, Inches(6.9), Inches(1.8), Inches(5.8), Inches(4.6), "Next", [
        "Telegram / WhatsApp delivery (bot token, BSP)",
        "Firebase auth + officer RBAC by geography",
        "Real LGD, Census and JJM / PMGSY data feeds",
        "Firestore serving store for multi-instance scale",
        "Field pilot in one aspirational district",
        "Photo evidence, impact view, demand forecasting",
    ], title_color=ACCENT, size=16)
    textbox(s, MARGIN, Inches(6.55), W - 2 * MARGIN, Inches(0.4),
            "All figures in this deck come from synthetic sample data, labelled as such in the product.", 12, MUTED)


def main() -> None:
    prs = Presentation()
    prs.slide_width, prs.slide_height = W, H
    for build in (slide_title, slide_problem, slide_journey, slide_ai, slide_trust, slide_score, slide_reach,
                  slide_interop, slide_deploy, slide_impact, slide_brics, slide_status):
        build(prs)
    prs.save(OUT)
    print(f"wrote {OUT} ({len(prs.slides)} slides)")


if __name__ == "__main__":
    main()
