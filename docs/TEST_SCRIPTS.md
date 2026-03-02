# OpenAnonymiser Testscripts voor String Endpoints

Twee standalone testscripts om de nieuwe string-endpoints `/analyze` en `/anonymize` te testen.

## 🚀 Snel starten

### Optie 1: Python-script (aanbevolen)
```bash
# Start eerst de API
uv run api.py

# Draai tests (in een andere terminal)
python tests/integration/test_endpoints.py
```

### Optie 2: Bash-script
```bash
# Start eerst de API
uv run api.py

# Draai tests (in een andere terminal)
./scripts/test_endpoints.sh
```

### Optie 3: Testen tegen een remote server
```bash
# Test tegen specifieke URL
python tests/integration/test_endpoints.py https://api.openanonymiser.commonground.nu
./scripts/test_endpoints.sh https://api.openanonymiser.commonground.nu
```

## 📋 Wat wordt getest

### ✅ Health check
- `GET /api/v1/health` → `{"ping": "pong"}`

### ✅ Analyze endpoint (`POST /api/v1/analyze`)
- **Basis tekstanalyse** - Nederlandse PII-detectie
- **Entity-filtering** - Alleen opgegeven types detecteren  
- **Engine-keuze** - SpaCy vs Transformers
- **Inputvalidatie** - Lege tekst, niet-ondersteunde talen

### ✅ Anonymize endpoint (`POST /api/v1/anonymize`)
- **Basis-anonimisering** - PII vervangen door placeholders
- **Strategiekeuze** - Verschillende anonimiseerstrategieën
- **Entity-filtering** - Alleen specifieke types anonimiseren
- **Inputvalidatie** - Ongeldige strategieën

### ✅ Foutafhandeling
- Ongeldige JSON-requests
- Vereiste velden ontbreken
- HTTP-foutcodes (422, 500)

### ✅ Document upload (bonus)
- PDF-upload test (als `test.pdf` aanwezig is)

## 📊 Voorbeeld output

```
🚀 OpenAnonymiser String Endpoints Test Suite
Testen tegen: http://localhost:8080

🔍 Health check
✅ PASS - Health endpoint werkt

🔍 /analyze endpoint  
✅ PASS - Analyse basis-tekst
✅ PASS - Analyse met entity-filtering
✅ PASS - Analyse met engine-keuze
✅ PASS - Validatie lege tekst
✅ PASS - Validatie niet-ondersteunde taal

🔍 /anonymize endpoint
✅ PASS - Anonimiseer basis-tekst
✅ PASS - Anonimiseer met strategie
✅ PASS - Anonimiseer met entity-filtering
✅ PASS - Ongeldige strategie

📊 Samenvatting testresultaten
=================================
Totaal tests: 12
Geslaagd: 12
Gefaalde: 0

🎉 Alle tests geslaagd!
```

## 🔧 Benodigdheden

### Python-script
- Python 3.6+
- `requests` library: `pip install requests`

### Bash-script  
- Bash-shell
- `curl` command
- `jq` (optioneel, voor prettige JSON-weergave)

## 💡 Gebruikstips

### Development workflow
```bash
# 1. Start API in development modus
uv run api.py &

# 2. Draai tests na wijzigingen
python tests/integration/test_endpoints.py

# 3. Stop de API
kill %1
```

### Docker-test
```bash
# 1. Build en run de container
docker build -t openanonymiser:test .
docker run -d -p 8081:8080 openanonymiser:test

# 2. Test container
python tests/integration/test_endpoints.py http://localhost:8081

# 3. Opruimen
docker stop $(docker ps -q --filter ancestor=openanonymiser:test)
```

### CI/CD-integratie
```bash
#!/bin/bash
# Voeg toe aan je CI-pipeline

# Start API op de achtergrond
uv run api.py --env production &
API_PID=$!

# Wacht op startup
sleep 10

# Draai tests
python tests/integration/test_endpoints.py

# Bewaar exit code
TEST_EXIT_CODE=$?

# Opruimen
kill $API_PID

# Exit met testresultaat
exit $TEST_EXIT_CODE
```

## 🆚 Script-vergelijking

| Eigenschap | Python-script | Bash-script |
|---------|---------------|-------------|
| **Cross-platform** | ✅ Windows/Mac/Linux | ❌ Alleen Unix |
| **JSON-afhandeling** | ✅ Native | ⚠️ String parsing |
| **Foutdetails** | ✅ Rijke output | ✅ Basis output |
| **Dependencies** | `requests` | `curl` |
| **Snelheid** | ⚡ Snel | ⚡ Snel |
| **Leesbaarheid** | ✅ Gestructureerd | ✅ Simpel |

## 🚀 Exit-codes

- `0` - Alle tests geslaagd
- `1` - Sommige tests gefaald  
- `1` - API niet beschikbaar

Perfect voor CI/CD-pipelines en geautomatiseerde tests!