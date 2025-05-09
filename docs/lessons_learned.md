# Lessons Learned uit de PoC

## Wat werkte goed
- Custom recognizers voor Nederlandse PII (zoals BSN, IBAN) waren eenvoudig toe te voegen.
- Containerisatie (Docker) maakte deployment en testen makkelijk.

## Wat kon beter
- Modelkeuze was niet modulair: SpaCy was hardcoded, waardoor uitbreiden lastig was.
- Toevoegen van nieuwe modellen (zoals transformers) vereiste veel codewijzigingen.
- Configuratie van recognizers en modellen was verspreid over de code.

## Belangrijkste verbeterpunten voor de nieuwe opzet
- Maak de NLP-engine verwisselbaar via een abstractielaag en configuratie.
- Centraliseer configuratie van modellen en recognizers.
- Documenteer keuzes en uitbreidingsmogelijkheden expliciet.

---

Deze inzichten zijn verwerkt in het migratieplan en de nieuwe architectuur. 