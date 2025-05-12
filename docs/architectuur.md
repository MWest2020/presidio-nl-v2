# Architectuur: Presidio-NL API (Gebruikersuitleg)

De Presidio-NL API is een modulaire service voor het detecteren en anonimiseren van privacygevoelige informatie (PII) in Nederlandse tekst. De architectuur is ontworpen voor flexibiliteit en uitbreidbaarheid.

## Overzicht
- **FastAPI**: REST API voor analyse en anonimisering van tekst.
- **Modulaire NLP-engine**: Ondersteunt verschillende modellen (zoals spaCy of transformers) via een abstractielaag. Modelkeuze is configureerbaar.
- **Pattern recognizers**: Custom herkenners voor Nederlandse PII (zoals IBAN, telefoon, e-mail).
- **Docker**: Alles draait in een container voor eenvoudige installatie en deployment.

## Request flow
1. **Client stuurt POST-request** naar `/analyze` of `/anonymize` met tekst.
2. **API** roept de modulaire analyzer aan:
   - Voert NER uit met het gekozen NLP-model.
   - Past pattern recognizers toe voor vaste patronen (zoals IBAN).
   - Combineert en dedupliceert resultaten.
3. **Response**: JSON met gevonden entiteiten of geanonimiseerde tekst.

## Waarom modulair?
- Je kunt eenvoudig wisselen van NLP-model (bijvoorbeeld voor betere herkenning of performance).
- Nieuwe herkenners of modellen zijn makkelijk toe te voegen zonder de API of logica te wijzigen.

---
Zie de README voor gebruiksinstructies en voorbeelden. 