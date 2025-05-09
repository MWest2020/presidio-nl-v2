FROM python:3.12-slim

# Systeem dependencies voor spaCy en presidio
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Kopieer alleen dependency files eerst voor betere caching
COPY pyproject.toml uv.lock ./

# Installeer uv
RUN pip install uv

# Installeer alle dependencies exact zoals gelocked
RUN uv pip install --system --no-deps .

# Kopieer de rest van de code
COPY . .

# Download spaCy model (indien nodig)
RUN python -m spacy download nl_core_news_md

EXPOSE 6666

CMD ["uvicorn", "app.api.app:app", "--host", "0.0.0.0", "--port", "6666"] 