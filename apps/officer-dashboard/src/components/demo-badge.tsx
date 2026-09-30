"use client";

import { useEffect, useState } from "react";
import { apiGet } from "@/lib/api";
import type { SystemStatus } from "@/lib/types";

/** Visible "Demo mode / sample data" badge with the per-integration real/demo breakdown. */
export function DemoBadge() {
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    apiGet<SystemStatus>("/api/system/status").then(setStatus).catch(() => setError(true));
  }, []);

  if (error) return <span className="rounded-full bg-red-100 px-2.5 py-1 text-xs font-medium text-red-800">API unreachable</span>;
  if (!status) return <span className="rounded-full border px-2.5 py-1 text-xs text-muted-foreground">Checking API…</span>;

  const all = Object.values(status.integrations);
  const live = status.live_count ?? all.filter((i) => i.mode === "real").length;
  const total = status.total_count ?? all.length;
  const failing = all.some((i) => i.mode === "fallback");
  const tone =
    live === 0 || failing
      ? "bg-amber-100 text-amber-900 ring-amber-300"
      : "bg-emerald-100 text-emerald-900 ring-emerald-300";

  return (
    <details className="relative">
      <summary
        className={`flex cursor-pointer list-none items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold ring-1 ${tone}`}
        title="Which integrations are live Google services and which run in demo mode"
      >
        <span className={`size-2 rounded-full ${live === 0 || failing ? "bg-amber-500" : "bg-emerald-500"}`} />
        {live === 0 ? "Demo mode" : `Live AI · ${live}/${total} integrations`} · sample data
      </summary>
      <div className="absolute right-0 z-[1000] mt-2 w-[22rem] rounded-lg border bg-popover p-3 text-xs shadow-lg">
        <p className="mb-2 font-medium">{status.data_notice}</p>
        <p className="mb-2 text-muted-foreground">
          Dataset {status.dataset_version} · {status.synthetic_requests.toLocaleString()} synthetic requests ·{" "}
          {status.live_requests} submitted in this demo
        </p>
        <ul className="space-y-1">
          {Object.entries(status.integrations).map(([name, i]) => (
            <li key={name} className="flex items-start justify-between gap-2">
              <span className="font-medium">{name.replaceAll("_", " ")}</span>
              <span className="text-right">
                <span
                  className={
                    i.mode === "real" ? "text-emerald-700" : i.mode === "fallback" ? "text-red-700" : "text-amber-700"
                  }
                >
                  {i.mode === "real" ? "live" : i.mode}
                </span>
                <span className="block text-muted-foreground">{i.mode === "demo" ? `${i.detail} · set ${i.env}` : i.detail}</span>
              </span>
            </li>
          ))}
        </ul>
      </div>
    </details>
  );
}
