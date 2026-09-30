# Audio transcription prompt (v1, Gemini fallback when Cloud Speech-to-Text is not configured)

Transcribe the attached citizen voice note verbatim in its original language and script
(Hindi in Devanagari, Telugu in Telugu script, English in Latin script). Do not translate,
summarise or add words. Expected language hint: {{language}}.
Return JSON with `transcript` and `language` (one of: en, hi, te).
