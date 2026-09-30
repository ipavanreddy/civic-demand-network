"use client";

import "leaflet/dist/leaflet.css";
import L from "leaflet";
import { useEffect, useRef } from "react";
import { bandColor, heatColor, type MapProps } from "@/lib/map-utils";

export default function LeafletMap({ hotspots, recommendations, center, zoom, selected, onSelect }: MapProps) {
  const el = useRef<HTMLDivElement>(null);
  const map = useRef<L.Map | null>(null);
  const layer = useRef<L.LayerGroup | null>(null);

  useEffect(() => {
    if (!el.current || map.current) return;
    map.current = L.map(el.current, { scrollWheelZoom: false }).setView(center, zoom);
    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 18,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    }).addTo(map.current);
    layer.current = L.layerGroup().addTo(map.current);
    return () => {
      map.current?.remove();
      map.current = null;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    map.current?.flyTo(center, zoom, { duration: 0.8 });
  }, [center, zoom]);

  useEffect(() => {
    const g = layer.current;
    if (!g) return;
    g.clearLayers();
    const max = Math.max(1, ...hotspots.map((h) => h.request_count));
    for (const h of hotspots) {
      L.polygon(h.boundary, { color: "#ea580c", weight: 1, fillColor: heatColor(h.request_count, max), fillOpacity: 1 })
        .bindTooltip(`${h.top_category_label}: ${h.request_count} requests · ${h.unique_citizens} citizens`)
        .addTo(g);
    }
    for (const r of recommendations) {
      if (r.lat == null || r.lng == null) continue;
      const isSel = r.recommendation_id === selected;
      L.circleMarker([r.lat, r.lng], {
        radius: 6 + Math.sqrt(r.request_count) * 1.2,
        color: isSel ? "#111827" : "#ffffff",
        weight: isSel ? 3 : 1.5,
        fillColor: bandColor(r.priority_score),
        fillOpacity: 0.85,
      })
        .bindTooltip(`#${r.rank} ${r.title} · score ${r.priority_score}`)
        .on("click", () => onSelect(r.recommendation_id))
        .addTo(g);
    }
  }, [hotspots, recommendations, selected, onSelect]);

  return <div ref={el} className="h-full min-h-[380px] w-full rounded-lg" />;
}
