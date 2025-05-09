FROM python:3.12.10-slim-bookworm

# use the latest version of uv from the official repository
COPY --from=ghcr.io/astral-sh/uv:0.7.3 /uv /uvx /bin/

# RUN apt-get update && apt-get install -y build-essential
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -r presidio && useradd --no-log-init -r -g presidio presidio

WORKDIR /app

COPY pyproject.toml uv.lock ./

# Geef schrijfrechten aan presidio user op /app en uv.lock
RUN chmod -R a+w /app

USER presidio

RUN uv sync --frozen --no-dev --no-cache

COPY src/api ./src/api

COPY api.py ./

EXPOSE 8080

CMD ["uv", "run", "--no-dev", "--no-cache", "api.py", "--host=0.0.0.0", "--workers=2", "--env=production", "--port=8080"]