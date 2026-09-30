"use client";

import dynamic from "next/dynamic";
import { useState } from "react";
import type { MapProps } from "@/lib/map-utils";


const GoogleMap = dynamic(() => import("./map-google"), { ssr: false, loading: () => <MapSkeleton /> });
const LeafletMap = dynamic(() => import("./map-leaflet"), { ssr: false, loading: () => <MapSkeleton /> });

function MapSkeleton() {
  return <div className="h-full min-h-[380px] animate-pulse rounded-lg bg-muted" />;
}

/** Google Maps when NEXT_PUBLIC_MAPS_API_KEY is set (and accepted), otherwise Leaflet + OpenStreetMap tiles (labelled). */
export function HotspotMap(props: MapProps) {
  const [googleFailed, setGoogleFailed] = useState(false);
  const google = Boolean(process.env.NEXT_PUBLIC_MAPS_API_KEY) && !googleFailed;
  return (
    <div className="relative h-full min-h-[380px]">
      {google ? <GoogleMap {...props} onFail={() => setGoogleFailed(true)} /> : <LeafletMap {...props} />}
      <div className="pointer-events-none absolute bottom-2 left-2 z-[500] rounded bg-background/90 px-2 py-1 text-[11px] shadow">
        {google
          ? "Google Maps"
          : googleFailed
            ? "Google Maps key rejected for this domain; fallback map: Leaflet + OpenStreetMap"
            : "Demo map: Leaflet + OpenStreetMap (set NEXT_PUBLIC_MAPS_API_KEY for Google Maps)"} · H3 res-7
        hexagons = request hotspots · circles = demand clusters (size = requests, colour = priority)
      </div>
    </div>
  );
}
