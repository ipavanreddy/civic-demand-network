"use client";

import { useEffect, useState } from "react";
import { apiGet } from "@/lib/api";
import type { StateInfo } from "@/lib/types";

type Interop = {
  state: string;
  raw_unit_record: Record<string, unknown>;
  canonical_unit: Record<string, unknown>;
  canonical_indicators: Record<string, unknown>[];
  raw_investment_record: Record<string, unknown> | null;
  canonical_investment: Record<string, unknown> | null;
  canonical_request_example: Record<string, unknown> | null;
  field_mapping: Record<string, string>;
  indicator_mapping: { canonical: string; columns: string[]; transform: string; source: string }[];
};

function Json({ value }: { value: unknown }) {
  return <pre className="max-h-72 overflow-auto rounded bg-muted p-2 text-[11px] leading-snug">{JSON.stringify(value, null, 2)}</pre>;
}

/** PRD §20-22: state-specific data, common interfaces. Raw state record → adapter → canonical schema. */
export function InteropView({ states }: { states: StateInfo[] }) {
  const [code, setCode] = useState(states[0]?.state_code ?? "BR");
  const [data, setData] = useState<Interop | null>(null);
  const info = states.find((s) => s.state_code === code);

  useEffect(() => {
    let live = true;
    apiGet<Interop>(`/api/states/${code}/interop`).then((d) => live && setData(d));
    return () => {
      live = false;
    };
  }, [code]);

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-wrap items-center gap-2">
        {states.map((s) => (
          <button
            key={s.state_code}
            onClick={() => setCode(s.state_code)}
            className={`rounded-full border px-3 py-1 text-sm ${s.state_code === code ? "bg-foreground text-background" : ""}`}
          >
            {s.name} ({s.name_local})
          </button>
        ))}
      </div>
      {info && (
        <div className="grid gap-2 text-sm sm:grid-cols-4">
          <div><span className="text-muted-foreground">Languages</span><br />{info.languages.join(", ")}</div>
          <div><span className="text-muted-foreground">Units</span><br />{info.units} {info.level_labels.unit}</div>
          <div><span className="text-muted-foreground">Focus</span><br />{info.focus_categories.join(", ")}</div>
          <div><span className="text-muted-foreground">Adapter</span><br /><code className="text-xs">{info.adapter_config}</code></div>
        </div>
      )}
      {data && (
        <div className="grid gap-4 lg:grid-cols-3">
          <div>
            <p className="mb-1 text-sm font-medium">1 · Raw state record (state format)</p>
            <Json value={data.raw_unit_record} />
            {data.raw_investment_record && (
              <>
                <p className="mb-1 mt-3 text-sm font-medium">Raw investment row</p>
                <Json value={data.raw_investment_record} />
              </>
            )}
          </div>
          <div>
            <p className="mb-1 text-sm font-medium">2 · Adapter mapping (config only)</p>
            <Json value={{ fields: data.field_mapping, indicators: data.indicator_mapping }} />
          </div>
          <div>
            <p className="mb-1 text-sm font-medium">3 · Canonical schema (shared by all states)</p>
            <Json value={{ unit: data.canonical_unit, indicators: data.canonical_indicators.slice(0, 3), investment: data.canonical_investment }} />
            <p className="mb-1 mt-3 text-sm font-medium">Canonical request (same shape in every state)</p>
            <Json value={data.canonical_request_example} />
          </div>
        </div>
      )}
    </div>
  );
}
