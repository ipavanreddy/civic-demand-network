FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY app ./app
# Sample data, adapters, prompts, schemas and fixtures are staged into _bundle/ by
# infrastructure/cloud-run/deploy-api.sh (they live at the repo root, outside this build context).
COPY _bundle/data /srv/data
COPY _bundle/ai /srv/ai
ENV PORT=8080 DATA_DIR=/srv/data AI_DIR=/srv/ai LOCAL_STATE_PATH=
CMD ["sh", "-c", "uv run --no-dev uvicorn app.main:app --host 0.0.0.0 --port $PORT"]
