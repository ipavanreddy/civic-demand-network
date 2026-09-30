"use client";

import { ArrowDown, ArrowUp } from "lucide-react";
import type { RecommendationRow } from "@/lib/types";
import { bandColor } from "@/lib/map-utils";

const FACTOR_COLORS: Record<string, string> = {
  demand: "bg-orange-500",
  infra_gap: "bg-sky-600",
  vulnerability: "bg-violet-600",
  trend: "bg-emerald-600",
  investment: "bg-slate-400",
};

export function ScoreBar({ row }: { row: RecommendationRow }) {
  return (
    <div className="flex h-2 w-full overflow-hidden rounded bg-muted" title="Positive factor contributions">
      {row.breakdown
        .filter((f) => f.contribution > 0)
        .map((f) => (
          <div key={f.factor} className={FACTOR_COLORS[f.factor]} style={{ width: `${f.contribution}%` }} />
        ))}
    </div>
  );
}

export function FactorLegend() {
  return (
    <div className="flex flex-wrap gap-3 text-[11px] text-muted-foreground">
      {[
        ["demand", "Demand"],
        ["infra_gap", "Infra gap"],
        ["vulnerability", "Vulnerability"],
        ["trend", "Trend"],
      ].map(([k, l]) => (
        <span key={k} className="flex items-center gap-1">
          <span className={`size-2 rounded-sm ${FACTOR_COLORS[k]}`} /> {l}
        </span>
      ))}
      <span>(investment coverage is subtracted)</span>
    </div>
  );
}

export function RankingTable({
  rows,
  selected,
  onSelect,
}: {
  rows: RecommendationRow[];
  selected: string | null;
  onSelect: (id: string) => void;
}) {
  return (
    <ol className="flex flex-col divide-y">
      {rows.map((r) => {
        const delta = r.default_rank != null ? r.default_rank - r.rank : 0;
        return (
          <li key={r.recommendation_id}>
            <button
              onClick={() => onSelect(r.recommendation_id)}
              className={`grid w-full grid-cols-[2.5rem_1fr_4.5rem] items-center gap-3 px-2 py-2.5 text-left hover:bg-muted/60 ${
                selected === r.recommendation_id ? "bg-muted" : ""
              }`}
            >
              <span className="flex flex-col items-center text-sm font-semibold tabular-nums">
                #{r.rank}
                {delta !== 0 && (
                  <span className={`flex items-center text-[10px] ${delta > 0 ? "text-emerald-700" : "text-red-700"}`}>
                    {delta > 0 ? <ArrowUp className="size-3" /> : <ArrowDown className="size-3" />}
                    {Math.abs(delta)}
                  </span>
                )}
              </span>
              <span className="flex min-w-0 flex-col gap-1">
                <span className="truncate text-sm font-medium">{r.title}</span>
                <span className="truncate text-xs text-muted-foreground">
                  {r.block}, {r.district} ({r.state_name}) · {r.request_count} requests · {r.unique_citizens} citizens
                  {r.decision ? ` · ${r.decision.decision.replaceAll("_", " ")}` : ""}
                </span>
                <ScoreBar row={r} />
              </span>
              <span className="flex flex-col items-end">
                <span className="text-lg font-semibold tabular-nums" style={{ color: bandColor(r.priority_score) }}>
                  {r.priority_score}
                </span>
                <span className="text-[11px] text-muted-foreground">{r.band}</span>
              </span>
            </button>
          </li>
        );
      })}
    </ol>
  );
}
