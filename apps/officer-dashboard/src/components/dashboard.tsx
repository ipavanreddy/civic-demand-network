"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { apiGet, apiPost, qs, timeAgo } from "@/lib/api";
import type { Analytics, Hotspot, Ranking, RecommendationDetail as Detail, StateInfo, Taxonomy, Weights } from "@/lib/types";
import { HotspotMap } from "./hotspot-map";
import { InteropView } from "./interop-view";
import { FactorLegend, RankingTable } from "./ranking-table";
import { RecommendationDetail } from "./recommendation-detail";
import { DEFAULT_WEIGHTS, WeightsPanel } from "./weights-panel";

type WeightLogEntry = { at: string; officer: string; to: Weights; scope: string };
const INDIA: [number, number] = [21.5, 80.5];

function Kpi({ label, value, hint }: { label: string; value: string | number; hint?: string }) {
  return (
    <div className="rounded-lg border bg-card p-3">
      <div className="text-xs text-muted-foreground">{label}</div>
      <div className="text-2xl font-semibold tabular-nums">{typeof value === "number" ? value.toLocaleString("en-IN") : value}</div>
      {hint && <div className="text-[11px] text-muted-foreground">{hint}</div>}
    </div>
  );
}

function Select({ label, value, onChange, options }: {
  label: string; value: string; onChange: (v: string) => void; options: { value: string; label: string }[];
}) {
  return (
    <label className="flex flex-col gap-1 text-xs text-muted-foreground">
      {label}
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="h-8 min-w-40 rounded-md border bg-background px-2 text-sm text-foreground"
      >
        {options.map((o) => (
          <option key={o.value} value={o.value}>{o.label}</option>
        ))}
      </select>
    </label>
  );
}

export function Dashboard() {
  const [states, setStates] = useState<StateInfo[]>([]);
  const [taxonomy, setTaxonomy] = useState<Taxonomy | null>(null);
  const [scope, setScope] = useState({ state: "", district: "", category: "" });
  const [ranking, setRanking] = useState<Ranking | null>(null);
  const [hotspots, setHotspots] = useState<Hotspot[]>([]);
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [weights, setWeights] = useState<Weights>(DEFAULT_WEIGHTS);
  const [log, setLog] = useState<WeightLogEntry[]>([]);
  const [selected, setSelected] = useState<string | null>(null);
  const [detail, setDetail] = useState<Detail | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [version, setVersion] = useState(0);

  const params = useMemo(
    () => ({ state: scope.state || null, district: scope.district || null, category: scope.category || null }),
    [scope],
  );

  useEffect(() => {
    Promise.all([apiGet<StateInfo[]>("/api/states"), apiGet<Taxonomy>("/api/taxonomy"), apiGet<WeightLogEntry[]>("/api/recommendations/weights-log")])
      .then(([s, t, l]) => {
        setStates(s);
        setTaxonomy(t);
        setLog(l);
      })
      .catch((e) => setError(String(e)));
  }, []);

  useEffect(() => {
    let live = true;
    Promise.all([
      apiGet<Ranking>(`/api/recommendations${qs(params)}`),
      apiGet<{ cells: Hotspot[] }>(`/api/hotspots${qs(params)}`),
      apiGet<Analytics>(`/api/analytics${qs({ state: params.state, district: params.district })}`),
    ])
      .then(([r, h, a]) => {
        if (!live) return;
        setRanking(r);
        setWeights(r.weights);
        setHotspots(h.cells);
        setAnalytics(a);
        setError(null);
        setSelected((cur) => (cur && r.items.some((i) => i.recommendation_id === cur) ? cur : r.items[0]?.recommendation_id ?? null));
      })
      .catch((e) => live && setError(`${e} (is the API running on :8010?)`));
    return () => {
      live = false;
    };
  }, [params, version]);

  useEffect(() => {
    if (!selected) return;
    let live = true;
    apiGet<Detail>(`/api/recommendations/${selected}${qs(params)}`)
      .then((d) => live && setDetail(d))
      .catch((e) => live && setError(String(e)));
    return () => {
      live = false;
    };
  }, [selected, params, version]);

  const apply = useCallback(
    async (w: Weights) => {
      setBusy(true);
      try {
        const r = await apiPost<Ranking>("/api/recommendations/score", { weights: w, ...params, officer: "planning-officer-demo" });
        setRanking(r);
        setLog(await apiGet<WeightLogEntry[]>("/api/recommendations/weights-log"));
        setVersion((v) => v + 1);
      } catch (e) {
        setError(String(e));
      } finally {
        setBusy(false);
      }
    },
    [params],
  );

  const stateInfo = states.find((s) => s.state_code === scope.state);
  const [center, zoom] = useMemo<[[number, number], number]>(() => {
    if (!stateInfo) return [INDIA, 5];
    if (scope.district && ranking?.items.length) {
      const pts = ranking.items.filter((i) => i.lat != null);
      if (pts.length) {
        const lat = pts.reduce((s, p) => s + (p.lat ?? 0), 0) / pts.length;
        const lng = pts.reduce((s, p) => s + (p.lng ?? 0), 0) / pts.length;
        return [[lat, lng], 9];
      }
    }
    return [stateInfo.map_center, 8];
  }, [stateInfo, scope.district, ranking]);

  const categories = taxonomy?.categories ?? [];

  return (
    <div className="flex flex-col gap-4">
      {/* Scope: India -> State -> District (+ category filter) */}
      <div className="flex flex-wrap items-end gap-3">
        <nav className="mr-2 flex items-center gap-1 text-sm">
          <button className="font-medium underline-offset-2 hover:underline" onClick={() => setScope({ state: "", district: "", category: scope.category })}>
            India
          </button>
          {stateInfo && (
            <>
              <span className="text-muted-foreground">›</span>
              <button className="font-medium underline-offset-2 hover:underline" onClick={() => setScope({ ...scope, district: "" })}>
                {stateInfo.name}
              </button>
            </>
          )}
          {scope.district && (
            <>
              <span className="text-muted-foreground">›</span>
              <span className="font-medium">{stateInfo?.districts.find((d) => d.code === scope.district)?.name}</span>
            </>
          )}
        </nav>
        <Select
          label="State"
          value={scope.state}
          onChange={(v) => setScope({ state: v, district: "", category: scope.category })}
          options={[{ value: "", label: "All India" }, ...states.map((s) => ({ value: s.state_code, label: s.name }))]}
        />
        <Select
          label="District"
          value={scope.district}
          onChange={(v) => setScope({ ...scope, district: v })}
          options={[{ value: "", label: stateInfo ? "All districts" : "Select a state first" }, ...(stateInfo?.districts ?? []).map((d) => ({ value: d.code, label: d.name }))]}
        />
        <Select
          label="Category"
          value={scope.category}
          onChange={(v) => setScope({ ...scope, category: v })}
          options={[{ value: "", label: "All categories" }, ...categories.map((c) => ({ value: c.id, label: c.label.en }))]}
        />
      </div>

      {error && <p className="rounded bg-red-50 px-3 py-2 text-sm text-red-800">{error}</p>}

      {analytics && (
        <div className="grid grid-cols-2 gap-3 md:grid-cols-3 lg:grid-cols-6">
          <Kpi label="Requests received" value={analytics.requests} hint={`${Math.round(analytics.synthetic_share * 100)}% synthetic sample`} />
          <Kpi label="Unique citizens" value={analytics.unique_citizens} />
          <Kpi label="Demand clusters" value={analytics.clusters} />
          <Kpi label="Top category" value={analytics.top_categories[0]?.label ?? "–"} hint={`${analytics.top_categories[0]?.requests ?? 0} requests`} />
          <Kpi label="Projects on record" value={analytics.investments_in_scope} hint="sample investment data" />
          <Kpi
            label="Data freshness"
            value={timeAgo(analytics.freshness.citizen_requests_last_received)}
            hint={`last citizen request · indicators ${analytics.freshness.indicator_years.join(", ")} (Census 2011 + sample)`}
          />
        </div>
      )}

      <Tabs defaultValue="priorities">
        <TabsList>
          <TabsTrigger value="priorities">Priorities</TabsTrigger>
          <TabsTrigger value="interop">Interoperability</TabsTrigger>
        </TabsList>
        <TabsContent value="priorities" className="flex flex-col gap-4">
          <div className="grid gap-4 lg:grid-cols-[1fr_20rem]">
            <Card className="overflow-hidden">
              <CardHeader>
                <CardTitle>Demand hotspots · {ranking?.scope.label ?? "…"}</CardTitle>
              </CardHeader>
              <CardContent className="h-[440px]">
                <HotspotMap
                  hotspots={hotspots}
                  recommendations={ranking?.items ?? []}
                  center={center}
                  zoom={zoom}
                  selected={selected}
                  onSelect={setSelected}
                />
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle>Policy lens (weights)</CardTitle>
              </CardHeader>
              <CardContent>
                <WeightsPanel weights={weights} onChange={setWeights} onApply={apply} busy={busy} log={log} />
              </CardContent>
            </Card>
          </div>
          {analytics && !scope.district && analytics.by_district.length > 1 && (
            <div className="flex flex-wrap gap-2 text-xs">
              <span className="text-muted-foreground">Drill down:</span>
              {analytics.by_district.map((d) => (
                <button
                  key={d.code}
                  className="rounded-full border px-2 py-0.5 hover:bg-muted"
                  onClick={() => setScope({ ...scope, state: d.state, district: d.code })}
                >
                  {d.name} ({d.requests})
                </button>
              ))}
            </div>
          )}
          <div className="grid gap-4 lg:grid-cols-[minmax(0,26rem)_1fr]">
            <Card>
              <CardHeader>
                <CardTitle>Ranked recommendations</CardTitle>
                <FactorLegend />
              </CardHeader>
              <CardContent className="max-h-[900px] overflow-auto px-2">
                {ranking && <RankingTable rows={ranking.items} selected={selected} onSelect={setSelected} />}
                {ranking && <p className="px-2 pt-2 text-[11px] text-muted-foreground">Score = {ranking.formula}</p>}
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-4">
                {detail && ranking ? (
                  <RecommendationDetail
                    key={`${detail.recommendation_id}-${detail.priority_score}-${detail.brief?.generated_at ?? ""}`}
                    detail={detail}
                    scope={ranking.scope}
                    onChanged={() => setVersion((v) => v + 1)}
                  />
                ) : (
                  <p className="text-sm text-muted-foreground">Select a recommendation.</p>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>
        <TabsContent value="interop">
          <Card>
            <CardHeader>
              <CardTitle>State-specific data, common interfaces</CardTitle>
            </CardHeader>
            <CardContent>{states.length > 0 && <InteropView states={states} />}</CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
