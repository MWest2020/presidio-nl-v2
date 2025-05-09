# Migratieplan: presidio-nl Proof of Concept → Modulaire, Model-agnostische Opzet

## Doel

## Stappen

1. **Inventarisatie & Analyse**
   - Lessons learned uit de PoC noteren.
   - Afhankelijkheden in kaart brengen (SpaCy, Presidio, custom recognizers, transformers).

2. **Nieuwe Structuur Opzetten**
   - Nieuwe mappenstructuur aanmaken:
     - `app/` (hoofdcode)
     - `app/api/` (FastAPI endpoints)
     - `app/anonymizer/` (anonimisatie-logica)
     - `app/nlp/` (abstractie en implementaties voor NLP-engines)
     - `conf/` (modelconfiguraties)
     - `docs/` (documentatie)
     - `tests/` (unittests)

3. **Abstractielaag voor NLP-Engines**
   - Interface `NlpEngine` in `app/nlp/base.py`.
   - Implementaties voor SpaCy (`spacy_engine.py`) en transformers (`transformers_engine.py`).
   - Configuratie bepaalt welke engine geladen wordt.

4. **Migratie van Kernfunctionaliteit**
   - Custom recognizers migreren naar `app/anonymizer/recognizers/`.
   - Werking met SpaCy als default garanderen.

5. **Configuratie & Docker**
   - YAML-configs voor verschillende modellen in `conf/`.
   - Dockerfile aanpassen voor modulaire build/run.

6. **Documentatie**
   - Migratieplan, architectuur, uitbreidingshandleiding en lessons learned in `docs/`.

7. **Testen & Validatie**
   - Unittests voor engine-interface.
   - Docker-containers testen.

## Keuzes
- **Herbruikbaarheid:** Bestaande recognizers en functionaliteit worden zoveel mogelijk hergebruikt.
- **Configuratie:** Modelkeuze via YAML of env var, niet hardcoded.
- **Uitbreidbaarheid:** Nieuwe modellen/recognizers kunnen eenvoudig worden toegevoegd.

---

Dit document wordt aangevuld tijdens de migratie. Zie ook `docs/architectuur.md` en `docs/uitbreiden.md` voor verdere details. 