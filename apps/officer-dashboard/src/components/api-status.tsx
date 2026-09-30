"use client";

import { useEffect, useState } from "react";
import { Badge } from "@/components/ui/badge";
import { apiGet } from "@/lib/api";

type Health = { status: string; project: string; model: string };

export function ApiStatus() {
  const [health, setHealth] = useState<Health | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    apiGet<Health>("/health").then(setHealth).catch(() => setError(true));
  }, []);

  if (error) return <Badge variant="destructive">API unreachable</Badge>;
  if (!health) return <Badge variant="outline">Checking API…</Badge>;
  return <Badge>API ok · {health.model}</Badge>;
}
