"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { apiPost } from "@/lib/api";
import { bandColor } from "@/lib/map-utils";
import type { BriefRecord, Decision, RecommendationDetail as Detail, Scope } from "@/lib/types";

function fmt(v: number | boolean): string {
  if (typeof v === "boolean") return v ? "yes" : "no";
  return v.toLocaleString("en-IN");
}

function Section({ title, tag, children }: { title: string; tag?: string; children: React.ReactNode }) {
  return (
    <section className="flex flex-col gap-2">
      <h3 className="flex items-center gap-2 text-sm font-semibold">
        {title}
        {tag && <span className="rounded bg-muted px-1.5 py-0.5 text-[10px] font-medium text-muted-foreground">{tag}</span>}
      </h3>
      {children}
    </section>
  );
}

export function RecommendationDetail({
  detail,
  scope,
  onChanged,
}: {
  detail: Detail;
  scope: Scope;
  onChanged: () => void;
}) {
  const [brief, setBrief] = useState<BriefRecord | null>(detail.brief);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [note, setNote] = useState("");
  const [decision, setDecision] = useState<Decision | null>(detail.decision);

  async function generate() {
    setBusy(true);
    setError(null);
    try {
      setBrief(
        await apiPost<BriefRecord>(`/api/recommendations/${detail.recommendation_id}/brief`, {
          state: scope.state,
          district: scope.district,
          category: scope.category,
        }),
      );
      onChanged();
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  }

  async function decide(d: Decision["decision"]) {
    const res = await apiPost<Decision>(`/api/recommendations/${detail.recommendation_id}/decision`, {
      decision: d,
      officer: "planning-officer-demo",
      note: note || null,
    });
    setDecision(res);
    onChanged();
  }

  const indicators = detail.indicators.filter((i) => i.indicator_name !== "water_supply_hours_per_day" || detail.category === "drinking_water");

  return (
    <div className="flex flex-col gap-5">
      <header className="flex items-start justify-between gap-4">
        <div>
          <p className="text-xs text-muted-foreground">
            {detail.cluster_id} · rank {detail.rank} of {detail.total_in_scope} in {detail.scope.label} · status {detail.status}
          </p>
          <h2 className="text-lg font-semibold">{detail.title}</h2>
          <p className="text-sm text-muted-foreground">
            {detail.block}, {detail.district} ({detail.state_name}) · population {detail.population.toLocaleString("en-IN")}
          </p>
        </div>
        <div className="text-right">
          <div className="text-3xl font-bold tabular-nums" style={{ color: bandColor(detail.priority_score) }}>
            {detail.priority_score}
            <span className="text-base font-normal text-muted-foreground"> / 100</span>
          </div>
          <div className="text-sm font-medium">{detail.band} priority</div>
        </div>
      </header>

      <Section title="Priority Score breakdown" tag="deterministic">
        <table className="w-full text-xs">
          <thead className="text-left text-muted-foreground">
            <tr>
              <th className="py-1">Factor</th>
              <th>Normalised</th>
              <th>Weight</th>
              <th>Points</th>
            </tr>
          </thead>
          <tbody>
            {detail.breakdown.map((f) => (
              <tr key={f.factor} className="border-t align-top">
                <td className="py-1.5 pr-2">
                  <div className="font-medium">{f.label}</div>
                  <div className="text-muted-foreground">{f.explanation}</div>
                </td>
                <td className="tabular-nums">{f.normalised.toFixed(2)}</td>
                <td className="tabular-nums">{f.weight}%</td>
                <td className={`tabular-nums font-medium ${f.contribution < 0 ? "text-red-700" : ""}`}>{f.contribution.toFixed(1)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </Section>

      <Section title="Citizen demand" tag={detail.is_synthetic ? "synthetic sample requests" : "citizen reports"}>
        <p className="text-sm">
          <b>{detail.request_count}</b> requests from <b>{detail.unique_citizens}</b> unique citizens ·{" "}
          {detail.recent_requests_30d} in the last 30 days · first{" "}
          {detail.first_seen ? new Date(detail.first_seen).toLocaleDateString() : "–"}, last{" "}
          {detail.last_seen ? new Date(detail.last_seen).toLocaleDateString() : "–"}
        </p>
        <ul className="flex flex-col gap-2">
          {detail.quotes.slice(0, 3).map((q) => (
            <li key={q.translated_en} className="rounded border-l-4 border-orange-400 bg-muted/50 px-3 py-2 text-sm">
              “{q.translated_en}”
              {q.language !== "en" && <div className="mt-1 text-xs text-muted-foreground">{q.original}</div>}
            </li>
          ))}
        </ul>
      </Section>

      <Section title="Official data (fused)" tag="sample data">
        <div className="max-h-56 overflow-auto">
          <table className="w-full text-xs">
            <thead className="sticky top-0 bg-card text-left text-muted-foreground">
              <tr>
                <th className="py-1">Place</th>
                <th>Indicator</th>
                <th>Value</th>
                <th>Year</th>
                <th>Source</th>
              </tr>
            </thead>
            <tbody>
              {indicators.map((i) => (
                <tr key={`${i.lgd_code}-${i.indicator_name}`} className="border-t">
                  <td className="py-1 pr-2">{i.unit}</td>
                  <td className="pr-2">{i.indicator_name.replaceAll("_", " ")}</td>
                  <td className="pr-2 tabular-nums">{fmt(i.value)}</td>
                  <td className="pr-2">{i.year}</td>
                  <td className="text-muted-foreground">
                    {i.source}
                    {i.is_sample && <span className="ml-1 rounded bg-amber-100 px-1 text-amber-900">sample</span>}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Section>

      <Section title="Existing investment">
        {detail.investments.length === 0 ? (
          <p className="text-sm text-muted-foreground">No project in this category recorded for these places (sample investment data).</p>
        ) : (
          <ul className="flex flex-col gap-1 text-sm">
            {detail.investments.map((i) => (
              <li key={i.project_id}>
                <b>{i.project_id}</b> {i.title} · {i.status} · ₹{(i.sanctioned_amount_inr / 1e5).toLocaleString("en-IN")} lakh ·
                covers {i.population_covered.toLocaleString("en-IN")} people
                {!i.covers_cluster_area && <span className="text-muted-foreground"> (same block, other places)</span>}
                <span className="ml-1 rounded bg-amber-100 px-1 text-xs text-amber-900">sample</span>
              </li>
            ))}
          </ul>
        )}
      </Section>

      <Section title="AI evidence brief" tag={brief ? (brief.mode === "demo" ? "demo template" : `Gemini · ${brief.model_version}`) : undefined}>
        {!brief && (
          <p className="text-sm text-muted-foreground">
            Gemini explains the ranking using only the structured data above. It never changes the score.
          </p>
        )}
        <div>
          <Button onClick={generate} disabled={busy} variant={brief ? "outline" : "default"}>
            {busy ? "Generating…" : brief ? "Regenerate brief" : "Generate evidence brief"}
          </Button>
          {error && <p className="mt-1 text-xs text-red-700">{error}</p>}
        </div>
        {brief && <BriefView brief={brief} />}
      </Section>

      <Section title="Human decision" tag="required">
        {decision ? (
          <p className="rounded bg-emerald-50 px-3 py-2 text-sm text-emerald-900">
            {decision.decision.replaceAll("_", " ")} by {decision.officer} at {new Date(decision.decided_at).toLocaleString()}
            {decision.note ? ` · “${decision.note}”` : ""}
          </p>
        ) : (
          <p className="text-xs text-muted-foreground">The platform recommends; a Planning Officer decides. Nothing is sanctioned automatically.</p>
        )}
        <textarea
          className="min-h-14 rounded-md border bg-background px-2 py-1 text-sm"
          placeholder="Note for the record (optional)"
          value={note}
          onChange={(e) => setNote(e.target.value)}
        />
        <div className="flex flex-wrap gap-2">
          <Button onClick={() => decide("approve_for_field_verification")}>Approve for field verification</Button>
          <Button variant="outline" onClick={() => decide("defer")}>
            Defer
          </Button>
          <Button variant="destructive" onClick={() => decide("reject")}>
            Reject
          </Button>
        </div>
      </Section>
    </div>
  );
}

function BriefView({ brief }: { brief: BriefRecord }) {
  const b = brief.evidence_brief;
  return (
    <article className="flex flex-col gap-3 rounded-lg border p-3 text-sm">
      <div className="flex flex-wrap items-center gap-2 text-xs">
        <span className={`rounded px-1.5 py-0.5 font-medium ${brief.grounding.ok ? "bg-emerald-100 text-emerald-900" : "bg-red-100 text-red-900"}`}>
          {brief.grounding.ok
            ? `Number check passed: ${brief.grounding.numbers_checked} numbers all found in the input data`
            : `Ungrounded numbers: ${brief.grounding.ungrounded_numbers.join(", ")}`}
        </span>
        <span className="text-muted-foreground">
          {brief.model_name} · {brief.model_version} · prompt {brief.prompt_version} · {new Date(brief.generated_at).toLocaleString()}
        </span>
      </div>
      {brief.note && <p className="text-xs text-amber-800">{brief.note}</p>}
      <h4 className="font-semibold">{b.title}</h4>
      <p>{b.summary}</p>
      <div>
        <p className="font-medium">Citizen demand evidence</p>
        <ul className="list-disc pl-5">{b.demand_evidence.map((x) => <li key={x}>{x}</li>)}</ul>
      </div>
      <div>
        <p className="font-medium">Data evidence</p>
        <ul className="list-disc pl-5">
          {b.data_evidence.map((d) => (
            <li key={d.claim}>
              {d.claim} <span className="text-muted-foreground">({d.source}, {d.year})</span>
            </li>
          ))}
        </ul>
      </div>
      <div>
        <p className="font-medium">Existing investment</p>
        <ul className="list-disc pl-5">{b.investment_context.map((x) => <li key={x}>{x}</li>)}</ul>
      </div>
      <p>
        <span className="font-medium">Estimated beneficiaries:</span>{" "}
        {b.estimated_beneficiaries != null ? b.estimated_beneficiaries.toLocaleString("en-IN") : "not available"} ({b.beneficiaries_basis})
      </p>
      <div>
        <p className="font-medium">Uncertainties</p>
        <ul className="list-disc pl-5 text-amber-900">{b.uncertainties.map((x) => <li key={x}>{x}</li>)}</ul>
      </div>
      <p>
        <span className="font-medium">Suggested next step:</span> {b.next_step}
      </p>
    </article>
  );
}
