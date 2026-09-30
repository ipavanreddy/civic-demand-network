import { Badge } from "@/components/ui/badge";
import { ApiStatus } from "@/components/api-status";
import { CitizenApp } from "@/components/citizen-app";
import { DemoBadge } from "@/components/demo-badge";

export default function Home() {
  return (
    <main className="mx-auto flex w-full max-w-3xl flex-col gap-5 p-4 md:p-6">
      <header className="flex flex-wrap items-start justify-between gap-3">
        <div className="flex flex-col gap-1">
          <Badge variant="secondary" className="w-fit">Citizen</Badge>
          <h1 className="text-3xl font-semibold tracking-tight">JanVaani · जनवाणी · జనవాణి</h1>
          <p className="text-muted-foreground">Your voice for local development</p>
        </div>
        <div className="flex items-center gap-2">
          <ApiStatus />
          <DemoBadge />
        </div>
      </header>
      <CitizenApp />
    </main>
  );
}
