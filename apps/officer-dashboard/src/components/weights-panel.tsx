"use client";

import { Button } from "@/components/ui/button";
import type { Weights } from "@/lib/types";

const FACTORS: { key: keyof Weights; label: string; hint: string }[] = [
  { key: "demand", label: "Demand intensity", hint: "recency-weighted unique citizens per 10k people" },
  { key: "infra_gap", label: "Infrastructure gap", hint: "category-specific gap indicator" },
  { key: "vulnerability", label: "Vulnerability", hint: "SC/ST or slum share, literacy, aspirational district" },
  { key: "trend", label: "Demand trend", hint: "last 30 days vs the 30 before" },
  { key: "investment", label: "Investment coverage (−)", hint: "subtracted: sanctioned/ongoing projects" },
];

export const DEFAULT_WEIGHTS: Weights = { demand: 30, infra_gap: 30, vulnerability: 20, trend: 10, investment: 10 };

export function WeightsPanel({
  weights,
  onChange,
  onApply,
  busy,
  log,
}: {
  weights: Weights;
  onChange: (w: Weights) => void;
  onApply: (w: Weights) => void;
  busy: boolean;
  log: { at: string; officer: string; to: Weights; scope: string }[];
}) {
  const isDefault = FACTORS.every((f) => weights[f.key] === DEFAULT_WEIGHTS[f.key]);
  return (
    <div className="flex flex-col gap-3">
      <p className="text-xs text-muted-foreground">
        Policy lens: adjust the weights and apply to re-rank. The score is deterministic; every change is recorded.
      </p>
      {FACTORS.map((f) => (
        <label key={f.key} className="flex flex-col gap-1 text-sm">
          <span className="flex justify-between">
            <span className="font-medium">{f.label}</span>
            <span className="tabular-nums">{weights[f.key]}%</span>
          </span>
          <input
            type="range"
            min={0}
            max={80}
            step={5}
            value={weights[f.key]}
            onChange={(e) => onChange({ ...weights, [f.key]: Number(e.target.value) })}
            className="accent-orange-600"
            aria-label={`${f.label} weight`}
          />
          <span className="text-[11px] text-muted-foreground">{f.hint}</span>
        </label>
      ))}
      <div className="flex gap-2">
        <Button onClick={() => onApply(weights)} disabled={busy}>
          {busy ? "Re-ranking…" : "Apply & re-rank"}
        </Button>
        <Button
          variant="outline"
          disabled={busy || isDefault}
          onClick={() => {
            onChange(DEFAULT_WEIGHTS);
            onApply(DEFAULT_WEIGHTS);
          }}
        >
          PRD defaults
        </Button>
      </div>
      {log.length > 0 && (
        <div className="text-xs">
          <p className="mb-1 font-medium">Weight change log (audit)</p>
          <ul className="max-h-28 space-y-1 overflow-auto text-muted-foreground">
            {log.slice(0, 6).map((e) => (
              <li key={e.at}>
                {new Date(e.at).toLocaleTimeString()} · {e.officer} · D{e.to.demand}/G{e.to.infra_gap}/V{e.to.vulnerability}/T
                {e.to.trend}/I{e.to.investment} · {e.scope}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
