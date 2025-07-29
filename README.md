# OpenAnonymizer: Modulaire PII-detectie voor Nederlandse tekst

Presidio-NL is een modulaire API-service voor het detecteren en anonimiseren van privacygevoelige informatie (PII) in Nederlandse tekst. De service is gebaseerd op [Microsoft Presidio](https://github.com/microsoft/presidio) en biedt ondersteuning voor verschillende NLP-modellen (zoals spaCy of HuggingFace transformers) zonder dat de API of logica hoeft te worden aangepast.

## Installatie & Gebruik

### 1. Lokaal draaien (voor ontwikkeling)

Installeer dependencies en start de API:

```bash
uv venv
uv sync
uv run api.py
```

De API is nu bereikbaar op [http://localhost:8080/api/v1/docs](http://localhost:8080/api/v1/docs) (Swagger UI).

### 2. Docker Compose (aanbevolen)

Start beide services (API + UI) met docker-compose:

```bash
docker-compose up -d
```

Na opstarten zijn de services bereikbaar op:
- **API**: [http://localhost:8001/api/v1/docs](http://localhost:8001/api/v1/docs) (Swagger UI)
- **UI**: [http://localhost:8002](http://localhost:8002) (Web interface)

### 3. Individuele Docker containers

Bouw het backend image:

```bash
docker build -t openanonymizer .
```

Start alleen de backend container:

```bash
docker run -d -p 8001:8080 --name openanonymiser openanonymizer
```

API bereikbaar op [http://localhost:8001/api/v1/docs](http://localhost:8001/api/v1/docs)
