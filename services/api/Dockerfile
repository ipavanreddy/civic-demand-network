# JanVaani API image. Build from the REPO ROOT so the runtime files in ai/ (prompts, schemas,
# taxonomy, evaluation fixtures) and data/ (adapters, canonical schemas, sample data) are included:
#
#   docker build -f services/api/Dockerfile -t civic-demand-network-api .
#
# The image mirrors the repo layout (/srv = repo root), so app/config.py resolves ai/ and data/
# exactly as in local dev. No secrets or .env files are copied (see /.dockerignore).
FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.11 /uv /usr/local/bin/uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy PYTHONUNBUFFERED=1

WORKDIR /srv/services/api
COPY services/api/pyproject.toml services/api/uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY services/api/app ./app
COPY ai /srv/ai
COPY data /srv/data

# Unprivileged runtime user; .data/ is the local fallback for media if Cloud Storage is unavailable.
RUN useradd --system --uid 10001 app && mkdir -p .data && chown app .data
USER app

# LOCAL_STATE_PATH empty: runtime state is in memory only (sample data reloads on every start).
ENV PORT=8080 LOCAL_STATE_PATH= PATH=/srv/services/api/.venv/bin:$PATH
EXPOSE 8080
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --proxy-headers --forwarded-allow-ips='*'"]
