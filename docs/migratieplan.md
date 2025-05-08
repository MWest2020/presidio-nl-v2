# Migratieplan: presidio-nl Proof of Concept → Modulaire, Model-agnostische Opzet

## Doel
De bestaande werking (API en CLI voor anonimisering) behouden, maar de architectuur zo aanpassen dat het onderliggende taalmodel eenvoudig verwisselbaar is (SpaCy als default, uitbreidbaar naar andere modellen zoals transformers).

## Stappen

1. **Inventarisatie & Analyse**
   - Overzicht maken van bestaande modules (API, CLI, recognizers, model-loading, Docker, tests).
   - Lessons learned uit de PoC noteren.
   - Afhankelijkheden in kaart brengen (SpaCy, Presidio, custom recognizers, transformers).

2. **Nieuwe Structuur Opzetten**
   - Nieuwe mappenstructuur aanmaken:
     - `app/` (hoofdcode)
     - `app/api/` (FastAPI endpoints)
     - `app/cli/` (CLI entrypoint)
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
   - API en CLI refactoren zodat ze de nieuwe engine-interface gebruiken.
   - Custom recognizers migreren naar `app/anonymizer/recognizers/`.
   - Werking met SpaCy als default garanderen.

5. **Configuratie & Docker**
   - YAML-configs voor verschillende modellen in `conf/`.
   - Dockerfile aanpassen voor modulaire build/run.

6. **Documentatie**
   - Migratieplan, architectuur, uitbreidingshandleiding en lessons learned in `docs/`.

7. **Testen & Validatie**
   - Unittests voor engine-interface.
   - Functionele tests voor API/CLI.
   - Docker-containers testen.

## Keuzes
- **Modulariteit:** Abstractielaag voor NLP-engine zodat modelkeuze losstaat van API/CLI.
- **Herbruikbaarheid:** Bestaande recognizers en functionaliteit worden zoveel mogelijk hergebruikt.
- **Configuratie:** Modelkeuze via YAML of env var, niet hardcoded.
- **Uitbreidbaarheid:** Nieuwe modellen/recognizers kunnen eenvoudig worden toegevoegd.

---

Dit document wordt aangevuld tijdens de migratie. Zie ook `docs/architectuur.md` en `docs/uitbreiden.md` voor verdere details. 