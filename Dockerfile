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

# Disable UV cache for runtime (read-only filesystem in K8s)
ENV UV_NO_CACHE=1

# resolve from uv.lock only, no dev dependencies
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

CMD ["uv", "run", "api.py", "--host", "0.0.0.0", "--workers", "2", "--env", "production", "--port", "8080"]