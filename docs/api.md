# API-gebruik: Presidio-NL

De Presidio-NL API biedt endpoints voor het detecteren en anonimiseren van privacygevoelige informatie (PII) in Nederlandse tekst.

## Endpoints

### 1. POST /analyze
Detecteert PII in tekst.

**Request:**
```json
{
  "text": "Mijn IBAN is NL91ABNA0417164300 en mijn telefoon is 06-12345678.",
  "entities": ["IBAN", "PHONE_NUMBER"],
  "language": "nl"
}
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

### 2. POST /anonymize
Anonimiseert PII in tekst.

**Request:**
```json
{
  "text": "Mijn IBAN is NL91ABNA0417164300 en mijn telefoon is 06-12345678.",
  "entities": ["IBAN", "PHONE_NUMBER"],
  "language": "nl"
}
```
**Response:**
```json
{
  "text": "...",
  "anonymized": "Mijn IBAN is <IBAN> en mijn telefoon is <PHONE_NUMBER>."
}
```

### 3. GET /entities
Geeft een lijst van ondersteunde entiteitstypen.

### 4. GET /health
Health check endpoint.

---
Zie de Swagger UI op `/docs` voor interactieve documentatie. 