FROM python:3.12.11-slim-bookworm

# use the latest version of uv from the official repository
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN groupadd -r presidio && useradd --no-log-init -r -g presidio presidio

WORKDIR /app

# Create necessary directories and set permissions
RUN mkdir -p /home/presidio/.cache/uv && \
    chown -R presidio:presidio /home/presidio/.cache && \
    chown -R presidio:presidio /app

COPY --chown=presidio:presidio pyproject.toml uv.lock ./

USER presidio

RUN uv sync --frozen --no-dev --no-cache

COPY --chown=presidio:presidio src/api ./src/api

COPY --chown=presidio:presidio api.py ./

COPY --chown=presidio:presidio scripts/healthcheck.py ./scripts/

EXPOSE 8080

# Add Docker healthcheck
HEALTHCHECK \
    --interval=60s \
    --timeout=5s \
    --start-period=25s \
    --retries=5 \
  CMD ["python", "scripts/healthcheck.py", "--port", "8080"]

CMD ["uv", "run", "--no-dev", "--no-cache", "api.py", "--host=0.0.0.0", "--workers=2", "--env=production", "--port=8080"]