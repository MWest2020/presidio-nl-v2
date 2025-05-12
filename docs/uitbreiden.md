# Uitbreiden: Nieuwe modellen of recognizers toevoegen

Wil je de Presidio-NL API uitbreiden met een nieuw NLP-model of een extra herkenner? Dat kan eenvoudig dankzij de modulaire opzet.

## Nieuw NLP-model toevoegen
1. **Implementeer een nieuwe engine**
   - Voeg een Python-klasse toe in `src/api/nlp/` (zie `spacy_engine.py` of `transformers_engine.py` als voorbeeld).
   - Zorg dat deze de interface uit [`src/api/nlp/base.py`](../src/api/nlp/base.py) (`NLPEngine`) implementeert.
2. **Pas de configuratie aan**
   - Voeg het model toe aan de settings in `src/api/config.py` of via een config-bestand.
3. **Gebruik**
   - De API gebruikt automatisch het gekozen model bij het opstarten.

## Nieuwe recognizer toevoegen
1. **Maak een nieuwe recognizer-klasse**
   - Voeg een Python-klasse toe in `src/api/anonymizer/recognizers/` (zie `patterns.py` als voorbeeld).
   - Implementeer een subclass van `PatternRecognizer`.
2. **Registreer de recognizer**
   - Voeg de nieuwe recognizer toe aan de registry in `src/api/anonymizer/engine.py`.

---
Zie de codevoorbeelden in de genoemde modules voor een snelle start. 