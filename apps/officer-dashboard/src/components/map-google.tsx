"use client";

import { useEffect, useRef, useState } from "react";
import { bandColor, heatColor, type MapProps } from "@/lib/map-utils";

/* Minimal typings for the parts of the Maps JavaScript API used here. */
type LatLng = { lat: number; lng: number };
type Overlay = { setMap(m: unknown): void; addListener?(ev: string, fn: () => void): void };
type GoogleMapsNS = {
  maps: {
    Map: new (el: HTMLElement, opts: object) => { panTo(c: LatLng): void; setZoom(z: number): void };
    Polygon: new (opts: object) => Overlay;
    Circle: new (opts: object) => Overlay;
  };
};

declare global {
  interface Window {
    google?: GoogleMapsNS;
  }
}

let loader: Promise<GoogleMapsNS> | null = null;
function loadGoogleMaps(key: string): Promise<GoogleMapsNS> {
  if (window.google?.maps) return Promise.resolve(window.google);
  loader ??= new Promise((resolve, reject) => {
    const s = document.createElement("script");
    s.src = `https://maps.googleapis.com/maps/api/js?key=${encodeURIComponent(key)}&v=weekly`;
    s.async = true;
    s.onload = () => (window.google ? resolve(window.google) : reject(new Error("Maps failed to load")));
    s.onerror = () => reject(new Error("Maps failed to load"));
    document.head.appendChild(s);
  });
  return loader;
}

export default function GoogleHotspotMap({ hotspots, recommendations, center, zoom, selected, onSelect }: MapProps) {
  const el = useRef<HTMLDivElement>(null);
  const map = useRef<{ panTo(c: LatLng): void; setZoom(z: number): void } | null>(null);
  const overlays = useRef<Overlay[]>([]);
  const [g, setG] = useState<GoogleMapsNS | null>(null);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    loadGoogleMaps(process.env.NEXT_PUBLIC_MAPS_API_KEY ?? "")
      .then((google) => {
        if (el.current && !map.current) {
          map.current = new google.maps.Map(el.current, { center: { lat: center[0], lng: center[1] }, zoom, mapTypeControl: false });
        }
        setG(google);
      })
      .catch(() => setFailed(true));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    map.current?.panTo({ lat: center[0], lng: center[1] });
    map.current?.setZoom(zoom);
  }, [center, zoom, g]);

  useEffect(() => {
    if (!g || !map.current) return;
    overlays.current.forEach((o) => o.setMap(null));
    overlays.current = [];
    const max = Math.max(1, ...hotspots.map((h) => h.request_count));
    for (const h of hotspots) {
      overlays.current.push(
        new g.maps.Polygon({
          map: map.current,
          paths: h.boundary.map(([lat, lng]) => ({ lat, lng })),
          strokeColor: "#ea580c",
          strokeWeight: 1,
          fillColor: heatColor(h.request_count, max),
          fillOpacity: 1,
        }),
      );
    }
    for (const r of recommendations) {
      if (r.lat == null || r.lng == null) continue;
      const c = new g.maps.Circle({
        map: map.current,
        center: { lat: r.lat, lng: r.lng },
        radius: 800 + Math.sqrt(r.request_count) * 250,
        strokeColor: r.recommendation_id === selected ? "#111827" : "#ffffff",
        strokeWeight: r.recommendation_id === selected ? 3 : 1,
        fillColor: bandColor(r.priority_score),
        fillOpacity: 0.8,
        clickable: true,
      });
      c.addListener?.("click", () => onSelect(r.recommendation_id));
      overlays.current.push(c);
    }
  }, [g, hotspots, recommendations, selected, onSelect]);

  if (failed) return <div className="p-4 text-sm text-red-700">Google Maps failed to load. Check NEXT_PUBLIC_MAPS_API_KEY.</div>;
  return <div ref={el} className="h-full min-h-[380px] w-full rounded-lg" />;
}
