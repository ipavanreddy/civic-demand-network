# Translation prompt (v1, Gemini fallback when Cloud Translation is not configured)

Translate the citizen request below into plain English. Keep place names as transliterated
proper nouns. Do not add, remove or infer facts; keep every number exactly as stated.
Return JSON with `text_en` and `detected_language` (one of: en, hi, te).

Source language hint: {{language}}

"""
{{text}}
"""
