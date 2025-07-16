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

De API is nu bereikbaar op [http://localhost:8080/docs](http://localhost:8080/api/v1docs) (Swagger UI).

### 2. Docker build & run

Bouw het image (bijvoorbeeld met naam `presidio-nl`):

```bash
docker build -t openanonymizer .
```

Start de container:

```bash
docker run -d -p 8000:8080 --name presidio-nl presidio-nl
```
