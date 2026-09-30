import type { Hotspot, RecommendationRow } from "@/lib/types";

export type MapProps = {
  hotspots: Hotspot[];
  recommendations: RecommendationRow[];
  center: [number, number];
  zoom: number;
  selected: string | null;
  onSelect: (recommendationId: string) => void;
};

export function bandColor(score: number): string {
  if (score >= 70) return "#dc2626";
  if (score >= 45) return "#d97706";
  return "#64748b";
}

export function heatColor(count: number, max: number): string {
  const t = Math.min(1, count / Math.max(1, max));
  const alpha = 0.15 + 0.55 * t;
  return `rgba(234, 88, 12, ${alpha.toFixed(2)})`;
}
