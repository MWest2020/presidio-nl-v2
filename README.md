# Presidio-NL: Modulaire PII-detectie voor Nederlandse tekst

Presidio-NL is een modulaire API-service voor het detecteren en anonimiseren van privacygevoelige informatie (PII) in Nederlandse tekst. De service is gebaseerd op [Microsoft Presidio](https://github.com/microsoft/presidio) en biedt ondersteuning voor verschillende NLP-modellen (zoals spaCy of HuggingFace transformers) zonder dat de API of logica hoeft te worden aangepast.

## Waarom deze service?
- **Privacy by design:** Detecteer en anonimiseer persoonsgegevens (namen, telefoons, e-mails, IBAN, etc.) in Nederlandse tekst.
- **Modulair:** Wissel eenvoudig van NLP-engine (bijvoorbeeld spaCy of BERT) via configuratie.
- **Uitbreidbaar:** Voeg eenvoudig nieuwe herkenningspatronen of modellen toe.
- **API-gestuurd:** Eenvoudig te integreren in bestaande workflows via REST.

## Architectuur
- **FastAPI**: REST API met endpoints voor analyse (`/analyze`) en anonimisering (`/anonymize`).
- **Modulaire NLP-engine**: Kies tussen spaCy of transformers voor Named Entity Recognition (NER).
- **Pattern recognizers**: Custom herkenners voor Nederlandse IBAN, telefoonnummer en e-mail (uitbreidbaar).
- **Configuratie**: Bepaal via instellingen welk model en welke entiteiten gebruikt worden.

## Installatie & Gebruik

### 1. Lokaal draaien (voor ontwikkeling)
Installeer dependencies en start de API:
```bash
uv venv
uv sync
uv run api.py
```
De API is nu bereikbaar op [http://localhost:8080/docs](http://localhost:8080/docs) (Swagger UI).

### 2. Docker build & run

Bouw het image (bijvoorbeeld met naam `presidio-nl`):
```bash
docker build -t presidio-nl .
```

Start de container:
```bash
docker run -d -p 8000:8080 --name presidio-nl presidio-nl
```

### 3. Productie Deployment

Voor productie deployment kun je de Docker container gebruiken op je eigen infrastructuur.

## Voorbeeldgebruik

### Analyseer tekst op PII
```bash
# Lokaal (ontwikkeling)
curl -X POST "http://localhost:8080/analyze" -H "Content-Type: application/json" -d '{
  "text": "Mijn IBAN is NL91ABNA0417164300 en mijn telefoon is 06-12345678.",
  "entities": ["IBAN", "PHONE_NUMBER"],
  "language": "nl"
}'

# Productie (vervang your-domain.com met je eigen domein)
curl -X POST "https://your-domain.com/analyze" -H "Content-Type: application/json" -d '{
  "text": "Mijn IBAN is NL91ABNA0417164300 en mijn telefoon is 06-12345678.",
  "entities": ["IBAN", "PHONE_NUMBER"],
  "language": "nl"
}'
```
**Response:**
```json
{
  "text": "...",
  "entities_found": [
    {"entity_type": "IBAN", ...},
    {"entity_type": "PHONE_NUMBER", ...}
  ]
}
```

### Anonimiseer tekst
```bash
# Lokaal (ontwikkeling)
curl -X POST "http://localhost:8080/anonymize" -H "Content-Type: application/json" -d '{
  "text": "Mijn IBAN is NL91ABNA0417164300 en mijn telefoon is 06-12345678.",
  "entities": ["IBAN", "PHONE_NUMBER"],
  "language": "nl"
}'

# Productie (vervang your-domain.com met je eigen domein)
curl -X POST "https://your-domain.com/anonymize" -H "Content-Type: application/json" -d '{
  "text": "Mijn IBAN is NL91ABNA0417164300 en mijn telefoon is 06-12345678.",
  "entities": ["IBAN", "PHONE_NUMBER"],
  "language": "nl"
}'
```
**Response:**
```json
{
  "text": "...",
  "anonymized": "Mijn IBAN is <IBAN> en mijn telefoon is <PHONE_NUMBER>."
}
```

## Endpoints
- `POST /analyze` — Detecteert PII in tekst.
- `POST /anonymize` — Anonimiseert PII in tekst.
- `GET /entities` — Lijst van ondersteunde entiteitstypen.
- `GET /health` — Health check.

## Uitbreidbaarheid
- **Nieuw NLP-model?** Voeg toe in `src/api/nlp/` en pas de configuratie aan in `src/api/config.py`.
- **Nieuwe herkenner?** Voeg toe in `src/api/anonymizer/recognizers/patterns.py` en registreer in `engine.py`.
- **Entiteiten aanpassen?** Pas de lijst aan in de configuratie.

## Werkwijze samengevat
1. **Request** naar `/analyze` of `/anonymize` met tekst en gewenste entiteiten.
2. **ModularTextAnalyzer** voert NER en pattern matching uit (modulair).
3. **Resultaat**: lijst van gevonden entiteiten of geanonimiseerde tekst.

## Toekomst & bijdragen
- Ondersteuning voor meer entiteitstypen (zoals BSN, kenteken, etc.)
- Fine-tuning van modellen voor betere herkenning
- Integratie met andere privacy-tools

**Bijdragen of feedback?** Open een issue of pull request!
