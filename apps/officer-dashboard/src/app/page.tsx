import { Badge } from "@/components/ui/badge";
import { ApiStatus } from "@/components/api-status";
import { Dashboard } from "@/components/dashboard";
import { DemoBadge } from "@/components/demo-badge";

export default function Home() {
  return (
    <main className="mx-auto flex w-full max-w-[1400px] flex-col gap-4 p-4 md:p-6">
      <header className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-col gap-1">
          <Badge variant="secondary" className="w-fit">Planning Officer</Badge>
          <h1 className="text-2xl font-semibold tracking-tight">JanVaani · Citizen Demand Intelligence</h1>
          <p className="text-sm text-muted-foreground">
            Multilingual citizen requests → demand clusters → fused data → transparent Priority Score → evidence brief → your decision.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <ApiStatus />
          <DemoBadge />
        </div>
      </header>
      <Dashboard />
    </main>
  );
}
