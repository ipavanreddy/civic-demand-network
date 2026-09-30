# Vercel: citizen app and officer dashboard

Each frontend is its **own Vercel project**, deployed from its own directory. The apps have no
workspace dependencies: each directory has its own `package.json`, `pnpm-lock.yaml` and
`pnpm-workspace.yaml` (build-script allow-list only), so `pnpm install && pnpm build` works from
`apps/<app>` alone. No Docker and no `output: "standalone"`: Vercel runs `next build` natively.

The API runs on Cloud Run: `https://civic-demand-network-api-847963771142.asia-south1.run.app`
(deployed with `infrastructure/cloud-run/deploy.sh api`).

## Project settings

| Setting | Citizen app | Officer dashboard |
|---|---|---|
| Project name (suggested) | `janvaani-citizen` | `janvaani-officer` |
| Framework preset | Next.js | Next.js |
| Root Directory | `apps/citizen-web` | `apps/officer-dashboard` |
| Install Command | `pnpm install` | `pnpm install` |
| Build Command | `pnpm build` (default `next build`) | `pnpm build` |
| Output Directory | default (`.next`) | default (`.next`) |
| Node.js version | 22.x (Next.js 16 needs >= 20.9) | 22.x |
| Include files outside the Root Directory | not needed (off is fine) | not needed |

## Environment variables (Production and Preview; never committed)

| Variable | Citizen app | Officer dashboard | Value |
|---|---|---|---|
| `NEXT_PUBLIC_API_URL` | required | required | `https://civic-demand-network-api-847963771142.asia-south1.run.app` |
| `NEXT_PUBLIC_MAPS_API_KEY` | not used | optional | Browser Maps JavaScript API key (HTTP-referrer restricted) |

`NEXT_PUBLIC_*` values are inlined into the JS bundle at build time: **redeploy after changing them**.
Without `NEXT_PUBLIC_MAPS_API_KEY`, or if Google rejects the key for the current domain, the
dashboard falls back to Leaflet + OpenStreetMap tiles and says so on the map.

## After the first deploy

1. **CORS on the API.** Redeploy the API with the two production URLs, and optionally a regex for
   preview deployments:

   ```bash
   CORS_ORIGINS="https://janvaani-citizen.vercel.app,https://janvaani-officer.vercel.app" \
   CORS_ORIGIN_REGEX='https://janvaani-.*\.vercel\.app' \
     infrastructure/cloud-run/deploy.sh api
   ```

2. **Maps key referrers.** The browser key must allow the Vercel domains, e.g.
   `https://*.vercel.app/*` (or the two exact URLs) and, for local dev, `http://localhost:3011/*`.
   Local testing on 2026-09-30 returned `RefererNotAllowedMapError` for `http://localhost:3011/`,
   so the current restriction does not match the dev port either.

3. **Smoke test.** Open both URLs: the header badge should read
   *Live AI · 8/9 integrations · sample data* (Telegram is the only demo integration). Click it to
   see each integration's mode. "API unreachable" means `NEXT_PUBLIC_API_URL` or CORS is wrong.

## CLI equivalent

```bash
cd apps/citizen-web
vercel link --project janvaani-citizen
vercel env add NEXT_PUBLIC_API_URL production   # paste the Cloud Run URL
vercel deploy --prod
```

Repeat in `apps/officer-dashboard` with `--project janvaani-officer` and, optionally,
`NEXT_PUBLIC_MAPS_API_KEY`.
