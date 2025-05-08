# Handleiding: Uitbreiden met nieuwe modellen of recognizers

## Nieuwe NLP-modellen toevoegen

1. **Maak een nieuwe engine-implementatie aan**
   - Voeg een Python-bestand toe in `app/nlp/` (bijv. `my_engine.py`).
   - Implementeer de interface uit `base.py`.

2. **Voeg een configuratiebestand toe**
   - Maak een YAML-bestand aan in `conf/` (bijv. `my_engine.yaml`).
   - Geef hierin aan welk model geladen moet worden en eventuele parameters.

3. **Pas de config-loader aan**
   - Zorg dat de applicatie de nieuwe engine kan laden op basis van de config.

4. **Test de werking**
   - Draai de API en CLI met het nieuwe model en controleer de output.

## Nieuwe recognizers toevoegen

1. **Maak een nieuwe recognizer-klasse**
   - Voeg een Python-bestand toe in `app/anonymizer/recognizers/`.
   - Implementeer een recognizer (bijv. subclass van `PatternRecognizer` of `EntityRecognizer`).

2. **Registreer de recognizer**
   - Voeg de nieuwe recognizer toe aan de registry in de analyzer-engine.
   - Dit kan via code of (optioneel) via een config.

3. **Test de werking**
   - Controleer of de nieuwe entiteit correct wordt herkend in de API/CLI.

---

Zie ook `docs/architectuur.md` voor de architectuur en `docs/migratieplan.md` voor de migratiestappen. 