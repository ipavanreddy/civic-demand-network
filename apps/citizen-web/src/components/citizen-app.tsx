"use client";

import { useEffect, useRef, useState } from "react";
import { Mic, Square, Volume2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import { ChatBot } from "@/components/chat-bot";
import { apiGet, apiPost, apiPostForm } from "@/lib/api";
import { LANGS, STRINGS, URGENCY, type Lang } from "@/lib/i18n";
import type { RequestView, Scenario, StateInfo, Taxonomy } from "@/lib/types";

const CITIZEN_REF = "citizen-web-demo-profile";

function detectLang(text: string, fallback: Lang): Lang {
  if (/[ఀ-౿]/.test(text)) return "te";
  if (/[ऀ-ॿ]/.test(text)) return "hi";
  return /[a-z]/i.test(text) ? "en" : fallback;
}

function speak(view: RequestView) {
  const s = view.message.speech;
  if (s?.audio_base64 && s.mime) {
    void new Audio(`data:${s.mime};base64,${s.audio_base64}`).play();
    return;
  }
  if (typeof window === "undefined" || !("speechSynthesis" in window)) return;
  const u = new SpeechSynthesisUtterance(view.message.text);
  u.lang = LANGS.find((l) => l.code === view.message.language)?.bcp47 ?? "en-IN";
  window.speechSynthesis.cancel();
  window.speechSynthesis.speak(u);
}

function Row({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="grid grid-cols-[8.5rem_1fr] gap-2 py-1 text-sm">
      <span className="text-muted-foreground">{label}</span>
      <span>{children}</span>
    </div>
  );
}

export function CitizenApp() {
  const [lang, setLang] = useState<Lang>("hi");
  const [states, setStates] = useState<StateInfo[]>([]);
  const [taxonomy, setTaxonomy] = useState<Taxonomy | null>(null);
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [stateCode, setStateCode] = useState("BR");
  const [district, setDistrict] = useState("BR.GAY");
  const [text, setText] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [view, setView] = useState<RequestView | null>(null);
  const [correcting, setCorrecting] = useState(false);
  const [fixCategory, setFixCategory] = useState("");
  const [fixPlace, setFixPlace] = useState("");
  const [answer, setAnswer] = useState("");
  const [recording, setRecording] = useState(false);
  const [lookupId, setLookupId] = useState("");
  const [lookup, setLookup] = useState<RequestView | null>(null);
  const recorder = useRef<MediaRecorder | null>(null);
  const t = STRINGS[lang];

  useEffect(() => {
    Promise.all([apiGet<StateInfo[]>("/api/states"), apiGet<Taxonomy>("/api/taxonomy"), apiGet<Scenario[]>("/api/demo/scenarios")])
      .then(([s, tx, sc]) => {
        setStates(s);
        setTaxonomy(tx);
        setScenarios(sc);
      })
      .catch((e) => setError(`${e} (is the API running on :8010?)`));
  }, []);

  const catLabel = (id: string) => taxonomy?.categories.find((c) => c.id === id)?.label[lang] ?? id;
  const stateInfo = states.find((s) => s.state_code === stateCode);

  async function run(p: Promise<RequestView>) {
    setBusy(true);
    setError(null);
    try {
      const v = await p;
      setView(v);
      setCorrecting(false);
      setAnswer("");
      setLookupId(v.request.request_id);
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  }

  function submitText() {
    const language = detectLang(text, lang);
    void run(apiPost<RequestView>("/api/requests", {
      text, language, channel: "web", citizen_ref: CITIZEN_REF, state: stateCode || null, district: district || null,
    }));
  }

  function submitAudio(blob: Blob, filename: string) {
    const form = new FormData();
    form.append("audio", blob, filename);
    form.append("language", lang);
    if (stateCode) form.append("state", stateCode);
    if (district) form.append("district", district);
    form.append("citizen_ref", CITIZEN_REF);
    void run(apiPostForm<RequestView>("/api/requests/voice", form));
  }

  async function toggleRecording() {
    if (recording) {
      recorder.current?.stop();
      setRecording(false);
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const rec = new MediaRecorder(stream);
      const chunks: Blob[] = [];
      rec.ondataavailable = (e) => chunks.push(e.data);
      rec.onstop = () => {
        stream.getTracks().forEach((tr) => tr.stop());
        submitAudio(new Blob(chunks, { type: rec.mimeType || "audio/webm" }), "voice-note.webm");
      };
      rec.start();
      recorder.current = rec;
      setRecording(true);
    } catch {
      setError(t.micError);
    }
  }

  function confirm(body: Record<string, string | null> = {}) {
    if (!view) return;
    void run(apiPost<RequestView>(`/api/requests/${view.request.request_id}/confirm`, body));
  }

  function applyScenario(s: Scenario) {
    setLang(s.language);
    setStateCode(s.state);
    setDistrict(s.district ?? "");
    setText(s.text_original);
    setView(null);
  }

  const loc = view?.location;
  const confirmed = Boolean(view?.cluster);

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-wrap items-center gap-2" role="group" aria-label="Language">
        {LANGS.map((l) => (
          <button
            key={l.code}
            onClick={() => setLang(l.code)}
            className={`rounded-full border px-3 py-1 text-sm ${lang === l.code ? "bg-foreground text-background" : ""}`}
          >
            {l.label}
          </button>
        ))}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>{t.subtitle}</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col gap-4">
          <div className="flex flex-wrap gap-3">
            <label className="flex flex-col gap-1 text-xs text-muted-foreground">
              {t.state}
              <select
                className="h-9 rounded-md border bg-background px-2 text-sm text-foreground"
                value={stateCode}
                onChange={(e) => {
                  setStateCode(e.target.value);
                  setDistrict("");
                }}
              >
                {states.map((s) => (
                  <option key={s.state_code} value={s.state_code}>
                    {s.name} · {s.name_local}
                  </option>
                ))}
              </select>
            </label>
            <label className="flex flex-col gap-1 text-xs text-muted-foreground">
              {t.district}
              <select
                className="h-9 rounded-md border bg-background px-2 text-sm text-foreground"
                value={district}
                onChange={(e) => setDistrict(e.target.value)}
              >
                <option value="">–</option>
                {stateInfo?.districts.map((d) => (
                  <option key={d.code} value={d.code}>{d.name}</option>
                ))}
              </select>
            </label>
          </div>

          {scenarios.length > 0 && (
            <div className="flex flex-wrap items-center gap-2 text-xs">
              <span className="text-muted-foreground">{t.scenarios}:</span>
              {scenarios.map((s) => (
                <button key={s.id} className="rounded-full border px-2.5 py-1 hover:bg-muted" onClick={() => applyScenario(s)}>
                  {s.scenario} · {s.state} · {LANGS.find((l) => l.code === s.language)?.label}
                </button>
              ))}
            </div>
          )}

          <Tabs defaultValue="type">
            <TabsList>
              <TabsTrigger value="type">{t.typeTab}</TabsTrigger>
              <TabsTrigger value="speak">{t.speakTab}</TabsTrigger>
              <TabsTrigger value="chat">{t.chatTab}</TabsTrigger>
            </TabsList>
            <TabsContent value="type" className="flex flex-col gap-3">
              <Textarea
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder={t.placeholder}
                className="min-h-28 text-base"
                lang={lang}
              />
              <Button size="lg" onClick={submitText} disabled={busy || text.trim().length < 3}>
                {busy ? t.sending : t.submit}
              </Button>
            </TabsContent>
            <TabsContent value="speak" className="flex flex-col items-start gap-3">
              <Button size="lg" variant={recording ? "destructive" : "default"} onClick={toggleRecording} disabled={busy}>
                {recording ? <Square /> : <Mic />} {recording ? t.stop : t.record}
              </Button>
              {recording && <p className="animate-pulse text-sm text-red-700">{t.recordingHint}</p>}
              <label className="text-sm text-muted-foreground">
                {t.upload}{" "}
                <input
                  type="file"
                  accept="audio/*"
                  className="text-sm"
                  onChange={(e) => {
                    const f = e.target.files?.[0];
                    if (f) submitAudio(f, f.name);
                  }}
                />
              </label>
            </TabsContent>
            <TabsContent value="chat">
              <ChatBot state={stateCode} lang={lang} t={t} />
            </TabsContent>
          </Tabs>
          {error && <p className="rounded bg-red-50 px-3 py-2 text-sm text-red-800">{error}</p>}
        </CardContent>
      </Card>

      {view && (
        <Card>
          <CardHeader>
            <CardTitle className="flex flex-wrap items-center justify-between gap-2">
              <span>{t.understood}</span>
              <span className="text-sm font-normal text-muted-foreground">
                {t.requestId}: <b className="text-foreground">{view.request.request_id}</b> · {t.status}: {view.status_label}
              </span>
            </CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col gap-4">
            {view.demo_mode && (
              <p className="rounded bg-amber-50 px-3 py-2 text-xs text-amber-900 ring-1 ring-amber-200">
                Demo mode: {[view.speech?.note, view.provenance?.note, view.translation?.note].filter(Boolean).join(" ") || "sample data"}
              </p>
            )}
            <div className="rounded-lg bg-muted/60 p-3 text-base" lang={view.message.language}>
              {view.message.text}
              <div className="mt-2">
                <Button variant="outline" size="sm" onClick={() => speak(view)}>
                  <Volume2 /> {t.play}
                </Button>
                <span className="ml-2 text-xs text-muted-foreground">
                  {view.message.speech?.mode === "real" ? view.message.speech.provider : t.demoVoice}
                </span>
              </div>
            </div>

            <div className="divide-y">
              <Row label={t.original}>{view.request.text_original}</Row>
              {view.request.language !== "en" && <Row label={t.translation}>{view.request.text_en}</Row>}
              <Row label={t.category}>
                {catLabel(view.request.category)} {view.request.sub_category ? `· ${view.request.sub_category.replaceAll("_", " ")}` : ""}
              </Row>
              <Row label={t.location}>
                {loc?.resolved ? (
                  <>
                    {loc.unit_name}, {loc.block_name}, {loc.district_name}{" "}
                    <span className="text-xs text-muted-foreground">
                      ({t.method}: {loc.method.replace("_", " ")} · {Math.round(loc.confidence * 100)}% · {loc.lgd_unit} · H3 {loc.h3_cell})
                    </span>
                  </>
                ) : (
                  <span className="text-amber-800">?</span>
                )}
              </Row>
              <Row label={t.urgency}>
                {URGENCY[lang][view.request.urgency] ?? view.request.urgency}
                {view.request.urgency_reason ? <span className="text-muted-foreground"> · {view.request.urgency_reason}</span> : null}
              </Row>
              <Row label={t.vulnerable}>{view.request.vulnerable_groups.join(", ") || t.none}</Row>
              <Row label={t.missing}>{view.request.missing_information.join("; ") || t.none}</Row>
              <Row label={t.confidence}>
                {Math.round(view.request.confidence * 100)}%{" "}
                <span className="text-xs text-muted-foreground">
                  ({view.request.model_name} · {view.request.model_version} · {view.request.prompt_version})
                </span>
              </Row>
            </div>

            {view.needs_clarification && (
              <div className="flex flex-col gap-2 rounded-lg border border-amber-300 p-3">
                <p className="font-medium">{t.clarify}: {view.clarification_question}</p>
                {loc?.candidates?.length ? (
                  <div className="flex flex-wrap gap-2">
                    {loc.candidates.map((c) => (
                      <Button key={c.lgd_code} variant="outline" onClick={() => confirm({ lgd_code: c.lgd_code })} disabled={busy}>
                        {c.label}
                      </Button>
                    ))}
                  </div>
                ) : (
                  <div className="flex gap-2">
                    <input
                      className="h-9 flex-1 rounded-md border bg-background px-2 text-sm"
                      placeholder={t.placeText}
                      value={answer}
                      onChange={(e) => setAnswer(e.target.value)}
                    />
                    <Button onClick={() => confirm({ location_text: answer })} disabled={busy || !answer.trim()}>
                      {t.answer}
                    </Button>
                  </div>
                )}
              </div>
            )}

            {!view.needs_clarification && !confirmed && (
              <div className="flex flex-wrap gap-2">
                <Button size="lg" onClick={() => confirm()} disabled={busy}>
                  {t.confirm}
                </Button>
                <Button size="lg" variant="outline" onClick={() => setCorrecting((c) => !c)}>
                  {t.correct}
                </Button>
              </div>
            )}

            {correcting && !confirmed && (
              <div className="flex flex-wrap items-end gap-2 rounded-lg border p-3">
                <label className="flex flex-col gap-1 text-xs text-muted-foreground">
                  {t.category}
                  <select
                    className="h-9 rounded-md border bg-background px-2 text-sm text-foreground"
                    value={fixCategory || view.request.category}
                    onChange={(e) => setFixCategory(e.target.value)}
                  >
                    {taxonomy?.categories.map((c) => (
                      <option key={c.id} value={c.id}>{c.label[lang]}</option>
                    ))}
                  </select>
                </label>
                <label className="flex flex-1 flex-col gap-1 text-xs text-muted-foreground">
                  {t.placeText}
                  <input
                    className="h-9 rounded-md border bg-background px-2 text-sm text-foreground"
                    value={fixPlace}
                    onChange={(e) => setFixPlace(e.target.value)}
                  />
                </label>
                <Button onClick={() => confirm({ category: fixCategory || null, location_text: fixPlace || null })} disabled={busy}>
                  {t.saveCorrection}
                </Button>
              </div>
            )}

            {view.cluster && (
              <div className="flex flex-col gap-2 rounded-lg border border-emerald-300 bg-emerald-50/60 p-3">
                <p className="font-semibold text-emerald-900">
                  {t.joined}: {view.cluster.cluster_id} · {view.cluster.request_count} {t.requests} · {view.cluster.unique_citizens}{" "}
                  {t.citizens}
                </p>
                <p className="text-sm">{view.cluster.summary}</p>
                <p className="text-xs font-medium text-muted-foreground">{t.similar}</p>
                <ul className="list-disc pl-5 text-sm">
                  {view.cluster.representative_quotes.map((q) => (
                    <li key={q}>{q}</li>
                  ))}
                </ul>
              </div>
            )}
            <Button variant="ghost" className="w-fit" onClick={() => { setView(null); setText(""); }}>
              {t.newRequest}
            </Button>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle>{t.checkStatus}</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col gap-2">
          <div className="flex gap-2">
            <input
              className="h-9 flex-1 rounded-md border bg-background px-2 text-sm"
              placeholder="REQ-XXXXXX"
              value={lookupId}
              onChange={(e) => setLookupId(e.target.value.trim())}
            />
            <Button
              variant="outline"
              onClick={() =>
                apiGet<RequestView>(`/api/requests/${lookupId}`)
                  .then(setLookup)
                  .catch((e) => setError(String(e)))
              }
              disabled={!lookupId}
            >
              {t.checkStatus}
            </Button>
          </div>
          {lookup && (
            <p className="text-sm" lang={lookup.message.language}>
              <b>{lookup.status_label}</b> · {lookup.message.text}
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
